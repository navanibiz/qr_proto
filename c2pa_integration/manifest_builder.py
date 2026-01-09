import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def compute_sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compute_commitments(
    image_bytes: bytes,
    public_payload: str,
    hidden_payload_bytes: bytes,
) -> Dict[str, str]:
    return {
        "image_sha256": compute_sha256_hex(image_bytes),
        "l0_payload_sha256": compute_sha256_hex(public_payload.encode("utf-8")),
        "hidden_payload_sha256": compute_sha256_hex(hidden_payload_bytes),
    }


def build_manifest_payload(
    *,
    issuer_name: str,
    intent: str,
    event_id: str,
    ticket_id: str,
    valid_from: str,
    valid_to: str,
    commitments: Dict[str, str],
    issued_at: Optional[str] = None,
) -> Dict[str, Any]:
    issued = issued_at or _iso_now()
    intent_payload = {
        "issuer": issuer_name,
        "intent": intent,
        "event_id": event_id,
        "ticket_id": ticket_id,
        "issued_at": issued,
        "valid_from": valid_from,
        "valid_to": valid_to,
        "commitments": commitments,
    }

    return {
        "title": f"{event_id}:{ticket_id}",
        "format": "image/png",
        "claim_generator_info": [
            {
                "name": "qr_proto",
                "version": "0.1.0",
            }
        ],
        "assertions": [
            {
                "label": "c2pa.actions",
                "data": {
                    "actions": [
                        {
                            "action": "c2pa.created",
                            "when": issued,
                            "softwareAgent": {
                                "name": "qr_proto",
                                "version": "0.1.0",
                            },
                            "digitalSourceType": (
                                "http://cv.iptc.org/newscodes/"
                                "digitalsourcetype/digitalCreation"
                            ),
                        }
                    ]
                },
            },
            {
                "label": "com.qr_proto.intent",
                "data": intent_payload,
            },
        ],
    }


def manifest_to_json(manifest_payload: Dict[str, Any]) -> str:
    return json.dumps(manifest_payload, separators=(",", ":"), sort_keys=True)
