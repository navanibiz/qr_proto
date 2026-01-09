import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ui.style import inject_style, page_title, render_sidebar_nav
from ui.viewer_shared import render_viewer

st.set_page_config(page_title="Content Viewer", layout="centered")
inject_style()
render_sidebar_nav()
page_title("📄 Content Viewer — QR Scanner")

render_viewer(
    role_options=["General", "VIP", "Staff", "Asserter", "Admin"],
    default_role="General",
    button_label="🔍 Decode and Show My Event Info",
)
