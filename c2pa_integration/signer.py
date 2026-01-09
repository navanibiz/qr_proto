import io
import json
from typing import Any, Dict, Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa


_C2PA_IMPORT_ERROR = None


def is_c2pa_available() -> bool:
    try:
        import c2pa  # noqa: F401
        return True
    except Exception as exc:
        global _C2PA_IMPORT_ERROR
        _C2PA_IMPORT_ERROR = str(exc)
        return False
def get_c2pa_import_error() -> str | None:
    return _C2PA_IMPORT_ERROR


def sign_png_with_c2pa(
    *,
    input_png_bytes: bytes,
    manifest_payload: Dict[str, Any],
    cert_path: str,
    key_path: str,
    output_path: Optional[str] = None,
) -> bytes:
    """
    Signs and embeds a C2PA manifest into the PNG bytes.
    Falls back to raising a RuntimeError if c2pa-python isn't installed.
    """
    try:
        from c2pa import Builder, C2paSigningAlg, Signer
    except Exception as exc:
        raise RuntimeError(
            "c2pa-python import failed. "
            f"Details: {exc}"
        ) from exc

    manifest_json = json.dumps(manifest_payload, separators=(",", ":"), sort_keys=True)

    with open(cert_path, "rb") as f:
        cert_chain_bytes = f.read()
    cert_chain = cert_chain_bytes.decode("utf-8")
    with open(key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    certs = []
    try:
        certs = x509.load_pem_x509_certificates(cert_chain_bytes)
    except Exception:
        try:
            certs = [x509.load_pem_x509_certificate(cert_chain_bytes)]
        except Exception:
            certs = []

    cert_chain_for_signing = cert_chain

    print(f"[C2PA] Loaded certs: {len(certs)}")
    for i, cert in enumerate(certs):
        print(f"[C2PA] Cert[{i}] subject={cert.subject.rfc4514_string()} issuer={cert.issuer.rfc4514_string()}")

    if isinstance(private_key, rsa.RSAPrivateKey):
        def sign_callback(data: bytes) -> bytes:
            return private_key.sign(
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
        signing_alg = C2paSigningAlg.PS256
    elif isinstance(private_key, ec.EllipticCurvePrivateKey):
        def sign_callback(data: bytes) -> bytes:
            return private_key.sign(
                data,
                ec.ECDSA(hashes.SHA256()),
            )
        signing_alg = C2paSigningAlg.ES256
    else:
        raise RuntimeError("Unsupported private key type for C2PA signing.")

    if certs:
        leaf_pub = certs[0].public_key()
        key_matches = leaf_pub.public_numbers() == private_key.public_key().public_numbers()
        print(f"[C2PA] Leaf cert matches private key: {key_matches}")
        print(f"[C2PA] Signing alg: {signing_alg}")
        print(f"[C2PA] Embedded chain cert count: {len(certs)}")

    signer = Signer.from_callback(
        callback=sign_callback,
        alg=signing_alg,
        certs=cert_chain_for_signing,
        tsa_url=None,
    )

    builder = Builder(manifest_json)
    result = io.BytesIO()
    builder.sign(signer, "image/png", io.BytesIO(input_png_bytes), result)
    signed_bytes = result.getvalue()

    if output_path:
        with open(output_path, "wb") as f:
            f.write(signed_bytes)

    return signed_bytes
