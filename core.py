"""
AURA AI - Core Logic Module
Automated User Reception & Assistance with Scam Detection
Handles rules, AI extraction, offline heuristics fallback, contact rules, and database operations.
"""

import os
import re
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Configuration defaults
DEFAULT_MODEL = os.getenv("AURA_MODEL", "claude-sonnet-5-5")
DEFAULT_DB_PATH = os.getenv("AURA_DB", "aura.db")

# Availability options
AVAILABILITY_OPTIONS = ["Available", "Busy", "Do Not Disturb"]
DEFAULT_AVAILABILITY = "Busy"

# Contact categories
CONTACT_CATEGORIES = ["trusted", "known", "unknown", "blocked"]

# Scam Detection Signals & Regex Rules
# Format: (signal_name, points, regex_pattern)
SECURITY_RULES: List[Tuple[str, int, re.Pattern]] = [
    (
        "Credential request",
        3,
        re.compile(
            r"\b(?:otp|pin|cvv|passwords?|card\s*numbers?|aadhaar(?:\s*card|\s*number)?|verification\s*codes?)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "Urgency",
        2,
        re.compile(
            r"\b(?:immediately|right\s*now|urgently?|in\s+(?:ten|\d+)\s+minutes?|within\s+(?:thirty|\d+)\s+minutes?|last\s*chance|expires?\s*today|hurry(?:\s*up)?)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "Threat",
        2,
        re.compile(
            r"\b(?:account\s*will\s*be\s*(?:blocked|suspended|frozen)|legal\s*actions?|arrest(?:ed)?|penalt(?:y|ies)|sim\s*will\s*be\s*(?:blocked|suspended|deactivated)|case\s*filed)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "Suspicious link",
        2,
        re.compile(
            r"(?:https?://\S+|www\.\S+|bit\.ly/\S+|tinyurl\.com/\S+|cutt\.ly/\S+|\b[a-zA-Z0-9.-]+\.(?:xyz|top|click|info)(?:/\S*)?)",
            re.IGNORECASE,
        ),
    ),
    (
        "Reward claim",
        2,
        re.compile(
            r"\b(?:you(?:\s*have|\s*'ve)?\s*won|lotter(?:y|ies)|prizes?|cashbacks?|gift\s*cards?|congratulations?|lucky\s*draw)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "Money request",
        3,
        re.compile(
            r"\b(?:send|transfer|pay|deposit)\b.*?\b(?:money|rs\.?|inr|amounts?|fees?)\b|\b(?:processing|registration)\s*fees?\b",
            re.IGNORECASE,
        ),
    ),
]


def get_db_path() -> str:
    """Return the database path, overridable by AURA_DB environment variable."""
    return os.getenv("AURA_DB", DEFAULT_DB_PATH)


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Create and return a SQLite connection."""
    target_path = db_path or get_db_path()
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize SQLite database tables and default settings."""
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    time TEXT NOT NULL,
                    caller_id TEXT,
                    caller TEXT,
                    purpose TEXT,
                    message TEXT,
                    priority TEXT,
                    score INTEGER,
                    risk TEXT,
                    signals TEXT,
                    explanation TEXT,
                    category TEXT,
                    action TEXT,
                    transcript TEXT,
                    engine TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE COLLATE NOCASE,
                    category TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    k TEXT PRIMARY KEY,
                    v TEXT NOT NULL
                )
                """
            )
            # Default availability status
            conn.execute(
                """
                INSERT OR IGNORE INTO settings (k, v) VALUES (?, ?)
                """,
                ("status", DEFAULT_AVAILABILITY),
            )
    finally:
        conn.close()


def get_setting(key: str, default: Optional[str] = None, db_path: Optional[str] = None) -> Optional[str]:
    """Retrieve a setting by key."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT v FROM settings WHERE k = ?", (key,))
        row = cur.fetchone()
        return row["v"] if row else default
    finally:
        conn.close()


def set_setting(key: str, value: str, db_path: Optional[str] = None) -> None:
    """Save or update a setting by key."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO settings (k, v) VALUES (?, ?)
                ON CONFLICT(k) DO UPDATE SET v = excluded.v
                """,
                (key, value),
            )
    finally:
        conn.close()


def get_contact_category(name: Optional[str], db_path: Optional[str] = None) -> str:
    """Look up contact category by name (case-insensitive). Not found = unknown."""
    if not name or not name.strip():
        return "unknown"
    init_db(db_path)
    conn = get_db_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT category FROM contacts WHERE LOWER(name) = LOWER(?) LIMIT 1",
            (name.strip(),),
        )
        row = cur.fetchone()
        if row and row["category"]:
            cat = row["category"].strip().lower()
            return cat if cat in CONTACT_CATEGORIES else "unknown"
        return "unknown"
    finally:
        conn.close()


