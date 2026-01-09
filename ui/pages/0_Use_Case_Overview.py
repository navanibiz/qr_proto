import os
import sys
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ui.style import inject_style, page_title, render_sidebar_nav

st.set_page_config(page_title="Use Case Overview", layout="centered")
inject_style()
render_sidebar_nav()
page_title("Use Case Overview")

st.markdown("""
IntentMark supports layered disclosure and trust signals across multiple verification paths:

**Layering paths**
- **General only**: public QR data for anyone to read.
- **Issuer layers**: VIP/Staff/Admin layers that unlock with issuer keys.
- **Attester overlay**: a separate layer added after issuance for device/context attestation.

**Verification paths**
- **Content view**: decode layers based on role.
- **Trust view**: verify signed metadata (C2PA) without revealing hidden layers.
- **Combined**: validate trust + reveal authorized content.

**Common flows**
- Issuer issues General QR → issuer roles decode hidden layers.
- Attester appends overlay → attester decodes their layer only.
- Verifier checks signed metadata → admits/denies.
""")
