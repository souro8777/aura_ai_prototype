"""
AURA AI - Streamlit User Interface
Automated User Reception & Assistance with Scam-Detection Layer
Dual-tone Theme:
- Dark Mode (Deep Midnight #080A12, Violet & Electric Blue)
- Light Mode (Crisp White #FFFFFF & Sky Blue #0284C7)
"""

import textwrap
import streamlit as st
import pandas as pd
import core

# Page configuration
st.set_page_config(
    page_title="AURA AI - Personal Receptionist & Fraud Shield",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ensure database tables exist
core.init_db()

# ---------------------------------------------------------
# THEME STATE & PALETTE CONFIGURATION
# ---------------------------------------------------------
THEME_OPTIONS = [
    "Dark Mode",
    "Light Mode",
]

# Read saved theme and normalize to current options
saved_theme = core.get_setting("ui_theme", THEME_OPTIONS[0])
if "Light" in str(saved_theme):
    saved_theme = THEME_OPTIONS[1]
else:
    saved_theme = THEME_OPTIONS[0]
core.set_setting("ui_theme", saved_theme)

is_dark = (saved_theme == THEME_OPTIONS[0])

# Dual Tone Palettes
if is_dark:
    # Deep midnight background, Violet and electric-blue highlights, Soft lavender text accents
    BG_COLOR = "#080A12"           # Deep midnight background
    SIDEBAR_BG = "#0B0E1B"         # Midnight sidebar
    SURFACE_COLOR = "#101628"      # Midnight surface cards
    BORDER_COLOR = "#243054"       # Midnight slate border
    TEXT_COLOR = "#E9D5FF"         # Soft lavender text accents
    TEXT_MUTED = "#C4B5FD"         # Soft lavender secondary accents
    ACCENT_COLOR = "#8B5CF6"       # Vivid Violet highlight
    ACCENT_LIGHT = "#38BDF8"       # Electric Blue highlight
    ACCENT_DARK = "#6D28D9"        # Deep Violet
    ACCENT_GLOW = "rgba(139, 92, 246, 0.45)"
    ACCENT_SUBTLE = "rgba(139, 92, 246, 0.16)"
    CARD_TOP_BORDER = "#8B5CF6"
    BRAND_GRADIENT = "linear-gradient(135deg, #C084FC 0%, #818CF8 35%, #38BDF8 70%, #06B6D4 100%)"
    LOGO_COLOR_1 = "#C084FC"       # Lavender Violet
    LOGO_COLOR_2 = "#38BDF8"       # Electric Blue
else:
    # White and Sky Blue
    BG_COLOR = "#FFFFFF"
    SIDEBAR_BG = "#F4F9FD"
    SURFACE_COLOR = "#EBF5FC"
    BORDER_COLOR = "#BAE6FD"
    TEXT_COLOR = "#0C4A6E"
    TEXT_MUTED = "#475569"
    ACCENT_COLOR = "#0284C7"       # Electric Sky Blue
    ACCENT_LIGHT = "#38BDF8"
    ACCENT_DARK = "#0369A1"
    ACCENT_GLOW = "rgba(14, 165, 233, 0.30)"
    ACCENT_SUBTLE = "rgba(14, 165, 233, 0.12)"
    CARD_TOP_BORDER = "#0284C7"
    BRAND_GRADIENT = "linear-gradient(135deg, #0284C7 0%, #0EA5E9 50%, #38BDF8 100%)"
    LOGO_COLOR_1 = "#0284C7"
    LOGO_COLOR_2 = "#38BDF8"


def generate_logo_svg(size=40):
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle;">'
        f'<defs>'
        f'<linearGradient id="auraGrad_{size}" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="{LOGO_COLOR_1}"/>'
        f'<stop offset="100%" stop-color="{LOGO_COLOR_2}"/>'
        f'</linearGradient>'
        f'</defs>'
        f'<path d="M50 10 L84 26 C84 60 50 88 50 88 C50 88 16 60 16 26 Z" fill="{ACCENT_SUBTLE}" stroke="url(#auraGrad_{size})" stroke-width="4.5" stroke-linejoin="round"/>'
        f'<circle cx="50" cy="46" r="16" stroke="url(#auraGrad_{size})" stroke-width="3.5" stroke-dasharray="4 3"/>'
        f'<circle cx="50" cy="46" r="6" fill="url(#auraGrad_{size})"/>'
        f'<line x1="32" y1="41" x2="32" y2="51" stroke="url(#auraGrad_{size})" stroke-width="3" stroke-linecap="round"/>'
        f'<line x1="26" y1="44" x2="26" y2="48" stroke="url(#auraGrad_{size})" stroke-width="2.5" stroke-linecap="round"/>'
        f'<line x1="68" y1="41" x2="68" y2="51" stroke="url(#auraGrad_{size})" stroke-width="3" stroke-linecap="round"/>'
        f'<line x1="74" y1="44" x2="74" y2="48" stroke="url(#auraGrad_{size})" stroke-width="2.5" stroke-linecap="round"/>'
        f'</svg>'
    )