def upsert_contact(name: str, category: str, db_path: Optional[str] = None) -> None:
    """Insert or update a contact with category (trusted, known, unknown, blocked)."""
    clean_name = name.strip()
    clean_cat = category.strip().lower()
    if not clean_name:
        raise ValueError("Contact name cannot be empty.")
    if clean_cat not in CONTACT_CATEGORIES:
        clean_cat = "unknown"

    init_db(db_path)
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO contacts (name, category)
                VALUES (?, ?)
                ON CONFLICT(name) DO UPDATE SET category = excluded.category
                """,
                (clean_name, clean_cat),
            )
    finally:
        conn.close()


def list_contacts(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all contacts ordered by name."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, category FROM contacts ORDER BY name ASC")
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def delete_contact(contact_id: int, db_path: Optional[str] = None) -> None:
    """Delete a contact by ID."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    finally:
        conn.close()


def is_api_available() -> bool:
    """Check if Anthropic API key is configured."""
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    return bool(key)


def offline_fallback_extractor(transcript: str, availability: str = "Busy") -> Dict[str, Any]:
    """
    Offline regex/heuristic extraction engine when API key is not set or API call fails.
    Extracts caller, purpose, summary message, and initial priority.
    """
    text = transcript.strip()

    # 1. Caller extraction
    caller = "Unknown"
    caller_match = re.search(
        r"(?:(?:this\s+is|my\s+name\s+is|i\s+am|i'm)\s+([A-Za-z0-9\s&'-]+?)(?:[.,\n]|(?:\s+calling\b)|\s*$))",
        text,
        re.IGNORECASE,
    )
    if caller_match:
        extracted = caller_match.group(1).strip()
        if extracted and len(extracted) < 50:
            caller = extracted
    else:
        calling_from_match = re.search(
            r"(?:calling\s+from\s+([A-Za-z0-9\s&'-]+?)(?:[.,\n]|\s*$))",
            text,
            re.IGNORECASE,
        )
        if calling_from_match:
            extracted = calling_from_match.group(1).strip()
            if extracted and len(extracted) < 50:
                caller = extracted

    # Clean caller if it contains typical filler words
    caller = re.sub(r"^(?:hello|hi|hey)\s*,?\s*", "", caller, flags=re.IGNORECASE).strip()

    # 2. Purpose extraction
    purpose = "General inquiry or notification"
    purpose_match = re.search(
        r"calling\s+(?:about|regarding|because)\s+([^.\n?!]+)",
        text,
        re.IGNORECASE,
    )
    if purpose_match:
        purpose = purpose_match.group(1).strip()
        if len(purpose) > 80:
            purpose = purpose[:77] + "..."
    else:
        # Heuristic keywords for purpose
        if re.search(r"\b(?:hospital|admitted|father|mother|emergency|accident)\b", text, re.IGNORECASE):
            purpose = "Urgent medical update / Hospital notice"
        elif re.search(r"\b(?:otp|pin|verify|account\s*blocked)\b", text, re.IGNORECASE):
            purpose = "Account security verification inquiry"
        elif re.search(r"\b(?:won|lottery|prize|lucky\s*draw)\b", text, re.IGNORECASE):
            purpose = "Prize claim / Reward announcement"
        else:
            # First sentence as purpose
            first_sentence = re.split(r"[.?!]\s*", text)[0].strip()
            if first_sentence:
                purpose = first_sentence[:60]

    # 3. Message summary (1-2 sentences)
    sentences = [s.strip() for s in re.split(r"[.?!]\s+", text) if s.strip()]
    if sentences:
        message = ". ".join(sentences[:2])
        if not message.endswith("."):
            message += "."
    else:
        message = text[:150]

    # 4. Priority
    urgent_keywords = re.compile(
        r"\b(?:emergency|hospital|accident|urgent|urgently|deadline|interview|exam|admitted)\b",
        re.IGNORECASE,
    )
    priority = "High" if urgent_keywords.search(text) else "Medium"

    # Suggested action
    suggested_action = (
        "Call back immediately" if priority == "High" else "Review summary when available"
    )

    return {
        "caller": caller or "Unknown",
        "purpose": purpose,
        "message": message,
        "priority": priority,
        "suggested_action": suggested_action,
        "risk_explanation": "",
        "ai_suspicious": False,
        "engine": "offline-fallback",
    }


