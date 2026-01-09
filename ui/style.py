import streamlit as st


def inject_style() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Source+Serif+4:wght@600&display=swap');

        :root {
          --ink: #1f1f24;
          --muted: #5b5e6a;
          --accent: #0e8f7e;
          --accent-2: #f0a202;
          --card: #ffffff;
          --bg: #ffffff;
          --sidebar: #d8f0ff;
          --sidebar-dark: #2b4d6e;
          --title-bg: #e8f6ff;
          --field-bg: #f3f9ff;
          --soft-button: #d9ecff;
        }

        .stApp {
          background: var(--bg);
          color: var(--ink);
          font-family: "Space Grotesk", "Segoe UI", "Trebuchet MS", sans-serif;
          font-size: 20px;
        }

        h1, h2, h3 {
          font-family: "Source Serif 4", "Georgia", serif;
          color: var(--ink);
          letter-spacing: -0.5px;
        }

        h1 { font-size: 2.4rem; }
        h2 { font-size: 1.6rem; }
        h3 { font-size: 1.2rem; }

        h3, .stSubheader, .stSubheader p,
        [data-testid="stSubheader"] {
          color: #1b62b3 !important;
        }

        .page-title {
          background: var(--title-bg);
          padding: 0.6rem 1rem;
          border-radius: 14px;
          margin-bottom: 0.8rem;
          width: 100%;
          box-sizing: border-box;
        }

        .stMarkdown p, .stMarkdown li {
          color: var(--ink);
          font-size: 1.1rem;
        }

        .stTextInput label, .stTextArea label, .stSelectbox label,
        .stFileUploader label, .stCheckbox label, .stSlider label {
          color: var(--muted);
          font-weight: 600;
        }

        .stTextInput input,
        .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"] > div,
        .stFileUploader div[data-testid="stFileUploaderDropzone"],
        [data-testid="stFileUploaderDropzone"] {
          background: var(--field-bg);
          border-radius: 10px;
        }

        [data-testid="stFileUploaderDropzone"] {
          border: 1px dashed #9ec7f7;
        }

        [data-testid="stButton"],
        [data-testid="stFormSubmitButton"] {
          display: flex;
          justify-content: center;
        }

        .stButton > button,
        button[kind="primary"],
        button[kind="secondary"],
        button[kind="tertiary"],
        [data-testid="stFormSubmitButton"] > button,
        [data-testid="baseButton-primary"],
        [data-testid="stButton"] > button,
        [data-testid="baseButton-primary"] button,
        [data-testid="baseButton-secondary"] button,
        [data-testid="stFileUploader"] button {
          background: #0b3d91 !important;
          color: #ffffff;
          border: 0;
          padding: 0.8rem 2.4rem;
          border-radius: 12px;
          font-weight: 700;
          min-width: 260px;
        }

        .stButton > button:hover,
        button[kind="primary"]:hover,
        button[kind="secondary"]:hover,
        button[kind="tertiary"]:hover,
        [data-testid="stFormSubmitButton"] > button:hover,
        [data-testid="baseButton-primary"]:hover,
        [data-testid="stButton"] > button:hover,
        [data-testid="baseButton-primary"] button:hover {
          background: #08336f !important;
          color: #ffffff;
        }

        [data-testid="stDownloadButton"] {
          display: flex;
          justify-content: center;
        }

        [data-testid="stFileUploader"] button {
          background: #1b62b3 !important;
          font-family: "Space Grotesk", "Segoe UI", "Trebuchet MS", sans-serif !important;
          font-size: 1rem !important;
          font-weight: 700 !important;
        }

        button[kind="secondary"],
        [data-testid="baseButton-secondary"] > button {
          background: var(--soft-button) !important;
          color: #0b3d91 !important;
          border: 1px solid #b9d7ff !important;
          padding: 0.5rem 1.2rem;
          min-width: auto;
          border-radius: 10px;
          font-weight: 700;
        }

        .stDownloadButton > button,
        [data-testid="stDownloadButton"] > button {
          background: #124c9a !important;
          color: #ffffff !important;
          border: 0;
          padding: 0.8rem 2.4rem;
          border-radius: 12px;
          font-weight: 700;
          min-width: 260px;
        }

        .stAlert, .stInfo {
          border-radius: 12px;
        }

        [data-testid="stForm"] {
          border: 1px solid #d9e9ff;
          border-radius: 16px;
          padding: 1rem 1.2rem;
          background: #ffffff;
          box-shadow: 0 6px 16px rgba(20, 44, 80, 0.05);
        }

        [data-testid="stExpander"] {
          border: 1px solid #d9e9ff;
          border-radius: 16px;
          background: #ffffff;
        }

        .section-card {
          border: 1px solid #d9e9ff;
          border-radius: 14px;
          padding: 0.8rem 1rem;
          margin: 0.6rem 0 1rem 0;
          background: #ffffff;
        }

        .block-container {
          padding-top: 2rem;
          max-width: 1100px;
        }

        [data-testid="stSidebar"] {
          background: var(--sidebar);
        }

        [data-testid="stSidebar"] * {
          color: var(--sidebar-dark);
        }

        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label {
          font-size: 1.05rem;
          font-weight: 600;
        }

        [data-testid="stSidebar"] h2 {
          font-family: "Source Serif 4", "Georgia", serif;
          font-size: 1.2rem;
          color: #0b3d91;
          margin: 0.6rem 0 0.2rem 0;
          letter-spacing: 0.3px;
          text-transform: uppercase;
        }

        [data-testid="stSidebar"] a {
          font-size: 1.08rem;
        }

        [data-testid="stSidebarNav"] {
          display: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_title(text: str) -> None:
    st.markdown(f'<div class="page-title"><h1>{text}</h1></div>', unsafe_allow_html=True)


def render_sidebar_nav(show_config: bool | None = None) -> None:
    if show_config is None:
        show_config = st.session_state.get("show_config_links", False)
    st.sidebar.page_link("Home.py", label="Home")
    st.sidebar.page_link("pages/0_Use_Case_Overview.py", label="Use Case Overview")
    st.sidebar.markdown("## Issuer")
    st.sidebar.page_link("pages/1_Issuance_General.py", label="Issuance — General QR")
    st.sidebar.page_link("pages/3_Issuance_with_Layers.py", label="Issuance with Layers")
    st.sidebar.page_link("pages/1b_Issuer_By_Role_Viewer.py", label="By-Role Viewer")

    st.sidebar.markdown("## Attester")
    st.sidebar.page_link("pages/2_Assertion_Overlay.py", label="Assertion — Overlay")
    st.sidebar.page_link("pages/4_Manifest_Attachment.py", label="Manifest Attachment")
    st.sidebar.page_link("pages/2b_Attester_Overlay_Viewer.py", label="Attester Viewer")

    st.sidebar.markdown("## Verifier")
    st.sidebar.page_link("pages/5_Trust_Verification.py", label="Trust Verification")
    st.sidebar.page_link("pages/6_Content_Viewer.py", label="Content Viewer")

    if show_config:
        st.sidebar.markdown("## Config")
        st.sidebar.page_link("pages/0_Config_Issuer.py", label="Issuer Schema")
        st.sidebar.page_link("pages/0_Config_Attester.py", label="Attester Schema")
