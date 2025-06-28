import streamlit as st

st.set_page_config(page_title="Fractal QR Code Suite", layout="centered")

st.title("🌀 Fractal QR Code System")
st.markdown("""
Welcome to the **Fractal QR Code Platform**, a system that embeds layered data into visually standard QR codes using fractal tiling.

---

### 🔍 Features
            
- **Generate** new QR codes for events with encrypted hidden sections using Protobuf + fractal rendering.
- **Scan** QR codes to extract layered content based on your access level (General, VIP, Staff, Admin).
- **Role-based Access** ensures only authorized viewers can see sensitive info.

---

👉 Use the sidebar to:
- Create new event QR codes on the **Event Coordinator** page (if implemented).
- Decode QR codes on the **QR Scanner** page.
""")
