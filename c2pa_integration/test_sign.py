import argparse
import io
import os
from typing import Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa


def load_private_key(path: str):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def sign_callback_for_key(private_key):
    if isinstance(private_key, rsa.RSAPrivateKey):
        def _sign(data: bytes) -> bytes:
            return private_key.sign(
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
        return _sign, "PS256"
    if isinstance(private_key, ec.EllipticCurvePrivateKey):
        def _sign(data: bytes) -> bytes:
            return private_key.sign(data, ec.ECDSA(hashes.SHA256()))
        return _sign, "ES256"
    raise RuntimeError("Unsupported private key type.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal C2PA signing test.")
    parser.add_argument("--in", dest="input_path", required=True, help="Input PNG")
    parser.add_argument("--out", dest="output_path", required=True, help="Output signed PNG")
    parser.add_argument("--cert", required=True, help="Cert chain PEM")
    parser.add_argument("--key", required=True, help="Private key PEM")
    args = parser.parse_args()

    try:
        from c2pa import Builder, C2paSigningAlg, Signer
    except Exception as exc:
        print(f"[ERROR] c2pa import failed: {exc}")
        return 1

    with open(args.input_path, "rb") as f:
        image_bytes = f.read()
    with open(args.cert, "rb") as f:
        cert_chain = f.read().decode("utf-8")

    private_key = load_private_key(args.key)
    sign_cb, alg_str = sign_callback_for_key(private_key)
    signing_alg = getattr(C2paSigningAlg, alg_str)

    manifest = {
        "title": os.path.basename(args.input_path),
        "format": "image/png",
        "claim_generator_info": [
            {"name": "qr_proto", "version": "0.1.0"}
        ],
        "assertions": [
            {
                "label": "c2pa.actions",
                "data": {
                    "actions": [
                        {
                            "action": "c2pa.created",
                            "softwareAgent": {
                                "name": "qr_proto",
                                "version": "0.1.0",
                            },
                        }
                    ]
                },
            }
        ],
    }

    signer = Signer.from_callback(
        callback=sign_cb,
        alg=signing_alg,
        certs=cert_chain,
        tsa_url=None,
    )

    builder = Builder(manifest)
    result = io.BytesIO()
    builder.sign(signer, "image/png", io.BytesIO(image_bytes), result)

    with open(args.output_path, "wb") as f:
        f.write(result.getvalue())

    print(f"✅ Signed file written to {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