def call_conversation_engine(transcript: str, availability: str = "Busy") -> Dict[str, Any]:
    """
    Call Anthropic API if key is available; fallback to offline regex extraction if
    no key is set, library missing, or an API error occurs.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return offline_fallback_extractor(transcript, availability)

    try:
        import anthropic

        model_name = os.getenv("AURA_MODEL", DEFAULT_MODEL)
        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""You are AURA AI, an intelligent personal receptionist.
Analyze the following phone transcript or SMS message.
User availability status: {availability}

Transcript:
\"\"\"{transcript}\"\"\"

Return ONLY a raw, valid JSON object with no markdown fences, no explanatory text, and exactly these keys:
- "caller": name of the caller or organization (or "Unknown")
- "purpose": short phrase explaining why they contacted
- "message": 1-2 sentence clear summary
- "priority": "Low", "Medium", or "High" (mark High for true emergencies, medical, critical deadlines)
- "suggested_action": short recommended action for the user
- "risk_explanation": one plain-language line evaluating safety or risk
- "ai_suspicious": boolean (true if language suggests manipulation, coercion, deception, or a scam even if standard keywords are avoided; otherwise false)
"""

        response = client.messages.create(
            model=model_name,
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )

        content_text = ""
        for block in response.content:
            if getattr(block, "text", None):
                content_text += block.text

        content_text = content_text.strip()

        # Remove markdown fences if present
        if content_text.startswith("```"):
            lines = content_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            content_text = "\n".join(lines).strip()

        data = json.loads(content_text)

        return {
            "caller": str(data.get("caller") or "Unknown").strip(),
            "purpose": str(data.get("purpose") or "General notification").strip(),
            "message": str(data.get("message") or transcript[:150]).strip(),
            "priority": str(data.get("priority") or "Medium").capitalize().strip(),
            "suggested_action": str(data.get("suggested_action") or "Review details").strip(),
            "risk_explanation": str(data.get("risk_explanation") or "").strip(),
            "ai_suspicious": bool(data.get("ai_suspicious", False)),
            "engine": f"anthropic ({model_name})",
        }

    except Exception:
        # Graceful fallback on API timeout, auth failure, network error, or JSON parse error
        fallback_data = offline_fallback_extractor(transcript, availability)
        fallback_data["engine"] = "offline-fallback"
        return fallback_data


def scan_security_signals(transcript: str) -> Tuple[List[Dict[str, Any]], int]:
    """
    Scan transcript using regex rules.
    Each detected signal adds points once and records matched evidence.
    Returns (signals_list, total_score).
    """
    signals: List[Dict[str, Any]] = []
    total_score = 0

    for signal_name, points, pattern in SECURITY_RULES:
        match = pattern.search(transcript)
        if match:
            matched_text = match.group(0).strip()
            signals.append({
                "signal": signal_name,
                "points": points,
                "evidence": matched_text,
            })
            total_score += points

    return signals, total_score


def determine_risk_level(score: int) -> str:
    """Map rule score to risk level: 0-2 = Low, 3-5 = Medium, 6+ = High."""
    if score >= 6:
        return "High"
    if score >= 3:
        return "Medium"
    return "Low"


def determine_handling_action(category: str, risk: str, priority: str, availability: str) -> str:
    """
    Determine handling action, evaluated top to bottom, first match wins:
    1. category blocked -> "Rejected: caller is on your blocked list"
    2. risk High -> "Do not engage. Review in Security Centre"
    3. category trusted -> "Notify immediately (trusted contact)"
    4. status Available and risk Low -> "Ring through (you are available)"
    5. status Do Not Disturb and priority not High -> "Hold: summary saved for later"
    6. priority High and risk Low -> "Notify immediately (urgent)"
    7. risk Medium -> "Caution: verify caller before replying"
    8. else -> "Save summary for review"
    """
    category = (category or "unknown").lower().strip()
    risk = (risk or "Low").capitalize().strip()
    priority = (priority or "Medium").capitalize().strip()
    availability = (availability or DEFAULT_AVAILABILITY).strip()

    if category == "blocked":
        return "Rejected: caller is on your blocked list"

    if risk == "High":
        return "Do not engage. Review in Security Centre"

    if category == "trusted":
        return "Notify immediately (trusted contact)"

    if availability == "Available" and risk == "Low":
        return "Ring through (you are available)"

    if availability == "Do Not Disturb" and priority != "High":
        return "Hold: summary saved for later"

    if priority == "High" and risk == "Low":
        return "Notify immediately (urgent)"

    if risk == "Medium":
        return "Caution: verify caller before replying"

    return "Save summary for review"


