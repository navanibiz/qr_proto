import os
import sys
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ui.style import inject_style, page_title, render_sidebar_nav

st.set_page_config(page_title="IntentMark Suite", layout="centered")
inject_style()
page_title("IntentMark")

st.markdown("""
Welcome to the **IntentMark Platform**, a system that embeds layered data into visually standard QR codes.

---

### 🧭 IntentMark vision

IntentMark is a trust layer for QR codes that separates **public content**, **hidden access layers**, and **signed intent metadata**. It keeps the QR readable (no change to the fundamental QR) while enabling layered disclosure and verifiable issuer/attester intent using open standards (C2PA).

**Example use cases:**
- **Event access**: the same QR reveals different data to different roles (public, VIP, staff) without changing the visible QR.
- **Payments**: merchant publishes the QR; the POS/app adds an attestation layer to prove the device and context are legitimate.
- **High‑value assets**: public catalog info + issuer provenance + signed attestations for custody or transfers.
- **Identity & credentials**: show public ID details while authorized verifiers unlock hidden claims (roles, certifications).

### 🔍 What this platform does

- **Issuer**: generates the public General QR (also called L0 / layer 0) and (optionally) issuer-owned hidden layers.
- **Attester**: can add a **new hidden layer**, **signed metadata**, or **both** to attest intent and integrity.
- **Verifier**: checks trust signals (C2PA) and reveals only the layers they’re authorized to see.

This separation makes sense because QR codes are often **shared publicly** while trust and access control depend on **who is viewing and when**. In some use cases the issuer and attester are the **same party** (e.g., one organizer issues and signs conference tickets), while in others they are **different parties** (e.g., a merchant issues and a POS attests).

---

👉 Use the sidebar to:
- explore the **Issuer**, **Attester**, and **Verifier** sections to understand each role.
- experience the complete issuance → attestation → verification cycle.
- see how IntentMark elevates the QR experience with layered access and trust.
- future directions: NFC support and other credential carriers.
""")

col_left, col_right = st.columns([4, 1])
with col_right:
    config_on = st.session_state.get("show_config_links", False)
    label = "Config: On" if config_on else "Config: Off"
    button_type = "primary" if config_on else "secondary"
    if st.button(label, key="toggle_config", type=button_type):
        st.session_state["show_config_links"] = not st.session_state.get("show_config_links", False)
        st.rerun()

render_sidebar_nav(st.session_state.get("show_config_links", False))
