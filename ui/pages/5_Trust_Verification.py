import os
import sys
import streamlit as st

# Ensure project root is on sys.path for local imports.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from c2pa_integration import verify_png_with_c2pa
from ui.style import inject_style, page_title, render_sidebar_nav


st.set_page_config(page_title="Ticket Verifier", layout="centered")
inject_style()
render_sidebar_nav()
page_title("✅ Ticket Verifier")
st.caption("Validates signed metadata using C2PA.")

st.markdown("Upload a ticket PNG with signed metadata to verify issuer authenticity and intent.")

trust_store_dir = st.text_input("Trust store directory", "c2pa_integration/trust_store")
img_file = st.file_uploader("Upload signed PNG", type=["png"])

if img_file:
    png_bytes = img_file.getvalue()
    result = verify_png_with_c2pa(png_bytes, trust_store_dir=trust_store_dir)

    st.subheader("Verification Result")
    summary_rows = [
        {"Field": "Status", "Value": result.get("status", "unknown")},
        {"Field": "Manifest Present", "Value": result.get("manifest_present", "unknown")},
        {"Field": "Validation State", "Value": result.get("validation_state", "unknown")},
        {"Field": "Assertions", "Value": ", ".join(result.get("assertions", []))},
    ]
    st.table(summary_rows)
    with st.expander("Show Raw JSON"):
        st.json(result)

    summary = result.get("summary", [])
    explanations = result.get("explanations", [])
    if summary:
        st.subheader("Summary")
        for line in summary:
            st.markdown(f"- {line}")
    reason = result.get("reason")
    if reason:
        st.info(reason)
    if explanations:
        st.subheader("Checks")
        for item in explanations:
            code = item.get("code", "check")
            text = item.get("explanation", "")
            st.markdown(f"- {code}: {text}")

    status = result.get("status")
    decision = "Warn"
    if status == "valid":
        decision = "Admit"
    elif status in ("invalid", "error"):
        decision = "Deny"

    st.markdown(f"**Decision:** {decision}")
