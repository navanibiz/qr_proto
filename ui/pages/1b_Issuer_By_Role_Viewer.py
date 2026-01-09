import os
import sys
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ui.style import inject_style, page_title, render_sidebar_nav
from ui.viewer_shared import render_viewer

st.set_page_config(page_title="Issuer — By-Role Viewer", layout="centered")
inject_style()
render_sidebar_nav()
page_title("Issuer — By-Role Viewer")
st.markdown("Preview what different issuer roles can see from the same QR. Attester signals are shown but not decrypted.")

render_viewer(
    role_options=["General", "VIP", "Staff", "Admin"],
    default_role="General",
    button_label="🔍 Decode by Role",
    show_presence_checks=True,
    presence_title="Attester Signals (Visibility Only)",
)
