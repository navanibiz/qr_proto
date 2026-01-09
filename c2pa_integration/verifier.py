from typing import Any, Dict
import os
import tempfile

from .signer import is_c2pa_available


def verify_png_with_c2pa(png_bytes: bytes, trust_store_dir: str) -> Dict[str, Any]:
    """
    Verifies a C2PA manifest embedded in the PNG.
    Returns structured results for UI consumption.
    """
    if not is_c2pa_available():
        return {
            "status": "unavailable",
            "reason": "c2pa-python is not installed",
        }

    try:
        from c2pa import Reader
        from c2pa import c2pa as c2pa_internal
    except Exception as exc:
        return {"status": "error", "reason": f"c2pa import failed: {exc}"}

    if trust_store_dir and os.path.isdir(trust_store_dir):
        try:
            c2pa_internal.load_settings({
                "trust": {
                    "trust_store_path": trust_store_dir
                }
            })
        except Exception as exc:
            return {"status": "error", "reason": f"load_settings failed: {exc}"}

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "ticket.png")
        with open(path, "wb") as f:
            f.write(png_bytes)
        try:
            reader = Reader(path)
        except Exception as exc:
            return {
                "status": "missing",
                "manifest_present": False,
                "reason": f"Manifest not found: {exc}",
                "summary": [
                    "No C2PA manifest found in the image.",
                    "A signed manifest is a signal the QR was issued by an authorized vendor."
                ],
                "explanations": [],
            }
        manifest = reader.get_active_manifest()
        validation_state = reader.get_validation_state()
        validation_results = reader.get_validation_results()

    result = {
        "status": "unknown",
        "manifest_present": manifest is not None,
        "assertions": [],
        "validation_state": validation_state,
        "validation_results": validation_results,
        "summary": [],
        "explanations": [],
    }

    if manifest is None:
        result["status"] = "missing"
        return result

    if validation_state:
        normalized_state = validation_state.strip().lower()
        result["status"] = "valid" if normalized_state == "valid" else "invalid"

    # Human-friendly explanations for common validation codes.
    code_explanations = {
        "claimSignature.insideValidity": "Signature time is within the certificate validity window.",
        "claimSignature.validated": "Signature is cryptographically valid.",
        "assertion.hashedURI.match": "Manifest references match the embedded content.",
        "assertion.dataHash.match": "Data hash matches the signed payload.",
    }

    try:
        success_items = validation_results.get("activeManifest", {}).get("success", [])
        for item in success_items:
            code = item.get("code", "")
            explanation = code_explanations.get(code, item.get("explanation", ""))
            result["explanations"].append(
                {"code": code, "explanation": explanation}
            )
    except Exception:
        pass

    if result["status"] == "valid":
        result["summary"].append("Signature and manifest integrity checks passed.")
    elif result["status"] == "invalid":
        result["summary"].append("Signature or manifest integrity checks failed.")

    try:
        assertions = manifest.get("assertions", [])
        result["assertions"] = [a.get("label") for a in assertions if isinstance(a, dict)]
    except Exception:
        pass

    return result
