# AURA AI (Automated User Reception & Assistance)

A personal AI receptionist with a built-in fraud and scam-detection layer for Windows laptops.

AURA AI solves two major communication problems:
1. **Fraud by phone / SMS:** Protects users against OTP theft, fake bank calls, prize scams, phishing links, and coercion to transfer money.
2. **Missed calls with no context:** Screens calls when you are busy or in Do Not Disturb mode, providing concise summaries, urgency classification, and actionable routing.

---

## 🚀 Quick Start Guide (Windows)

Follow these simple steps to run AURA AI on your Windows computer:

### 1. Install Python 3.11 or Newer
- Download Python from [python.org](https://www.python.org/downloads/).
- **CRITICAL STEP:** During installation, tick the checkbox **"Add Python to PATH"** before clicking "Install Now".

### 2. Open a Terminal in the Project Folder
- Open File Explorer and navigate to this folder: `AURA_AI`
- Click the address bar at the top, type `cmd` or `powershell`, and press **Enter**.

### 3. Install Required Dependencies
In your command prompt or PowerShell, run:
```bash
pip install -r requirements.txt
```
> **Troubleshooting tip:** If `pip` is not recognized, run:
> ```bash
> python -m pip install -r requirements.txt
> ```

### 4. (Optional) Set Your Anthropic Claude API Key
AURA AI has an **automatic offline fallback**. If you do not have an API key, the app still works completely using its built-in local heuristics and regex engine!

To enable the Claude LLM engine:
- In Windows Command Prompt:
  ```cmd
  set ANTHROPIC_API_KEY=your_anthropic_api_key_here
  ```
- Or in PowerShell:
  ```powershell
  $env:ANTHROPIC_API_KEY="your_anthropic_api_key_here"
  ```
- (Optional) Customize the Claude model (defaults to `claude-sonnet-5-5`):
  ```cmd
  set AURA_MODEL=claude-sonnet-5-5
  ```

### 5. Launch the Application
Run:
```bash
streamlit run app.py
```
> **Troubleshooting tip:** If `streamlit` is not recognized, run:
> ```bash
> python -m streamlit run app.py
> ```
The app will open automatically in your browser at `http://localhost:8501`.

---

## 🧪 Running Automated Acceptance Tests
AURA AI comes with an automated test suite verifying all 8 core acceptance rules. Run:
```bash
python tests.py
```
Expected output:
```text
Ran 8 tests in ...s
OK
```

---

## 🛡️ How AURA AI Works

### Data Flow
```text
Input (Text / SMS) ➡️ Conversation Engine (AI / Fallback) ➡️ Security Engine (Rules + AI) ➡️ Contact Rules ➡️ SQLite Database ➡️ Streamlit Dashboard
```

### Risk Level Scoring
The security engine evaluates scam signals against case-insensitive rules. Each signal adds points once:

| Signal | Examples | Points |
|---|---|---|
| **Credential request** | OTP, PIN, CVV, password, card number, Aadhaar, verification code | **3** |
| **Urgency** | immediately, right now, urgent, in ten minutes, within 30 minutes, last chance, expires today, hurry | **2** |
| **Threat** | account will be blocked/suspended/frozen, legal action, arrest, penalty, SIM will be blocked, case filed | **2** |
| **Suspicious link** | http(s) URLs, bit.ly / tinyurl / cutt.ly, www links, odd TLDs (.xyz, .top, .click, .info) | **2** |
| **Reward claim** | you have won, lottery, prize, cashback, gift card, congratulations, lucky draw | **2** |
| **Money request** | send/transfer/pay/deposit + money/Rs/amount/fee, processing fee, registration fee | **3** |

- **Risk Levels:**
  - 🟢 **Low:** Score `0 - 2`
  - 🟠 **Medium:** Score `3 - 5`
  - 🔴 **High:** Score `6+`
- **Scammer Priority Rule:** A High-risk call automatically has its priority forced to **Low** (scammers never deserve a callback).

### Contact Categorization & Handling Rules
Handling actions are evaluated top to bottom; first match wins:
1. Category `blocked` ➡️ *"Rejected: caller is on your blocked list"*
2. Risk `High` ➡️ *"Do not engage. Review in Security Centre"*
3. Category `trusted` ➡️ *"Notify immediately (trusted contact)"*
4. Status `Available` & Risk `Low` ➡️ *"Ring through (you are available)"*
5. Status `Do Not Disturb` & Priority not `High` ➡️ *"Hold: summary saved for later"*
6. Priority `High` & Risk `Low` ➡️ *"Notify immediately (urgent)"*
7. Risk `Medium` ➡️ *"Caution: verify caller before replying"*
8. Else ➡️ *"Save summary for review"*

---

## 📁 File Structure
```text
AURA_AI/
├── core.py            # All logic: security rules, AI engine, contact rules, database
├── app.py             # Streamlit UI dashboard (imports core.py)
├── requirements.txt   # streamlit, pandas, anthropic
├── README.md          # Beginner-friendly documentation and Windows run guide
├── tests.py           # Automated test suite for the 8 acceptance checks
└── aura.db            # Auto-generated SQLite database (stores calls, contacts, settings)
```

---

## 🔒 Non-Negotiable Safety Principles
- **Advisory Risk Reporting:** AURA AI reports risk probability and evidence, never absolute certainty ("risk", never "this is definitely a scam").
- **User in Control:** Blocking numbers only occurs after explicit user approval in the Security Centre; it is never automatic.
- **Original Transcript Preservation:** The original text of every call is stored unaltered in the database for legal and audit safety.
- **Privacy First:** Keys are read from environment variables; transcripts and contacts stay on your local computer in SQLite (`aura.db`).