# ---------------------------------------------------------
# INJECT DEDENTED CUSTOM CSS (ZERO LEADING SPACES)
# ---------------------------------------------------------
custom_css = textwrap.dedent(f"""
<style>
/* App Root */
.stApp {{
    background-color: {BG_COLOR} !important;
    color: {TEXT_COLOR} !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}}

header[data-testid="stHeader"] {{
    background-color: {BG_COLOR} !important;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background-color: {SIDEBAR_BG} !important;
    border-right: 1px solid {BORDER_COLOR} !important;
}}
section[data-testid="stSidebar"] * {{
    color: {TEXT_COLOR} !important;
}}

/* All Headings, Paragraphs and Markdown text */
h1, h2, h3, h4, h5, h6, p, span, label, div[data-testid="stMarkdownContainer"] p {{
    color: {TEXT_COLOR} !important;
}}

/* Floating Primary Button with Violet & Electric-Blue Highlights */
button[kind="primary"] {{
    background: {BRAND_GRADIENT} !important;
    border: none !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    border-radius: 8px !important;
    padding: 10px 22px !important;
    box-shadow: 0 4px 16px {ACCENT_GLOW} !important;
    transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.2s ease !important;
}}
button[kind="primary"]:hover {{
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 8px 24px rgba(56, 189, 248, 0.5) !important;
    color: #FFFFFF !important;
}}

/* Floating Secondary Button */
button[kind="secondary"] {{
    background-color: {SURFACE_COLOR} !important;
    border: 1px solid {BORDER_COLOR} !important;
    color: {TEXT_COLOR} !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    transition: transform 0.2s ease, border-color 0.2s ease !important;
}}
button[kind="secondary"]:hover {{
    transform: translateY(-2px) !important;
    border-color: {ACCENT_LIGHT} !important;
    color: {ACCENT_LIGHT} !important;
}}

/* Floating Metric Cards */
[data-testid="stMetric"] {{
    background-color: {SURFACE_COLOR} !important;
    border: 1px solid {BORDER_COLOR} !important;
    border-top: 3.5px solid {CARD_TOP_BORDER} !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}}
[data-testid="stMetric"]:hover {{
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 22px {ACCENT_GLOW} !important;
}}
[data-testid="stMetricLabel"] {{
    color: {TEXT_MUTED} !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
}}
[data-testid="stMetricValue"] {{
    color: #FFFFFF !important;
    font-weight: 800 !important;
}}

/* Container borders */
[data-testid="stVerticalBlockBorderWrapper"] {{
    border-color: {BORDER_COLOR} !important;
    background-color: {SURFACE_COLOR} !important;
    border-radius: 10px !important;
}}

/* Floating Features Container */
.floating-feature-box {{
    animation: featureFloatAnim 5s ease-in-out infinite;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}}
.floating-feature-box:hover {{
    transform: translateY(-5px);
    box-shadow: 0 10px 24px {ACCENT_GLOW};
}}
@keyframes featureFloatAnim {{
    0%, 100% {{ transform: translateY(0px); }}
    50% {{ transform: translateY(-3px); }}
}}

/* Tab Headers */
.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
    border-bottom: 2px solid {BORDER_COLOR};
    background-color: transparent;
}}
.stTabs [data-baseweb="tab"] {{
    color: {TEXT_MUTED} !important;
    font-weight: 700;
    padding: 10px 18px;
    border-radius: 8px 8px 0 0;
}}
.stTabs [aria-selected="true"] {{
    color: {ACCENT_LIGHT} !important;
    background-color: {SURFACE_COLOR} !important;
    border-bottom: 3px solid {ACCENT_COLOR} !important;
}}

/* Roll-down Expanders: PREVENT TEXT FROM TURNING WHITE WHEN ROLLED DOWN */
[data-testid="stExpander"] {{
    background-color: {SURFACE_COLOR} !important;
    border: 1px solid {BORDER_COLOR} !important;
    border-radius: 8px !important;
    margin-bottom: 8px !important;
}}
[data-testid="stExpander"] details summary,
[data-testid="stExpander"] details summary *,
[data-testid="stExpander"] details summary span,
[data-testid="stExpander"] details summary p,
[data-testid="stExpander"] details[open] summary,
[data-testid="stExpander"] details[open] summary *,
[data-testid="stExpander"] details[open] summary span,
[data-testid="stExpander"] details[open] summary p,
[data-testid="stExpander"] details summary:hover,
[data-testid="stExpander"] details summary:hover *,
[data-testid="stExpander"] details summary:focus,
[data-testid="stExpander"] details summary:focus *,
[data-testid="stExpander"] details[open] summary:hover,
[data-testid="stExpander"] details[open] summary:hover *,
[data-testid="stExpander"] details[open] summary:focus,
[data-testid="stExpander"] details[open] summary:focus * {{
    color: {TEXT_COLOR} !important;
    font-weight: 700 !important;
}}
[data-testid="stExpander"] details summary svg,
[data-testid="stExpander"] details[open] summary svg,
[data-testid="stExpander"] [data-testid="stExpanderToggleIcon"] {{
    stroke: {TEXT_COLOR} !important;
    fill: {TEXT_COLOR} !important;
    color: {TEXT_COLOR} !important;
}}
[data-testid="stExpander"] [data-testid="stExpanderDetails"],
[data-testid="stExpander"] [data-testid="stExpanderDetails"] * {{
    color: {TEXT_COLOR} !important;
}}
[data-testid="stExpander"] code {{
    color: {ACCENT_LIGHT} !important;
    background-color: rgba(56, 189, 248, 0.12) !important;
    border: 1px solid {BORDER_COLOR} !important;
    border-radius: 4px !important;
    padding: 1px 4px !important;
}}

/* Radio button options inside expanders */
[data-testid="stRadio"] label,
[data-testid="stRadio"] label p,
[data-testid="stRadio"] label span,
[data-testid="stRadio"] div[role="radiogroup"] p,
[data-testid="stRadio"] div[role="radiogroup"] span {{
    color: {TEXT_COLOR} !important;
    font-weight: 600 !important;
}}

/* Inputs & Textareas */
textarea, input[type="text"] {{
    background-color: {SURFACE_COLOR} !important;
    color: {TEXT_COLOR} !important;
    border: 1px solid {BORDER_COLOR} !important;
    border-radius: 8px !important;
}}
textarea:focus, input[type="text"]:focus {{
    border-color: {ACCENT_COLOR} !important;
    box-shadow: 0 0 0 2px {ACCENT_GLOW} !important;
}}
</style>
""").strip()