def analyze_call(
    transcript: str,
    caller_id: str = "",
    availability: Optional[str] = None,
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Full processing pipeline:
    Input -> Conversation Engine -> Security Engine -> Contact Rules -> Database.
    """
    if not transcript or not transcript.strip():
        raise ValueError("Transcript cannot be empty or whitespace only.")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    clean_caller_id = (caller_id or "").strip()

    # Retrieve current availability setting if not supplied
    if not availability:
        availability = get_setting("status", DEFAULT_AVAILABILITY, db_path=db_path) or DEFAULT_AVAILABILITY

    # 1. Conversation Engine (AI or offline fallback)
    ai_result = call_conversation_engine(transcript, availability=availability)

    # Resolve caller name
    extracted_caller = ai_result.get("caller", "Unknown")
    resolved_caller = clean_caller_id if clean_caller_id else extracted_caller

    purpose = ai_result.get("purpose", "General inquiry")
    message = ai_result.get("message", transcript[:150])
    priority = ai_result.get("priority", "Medium")
    engine = ai_result.get("engine", "offline-fallback")
    ai_suspicious = ai_result.get("ai_suspicious", False)

    # 2. Security Engine (Rule scoring + AI assist)
    signals, score = scan_security_signals(transcript)
    risk = determine_risk_level(score)

    # AI assist: if rules say Low but model returned ai_suspicious=true, raise to Medium
    if risk == "Low" and ai_suspicious:
        risk = "Medium"
        score += 1
        signals.append({
            "signal": "AI-detected manipulation",
            "points": 1,
            "evidence": "Pattern indicates potential deception or pressure tactics.",
        })

    # Build risk explanation
    explanation = ai_result.get("risk_explanation", "").strip()
    if not explanation:
        if signals:
            explanation = "Scam signals detected: " + ", ".join(s["signal"] for s in signals) + "."
        else:
            explanation = "No scam signals found."

    # Non-negotiable rule: A High-risk call must have its priority forced to Low
    if risk == "High":
        priority = "Low"

    # 3. Contacts and Rules Module
    lookup_name = clean_caller_id if clean_caller_id else resolved_caller
    category = get_contact_category(lookup_name, db_path=db_path)
    action = determine_handling_action(
        category=category,
        risk=risk,
        priority=priority,
        availability=availability,
    )

    # 4. Database save
    call_record = {
        "time": timestamp,
        "caller_id": clean_caller_id,
        "caller": resolved_caller,
        "purpose": purpose,
        "message": message,
        "priority": priority,
        "score": score,
        "risk": risk,
        "signals": signals,
        "explanation": explanation,
        "category": category,
        "action": action,
        "transcript": transcript,
        "engine": engine,
    }

    call_id = save_call(call_record, db_path=db_path)
    call_record["id"] = call_id
    return call_record


def save_call(call_data: Dict[str, Any], db_path: Optional[str] = None) -> int:
    """Save call record to database with parameterized query."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    try:
        with conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO calls (
                    time, caller_id, caller, purpose, message, priority,
                    score, risk, signals, explanation, category, action,
                    transcript, engine
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    call_data["time"],
                    call_data.get("caller_id", ""),
                    call_data.get("caller", "Unknown"),
                    call_data.get("purpose", ""),
                    call_data.get("message", ""),
                    call_data.get("priority", "Medium"),
                    call_data.get("score", 0),
                    call_data.get("risk", "Low"),
                    json.dumps(call_data.get("signals", [])),
                    call_data.get("explanation", ""),
                    call_data.get("category", "unknown"),
                    call_data.get("action", ""),
                    call_data.get("transcript", ""),
                    call_data.get("engine", "offline-fallback"),
                ),
            )
            return cur.lastrowid
    finally:
        conn.close()


def get_calls(
    limit: int = 100,
    risk_filter: Optional[List[str]] = None,
    db_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Retrieve call history with optional risk filter."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    try:
        cur = conn.cursor()
        if risk_filter:
            placeholders = ",".join("?" for _ in risk_filter)
            query = f"""
                SELECT * FROM calls
                WHERE risk IN ({placeholders})
                ORDER BY id DESC LIMIT ?
            """
            cur.execute(query, (*risk_filter, limit))
        else:
            cur.execute("SELECT * FROM calls ORDER BY id DESC LIMIT ?", (limit,))

        rows = cur.fetchall()
        result = []
        for row in rows:
            item = dict(row)
            try:
                item["signals_parsed"] = json.loads(item["signals"])
            except Exception:
                item["signals_parsed"] = []
            result.append(item)
        return result
    finally:
        conn.close()


def get_security_calls(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve only Medium and High risk calls, newest first."""
    return get_calls(limit=100, risk_filter=["Medium", "High"], db_path=db_path)
