import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_key_pair(role):
    os.makedirs("keys", exist_ok=True)  # ✅ Ensure 'keys/' exists

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    
    with open(f"keys/{role}_private.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(f"keys/{role}_public.pem", "wb") as f:
        f.write(private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

# Generate keys
generate_key_pair("vip")
generate_key_pair("staff")
generate_key_pair("asserter")