st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR: Extreme left top corner Brand + Roll-down Expanders
# ---------------------------------------------------------

# 1. Extreme Left Top Corner Brand Header
sidebar_header_html = textwrap.dedent(f"""
<div style="margin-bottom: 12px; padding-top: 4px;">
    <div style="display: flex; align-items: center; gap: 8px;">
        <div>{generate_logo_svg(32)}</div>
        <div style="font-size: 1.75rem; font-weight: 900; letter-spacing: -0.5px; background: {BRAND_GRADIENT}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">AURA AI</div>
    </div>
    <div style="font-size: 0.72rem; letter-spacing: 0.4px; color: {TEXT_MUTED}; text-transform: uppercase; font-weight: 700; margin-top: 3px;">
        Automated User Reception & Assistance
    </div>
</div>
""").strip()

st.sidebar.markdown(sidebar_header_html, unsafe_allow_html=True)
st.sidebar.markdown(f"<hr style='border: none; border-top: 1px solid {BORDER_COLOR}; margin: 8px 0 14px 0;'/>", unsafe_allow_html=True)

# Retrieve persisted status from database
saved_status = core.get_setting("status", core.DEFAULT_AVAILABILITY) or core.DEFAULT_AVAILABILITY
if saved_status not in core.AVAILABILITY_OPTIONS:
    saved_status = core.DEFAULT_AVAILABILITY

