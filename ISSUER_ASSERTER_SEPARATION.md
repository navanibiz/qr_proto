# Issuer–Asserter Separation (MVP Direction)

This document describes the **issuer–asserter split** and its implications for the Fractal QR system.

## 1) Concept
- **Issuer**: creates the **public L0 QR** and may add issuer-owned hidden layers.
- **Asserter**: adds **additional overlays** and/or a **C2PA manifest** to attest intent and integrity.
- These can be **different parties** or the **same party** (issuer=asserter).

## 2) Why split?
- Real-world flows often separate **content generation** from **assertion/signing**.
- Issuers might not control attestation keys (compliance, security, or regulatory reasons).
- Asserters can add trust after the fact without reissuing the public QR.

## 3) What changes in the system
### 3.1 Schema split
- Two JSON schemas:
  - `schema/issuer_schema.json`
  - `schema/asserter_schema.json`
- Each schema owns its layers and key paths.

### 3.2 Capacity reservation
- Issuer QR sizing **reserves capacity** for asserter layers.
- This prevents re-issuing the L0 QR when assertions are added later.
- When the asserter needs more capacity or depth, it should send an **assertion request** back to the issuer so a new QR is issued with enough reserved room.

### 3.3 Key ownership
- Issuer and asserter use **separate keys**.
- For MVP, keys are local file paths but modeled as distinct.

## 4) MVP assumptions
- Same data types and number of layers are fixed.
- Keys are local but distinct by owner.
- Depth is encoded in the header so the asserter can decode/append overlays reliably.

## 5) Implications
- **Verification**: a QR may be valid (L0) but untrusted until an asserter manifest exists.
- **UX**: verification UI must handle “no manifest” gracefully.
- **Security**: the presence of a manifest is an **issuer/asserter trust signal**, not a guarantee.

## 6) Future direction
- Allow **dynamic layers** per owner.
- Support key management via external vaults or KMS.
- Add explicit **ownership metadata** in the header and C2PA claims.
