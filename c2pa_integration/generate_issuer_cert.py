import argparse
import os
from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID


def _generate_private_key(alg: str):
    if alg == "rsa":
        return rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return ec.generate_private_key(ec.SECP256R1())


def build_chain(
    common_name: str,
    days_valid: int,
    alg: str,
    country: str,
    state: str,
    locality: str,
    organization: str,
    org_unit: str,
) -> tuple[bytes, bytes, bytes, bytes]:
    sig_alg = hashes.SHA256()
    ca_key = _generate_private_key(alg)
    intermediate_key = _generate_private_key(alg)
    leaf_key = _generate_private_key(alg)

    def subject_with_cn(cn: str, org_name: str) -> x509.Name:
        attrs = [
            x509.NameAttribute(NameOID.COUNTRY_NAME, country),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state),
            x509.NameAttribute(NameOID.LOCALITY_NAME, locality),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, org_name),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, org_unit),
            x509.NameAttribute(NameOID.COMMON_NAME, cn),
        ]
        return x509.Name(attrs)

    root_subject = subject_with_cn(f"{common_name} Root CA", f"{organization} Root CA")
    intermediate_subject = subject_with_cn(
        f"{common_name} Intermediate CA",
        f"{organization} Intermediate CA",
    )
    leaf_subject = subject_with_cn(common_name, organization)

    now = datetime.now(timezone.utc)

    root_cert_builder = (
        x509.CertificateBuilder()
        .subject_name(root_subject)
        .issuer_name(root_subject)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=days_valid))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()),
            critical=False,
        )
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
            critical=False,
        )
    )
    root_cert = root_cert_builder.sign(ca_key, sig_alg)

    intermediate_cert_builder = (
        x509.CertificateBuilder()
        .subject_name(intermediate_subject)
        .issuer_name(root_cert.subject)
        .public_key(intermediate_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=days_valid))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(intermediate_key.public_key()),
            critical=False,
        )
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
            critical=False,
        )
    )
    intermediate_cert = intermediate_cert_builder.sign(ca_key, sig_alg)

    leaf_cert_builder = (
        x509.CertificateBuilder()
        .subject_name(leaf_subject)
        .issuer_name(intermediate_cert.subject)
        .public_key(leaf_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=days_valid))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=True,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.EMAIL_PROTECTION]),
            critical=True,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(leaf_key.public_key()),
            critical=False,
        )
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(intermediate_key.public_key()),
            critical=False,
        )
    )
    leaf_cert = leaf_cert_builder.sign(intermediate_key, sig_alg)

    root_pem = root_cert.public_bytes(serialization.Encoding.PEM)
    intermediate_pem = intermediate_cert.public_bytes(serialization.Encoding.PEM)
    leaf_pem = leaf_cert.public_bytes(serialization.Encoding.PEM)
    leaf_key_pem = leaf_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return leaf_pem, intermediate_pem, root_pem, leaf_key_pem


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a self-signed issuer cert/key for C2PA demos."
    )
    parser.add_argument("--cn", default="Example Event Org", help="Common Name")
    parser.add_argument("--days", type=int, default=365, help="Validity in days")
    parser.add_argument(
        "--alg",
        choices=["ec", "rsa"],
        default="ec",
        help="Key algorithm (default: ec/ES256)",
    )
    parser.add_argument("--country", default="US", help="Country code")
    parser.add_argument("--state", default="CA", help="State or province")
    parser.add_argument("--locality", default="Somewhere", help="Locality")
    parser.add_argument("--org", default="Example Org", help="Organization name")
    parser.add_argument("--org-unit", default="FOR TESTING_ONLY", help="Org unit")
    parser.add_argument(
        "--out-dir",
        default="c2pa_integration/trust_store",
        help="Output directory for cert/key",
    )
    parser.add_argument(
        "--cert-name",
        default="issuer_cert.pem",
        help="Certificate filename",
    )
    parser.add_argument(
        "--key-name",
        default="issuer_private_key.pem",
        help="Private key filename",
    )
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    leaf_pem, intermediate_pem, root_pem, key_pem = build_chain(
        args.cn,
        args.days,
        args.alg,
        args.country,
        args.state,
        args.locality,
        args.org,
        args.org_unit,
    )

    cert_path = os.path.join(args.out_dir, args.cert_name)
    ca_path = os.path.join(args.out_dir, "root_ca.pem")
    intermediate_path = os.path.join(args.out_dir, "intermediate_ca.pem")
    key_path = os.path.join(args.out_dir, args.key_name)

    with open(cert_path, "wb") as f:
        f.write(leaf_pem + intermediate_pem)
    with open(ca_path, "wb") as f:
        f.write(root_pem)
    with open(intermediate_path, "wb") as f:
        f.write(intermediate_pem)
    with open(key_path, "wb") as f:
        f.write(key_pem)

    print(f"✅ Wrote cert: {cert_path}")
    print(f"✅ Wrote CA:   {ca_path}")
    print(f"✅ Wrote ICA:  {intermediate_path}")
    print(f"✅ Wrote key:  {key_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