# 2. Roll down 1: Interface Theme (strictly Dark Mode and Light Mode, no color codes or previews)
with st.sidebar.expander("Interface Theme", expanded=False):
    theme_choice = st.radio(
        "Choose Interface Theme:",
        options=THEME_OPTIONS,
        index=THEME_OPTIONS.index(saved_theme),
        key="theme_radio_select",
    )
    if theme_choice != saved_theme:
        core.set_setting("ui_theme", theme_choice)
        st.rerun()

# 3. Roll down 2: Your Availability
with st.sidebar.expander(f"Your Availability ({saved_status})", expanded=False):
    selected_status = st.radio(
        "Set Availability Status:",
        options=core.AVAILABILITY_OPTIONS,
        index=core.AVAILABILITY_OPTIONS.index(saved_status),
        key="status_radio_select",
        help="Determines screening and routing rules for incoming calls.",
    )
    if selected_status != saved_status:
        core.set_setting("status", selected_status)
        st.info(f"Status updated to: {selected_status}")
        st.rerun()

# 4. Roll down 3: Risk Scoring Protocol
with st.sidebar.expander("Risk Scoring Protocol", expanded=False):
    st.markdown(
        textwrap.dedent(f"""
        <div style="font-size: 0.82rem; line-height: 1.6; color: {TEXT_COLOR};">
            • <strong>Low (0 - 2 pts):</strong> Standard / Verified<br/>
            • <strong>Medium (3 - 5 pts):</strong> Suspicious Signals<br/>
            • <strong>High (6+ pts):</strong> Severe Fraud Threat
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )

# 5. Roll down 4: Settings & Engine Details (Claude API part removed)
with st.sidebar.expander("Settings & Engine Details", expanded=False):
    st.markdown(
        textwrap.dedent(f"""
        <div style="font-size: 0.82rem; line-height: 1.6; color: {TEXT_COLOR};">
            <strong>Screening Engine:</strong> AURA Security Core<br/>
            <strong>Status:</strong> Active & Monitoring<br/>
            <strong>Detection Protocol:</strong> Deterministic 6-Vector Heuristics<br/>
            <hr style="border: none; border-top: 1px solid {BORDER_COLOR}; margin: 8px 0;"/>
            <strong>Database Storage:</strong> <code>{core.get_db_path()}</code><br/>
            <strong>Active Interface Theme:</strong> {saved_theme}
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# SAMPLE TRANSCRIPTS
# ---------------------------------------------------------
READY_MADE_SAMPLES = {
    "-- Select a sample transcript --": {
        "caller": "",
        "text": "",
    },
    "Normal contact (Study group reschedule)": {
        "caller": "Rahul",
        "text": "Hi, this is Rahul. I'm calling about tonight's study group, can we move it to 8 pm?",
    },
    "Urgent hospital notice (Father admitted)": {
        "caller": "Priya",
        "text": "This is Priya from City Hospital. Your father was admitted this morning, please call back urgently.",
    },
    "Scam fake bank OTP (Account block threat)": {
        "caller": "SBI Customer Care",
        "text": "Hello, this is SBI customer care. Your account will be blocked in ten minutes. Tell me your OTP immediately to verify.",
    },
    "Scam prize SMS with link (Lucky draw award)": {
        "caller": "Prize Center",
        "text": "Congratulations! You have won a lucky draw prize of Rs 50,000. Pay a processing fee and claim at http://bit.ly/claim-now",
    },
    "Other (Write your own transcript)": {
        "caller": "",
        "text": "",
    },
}

# ---------------------------------------------------------
# TOP HERO HEADER:
# Full form with large font size and brand gradient (matching left side AURA AI)
# Middle AURA AI small and styled like left corner full form
# ---------------------------------------------------------
hero_header_html = textwrap.dedent(f"""
<div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid {BORDER_COLOR}; padding-bottom: 14px; margin-bottom: 18px;">
    <div style="display: flex; align-items: center; gap: 14px;">
        <div>{generate_logo_svg(46)}</div>
        <div>
            <div style="font-size: 1.75rem; font-weight: 900; letter-spacing: -0.5px; background: {BRAND_GRADIENT}; -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.2;">
                Automated User Reception & Assistance
            </div>
            <div style="font-size: 0.75rem; letter-spacing: 1px; color: {TEXT_MUTED}; text-transform: uppercase; font-weight: 700; margin-top: 3px;">
                AURA AI
            </div>
        </div>
    </div>
    <div style="text-align: right;">
        <div style="font-size: 0.75rem; color: {TEXT_MUTED}; text-transform: uppercase; font-weight: 700;">Status</div>
        <div style="font-size: 1.05rem; font-weight: 800; color: {ACCENT_LIGHT};">{saved_status}</div>
    </div>
</div>
""").strip()

st.markdown(hero_header_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------
tab_simulate, tab_history, tab_security, tab_contacts = st.tabs([
    "Simulate Call",
    "Call History",
    "Security Centre",
    "Contacts",
])

# ---------------------------------------------------------
# TAB 1: SIMULATE CALL (MIDDLE FLOATING FEATURE CARDS)
# ---------------------------------------------------------
with tab_simulate:
    # Feature Showcase Visual Cards (Middle Floating)
    col_w1, col_w2, col_w3 = st.columns(3)

    with col_w1.container(border=True):
        st.markdown(
            textwrap.dedent(f"""
            <div class="floating-feature-box">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="{ACCENT_LIGHT}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                        <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                        <line x1="12" y1="19" x2="12" y2="23"/>
                        <line x1="8" y1="23" x2="16" y2="23"/>
                    </svg>
                    <span style="font-weight: 700; font-size: 0.95rem; color: {TEXT_COLOR};">Reception Core</span>
                </div>
                <div style="font-size: 0.82rem; color: {TEXT_MUTED}; line-height: 1.4;">
                    Extracts caller identity, intent, and drafts 1-2 sentence summaries automatically.
                </div>
            </div>
            """).strip(),
            unsafe_allow_html=True,
        )

    with col_w2.container(border=True):
        st.markdown(
            textwrap.dedent(f"""
            <div class="floating-feature-box">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="{ACCENT_COLOR}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                    </svg>
                    <span style="font-weight: 700; font-size: 0.95rem; color: {TEXT_COLOR};">Fraud Shield Radar</span>
                </div>
                <div style="font-size: 0.82rem; color: {TEXT_MUTED}; line-height: 1.4;">
                    Deterministic 6-vector regex heuristics + AI anomaly detection for OTP, urgency, and threats.
                </div>
            </div>
            """).strip(),
            unsafe_allow_html=True,
        )

    with col_w3.container(border=True):
        st.markdown(
            textwrap.dedent(f"""
            <div class="floating-feature-box">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="{ACCENT_LIGHT}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                        <circle cx="8.5" cy="7" r="4"/>
                        <line x1="20" y1="8" x2="20" y2="14"/>
                        <line x1="23" y1="11" x2="17" y2="11"/>
                    </svg>
                    <span style="font-weight: 700; font-size: 0.95rem; color: {TEXT_COLOR};">Rules & Routing</span>
                </div>
                <div style="font-size: 0.82rem; color: {TEXT_MUTED}; line-height: 1.4;">
                    Priority firewall evaluates trusted contacts, DND holds, and prevents scam callbacks.
                </div>
            </div>
            """).strip(),
            unsafe_allow_html=True,
        )

    st.subheader("Incoming Communication Simulation")

    # Sample selector dropdown (includes 'Other (Write your own transcript)')
    selected_sample_key = st.selectbox(
        "Load sample transcript:",
        options=list(READY_MADE_SAMPLES.keys()),
        index=0,
    )

    # Initialize session state for inputs
    if "input_transcript" not in st.session_state:
        st.session_state["input_transcript"] = ""
    if "input_caller" not in st.session_state:
        st.session_state["input_caller"] = ""

    # Populate inputs upon sample selection
    if selected_sample_key == "Other (Write your own transcript)":
        if st.session_state.get("_last_selected_sample") != selected_sample_key:
            st.session_state["input_transcript"] = ""
            st.session_state["input_caller"] = ""
            st.session_state["_last_selected_sample"] = selected_sample_key
    elif selected_sample_key != "-- Select a sample transcript --":
        sample_data = READY_MADE_SAMPLES[selected_sample_key]
        if st.session_state.get("_last_selected_sample") != selected_sample_key:
            st.session_state["input_transcript"] = sample_data["text"]
            st.session_state["input_caller"] = sample_data["caller"]
            st.session_state["_last_selected_sample"] = selected_sample_key

    if selected_sample_key == "Other (Write your own transcript)":
        st.caption("Write or paste your custom communication below to analyze it.")

    col_input_caller, col_status_display = st.columns([2, 1])
    with col_input_caller:
        caller_input = st.text_input(
            "Caller Name / Number (Optional)",
            value=st.session_state.get("input_caller", ""),
            placeholder="e.g. Rahul, SBI Support, +91 98765 43210",
            help="If left empty, AURA extracts the identity from the transcript.",
            key="caller_name_input_field",
        )

    with col_status_display:
        st.markdown(f"**Screening Status:** `{saved_status}`")
        st.caption("Change status anytime in the sidebar.")

    transcript_input = st.text_area(
        "Call Transcript or SMS Content *",
        value=st.session_state.get("input_transcript", ""),
        height=130,
        placeholder="Type or paste incoming call transcript or SMS message...",
        key="transcript_text_area",
    )

    is_empty_input = not bool(transcript_input.strip())

    analyze_clicked = st.button(
        "Analyze & Screen Call",
        type="primary",
        disabled=is_empty_input,
        help="Run reception screening and scam detection." if not is_empty_input else "Please enter transcript text.",
    )

    if analyze_clicked:
        if is_empty_input:
            st.warning("Please enter a call transcript or SMS message to analyze.")
        else:
            with st.spinner("Screening call through AURA AI engine..."):
                try:
                    result = core.analyze_call(
                        transcript=transcript_input,
                        caller_id=caller_input,
                        availability=saved_status,
                    )
                    st.session_state["last_analysis_result"] = result
                except Exception as err:
                    st.error(f"Analysis Error: {err}")

    # Display Analysis Output
    if "last_analysis_result" in st.session_state:
        res = st.session_state["last_analysis_result"]

        st.markdown(f"<hr style='border: none; border-top: 1px solid {BORDER_COLOR}; margin: 24px 0;'/>", unsafe_allow_html=True)
        st.subheader("Screening Report")

        risk_level = res["risk"]
        score = res["score"]
        risk_label = f"{risk_level} (Score: {score})"

        # 3 Floating Metrics
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric("Risk Assessment", risk_label)
        with m_col2:
            st.metric("Priority Level", res["priority"])
        with m_col3:
            st.metric("Contact Category", res["category"].capitalize())

        # Handling Action Callout
        action_text = res["action"]
        if risk_level == "High":
            st.error(f"Recommended Handling: {action_text}")
        elif risk_level == "Medium":
            st.warning(f"Recommended Handling: {action_text}")
        else:
            st.success(f"Recommended Handling: {action_text}")

        # Call Details Summary Container
        with st.container(border=True):
            st.markdown(f"**Caller Identified:** `{res['caller']}`")
            st.markdown(f"**Purpose:** {res['purpose']}")
            st.markdown(f"**Summary Message:** {res['message']}")
            st.markdown("**Engine:** AURA Security Core")
            st.markdown(f"**Why this risk level:** {res['explanation']}")

        # Detected Signals Table
        signals = res.get("signals", [])
        if signals:
            st.markdown("##### Detected Risk Signals & Evidence")
            df_signals = pd.DataFrame(signals)
            df_signals = df_signals.rename(
                columns={"signal": "Signal Name", "points": "Points", "evidence": "Matched Evidence"}
            )
            st.dataframe(df_signals, hide_index=True, width="stretch")
        else:
            st.info("No suspicious signals or keywords detected.")

# ---------------------------------------------------------
# TAB 2: CALL HISTORY
# ---------------------------------------------------------
with tab_history:
    st.subheader("Call History")
    st.caption("Review screened calls and audit trails.")

    filter_col, count_col = st.columns([3, 1])
    with filter_col:
        risk_filter = st.multiselect(
            "Filter calls by Risk Level:",
            options=["Low", "Medium", "High"],
            default=["Low", "Medium", "High"],
        )

    calls = core.get_calls(limit=100, risk_filter=risk_filter if risk_filter else None)

    with count_col:
        st.metric("Total Calls Found", len(calls))

    if not calls:
        st.info("No calls found matching the selected filter.")
    else:
        table_data = []
        for c in calls:
            table_data.append({
                "Time": c["time"],
                "Caller": c["caller"],
                "Purpose": c["purpose"],
                "Message": c["message"],
                "Priority": c["priority"],
                "Risk": c["risk"],
                "Action": c["action"],
            })
        df_calls = pd.DataFrame(table_data)
        st.dataframe(df_calls, hide_index=True, width="stretch")

        st.markdown(f"<hr style='border: none; border-top: 1px solid {BORDER_COLOR}; margin: 20px 0;'/>", unsafe_allow_html=True)
        st.subheader("Original Transcripts (Latest 20 Calls)")
        for c in calls[:20]:
            expander_title = f"{c['time']} | {c['caller']} | Risk: {c['risk']} | {c['purpose']}"
            with st.expander(expander_title):
                st.markdown(f"**Action:** `{c['action']}` | **Priority:** `{c['priority']}` | **Engine:** AURA Security Core")
                st.markdown("**Original Transcript:**")
                st.code(c["transcript"], language="text")

# ---------------------------------------------------------
# TAB 3: SECURITY CENTRE
# ---------------------------------------------------------
with tab_security:
    st.subheader("Security Centre")
    st.caption("Review flagged Medium and High risk calls. Blocking requires explicit approval.")

    security_calls = core.get_security_calls()

    if not security_calls:
        with st.container(border=True):
            st.markdown(
                textwrap.dedent(f"""
                <div style="text-align: center; padding: 22px 0;">
                    <div style="margin-bottom: 10px;">
                        <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="{ACCENT_LIGHT}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                            <path d="m9 12 2 2 4-4"/>
                        </svg>
                    </div>
                    <div style="font-size: 1.15rem; font-weight: 700; color: {TEXT_COLOR};">Nothing Flagged</div>
                    <div style="font-size: 0.88rem; color: {TEXT_MUTED}; margin-top: 4px;">All processed incoming calls are currently within Low risk parameters.</div>
                </div>
                """).strip(),
                unsafe_allow_html=True,
            )
    else:
        for idx, sc in enumerate(security_calls):
            caller_name = sc["caller"]
            current_category = core.get_contact_category(caller_name)
            risk_badge = f"[{sc['risk'].upper()} RISK]"

            exp_label = f"{risk_badge} Caller: {caller_name} | {sc['time']} - {sc['purpose']}"
            with st.expander(exp_label, expanded=(idx == 0)):
                st.markdown(f"**Risk Level:** `{sc['risk']}` (Score: {sc['score']})")
                st.markdown(f"**Explanation:** {sc['explanation']}")
                st.markdown(f"**Recommended Action:** `{sc['action']}`")
                st.markdown(f"**Current Contact Status:** `{current_category}`")

                signals_list = sc.get("signals_parsed", [])
                if signals_list:
                    st.markdown("**Flagged Signals:**")
                    df_sec_sig = pd.DataFrame(signals_list)
                    df_sec_sig = df_sec_sig.rename(
                        columns={"signal": "Signal", "points": "Points", "evidence": "Evidence"}
                    )
                    st.dataframe(df_sec_sig, hide_index=True, width="stretch")

                st.markdown("**Original Transcript:**")
                st.code(sc["transcript"], language="text")

                # Action button to block caller
                if current_category == "blocked":
                    st.info(f"Caller '{caller_name}' is already marked as blocked.")
                else:
                    block_btn_key = f"block_btn_{sc['id']}_{idx}"
                    if st.button(f"Approve: block '{caller_name}'", key=block_btn_key, type="secondary"):
                        core.upsert_contact(caller_name, "blocked")
                        st.success(f"Caller '{caller_name}' has been added to your blocked list.")
                        st.rerun()

# ---------------------------------------------------------
# TAB 4: CONTACTS
# ---------------------------------------------------------
with tab_contacts:
    st.subheader("Manage Contacts")
    st.caption("Configure screening behavior by assigning contacts to trusted, known, unknown, or blocked lists.")

    col_add, col_list = st.columns([1, 1])

    with col_add:
        st.markdown("##### Add or Update Contact")
        with st.form("contact_form", clear_on_submit=True):
            new_contact_name = st.text_input("Contact Name *", placeholder="e.g. Rahul, SBI Customer Care")
            new_contact_category = st.selectbox(
                "Category *",
                options=core.CONTACT_CATEGORIES,
                format_func=lambda x: f"{x.capitalize()} ({'Immediate notify' if x == 'trusted' else 'Blocked from ringing' if x == 'blocked' else 'Standard screening'})",
            )
            submit_contact = st.form_submit_button("Save Contact", type="primary")

            if submit_contact:
                if not new_contact_name.strip():
                    st.error("Contact name cannot be empty.")
                else:
                    core.upsert_contact(new_contact_name.strip(), new_contact_category)
                    st.success(f"Contact '{new_contact_name.strip()}' saved as '{new_contact_category}'.")
                    st.rerun()

    with col_list:
        st.markdown("##### Saved Contacts")
        all_contacts = core.list_contacts()
        if not all_contacts:
            st.info("No saved contacts yet. Add your trusted contacts, family, or known numbers.")
        else:
            df_contacts = pd.DataFrame(all_contacts)
            df_contacts = df_contacts.rename(columns={"id": "ID", "name": "Name", "category": "Category"})
            st.dataframe(df_contacts[["Name", "Category"]], hide_index=True, width="stretch")

            contact_to_remove = st.selectbox(
                "Select contact to remove:",
                options=[c["name"] for c in all_contacts],
                key="delete_contact_select",
            )
            if st.button("Remove Selected Contact", type="secondary"):
                matching = [c["id"] for c in all_contacts if c["name"] == contact_to_remove]
                if matching:
                    core.delete_contact(matching[0])
                    st.success(f"Removed contact '{contact_to_remove}'.")
                    st.rerun()
