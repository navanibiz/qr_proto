import os
import sys
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ui.style import inject_style, page_title, render_sidebar_nav
from ui.viewer_shared import render_viewer

st.set_page_config(page_title="Attester — Viewer", layout="centered")
inject_style()
render_sidebar_nav()
page_title("Attester — Viewer")
st.markdown("Verify attester overlays and signed metadata without exposing issuer-only sections.")

render_viewer(
    role_options=["Asserter"],
    default_role="Asserter",
    button_label="🔍 Decode Attester Overlay",
    show_role_select=False,
    show_presence_checks=True,
    presence_title="Attester Signals",
)
