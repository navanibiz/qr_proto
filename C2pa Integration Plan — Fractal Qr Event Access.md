# C2PA Integration Plan — Fractal QR Event Access (PNG + Streamlit)

This design doc describes how to integrate **C2PA** into the existing **Fractal QR** system for the **event access** use case, using **PNG** artifacts and a **Streamlit** issuer/verifier UI.

> **One-sentence framing:** C2PA turns each Fractal QR ticket image into a **signed, verifiable artifact** that declares *who issued it* and *what it is intended to do*, enabling **Admit / Warn / Deny** decisions **before** access is granted.

---

## 0) Reference implementation

Use these as the primary references:

* `c2pa-python` (library): [https://github.com/contentauth/c2pa-python](https://github.com/contentauth/c2pa-python)
* `c2pa-python-example` (reference app): [https://github.com/contentauth/c2pa-python-example](https://github.com/contentauth/c2pa-python-example)

The example repo is useful as a working pattern for: **manifest construction → signing → attaching to an asset → verification**.

---

## 1) Context: Current Fractal QR implementation (what exists)

The existing system already supports:

* **Visible layer (L0):** URL payload containing base64 JSON (general event fields)
* **Hidden layers:** protobuf sections (VIP/Staff/Admin), zlib-compressed, embedded into fractal tiles
* **Role-based decoding:** decrypt VIP/Staff/Admin fields after bitstream extraction
* **Streamlit UI:** encode/decode flows are already present

Known gaps relevant to provenance:

* Public payload integrity not authenticated
* No issuer authenticity / provenance bound to the image
* No standardized verification path (especially useful for auditors / third-party verifiers)

---

## 2) Goals

### 2.1 MVP goals

* Attach a **C2PA signed manifest** to the **final ticket PNG**.
* Provide **offline-verifiable** authenticity at scan time (verifier trusts a local certificate store).
* Encode minimally necessary public claims:

  * issuer identity
  * intent = `event_access_admit`
  * `event_id`, `ticket_id`
  * validity window
  * integrity commitments (hashes)
* Integrate into existing **Streamlit** pages:

  * Issue (Generate + Sign)
  * Verify (Upload + Validate)

### 2.2 Non-goals (for MVP)

* Full PKI lifecycle, certificate transparency, or enterprise revocation systems
* Cross-issuer federation between independent ticketing platforms
* NFC support (Phase 2)

---

## 3) System model

### 3.1 Canonical artifact

The **PNG image** produced by the Fractal QR encoder is the **source of truth**.

It contains:

* L0 QR modules
* fractal tiles encoding hidden payload
* embedded C2PA manifest (JUMBF)

### 3.2 Trust roles

* **Issuer:** event organizer (or their platform) that signs the ticket image
* **Verifier:** gate scanner (Streamlit verifier today; mobile scanner later)
* **Trust store:** verifier’s local store of accepted issuer certificate(s)

---

## 4) What goes into C2PA vs layers

### 4.1 Public claims (C2PA manifest — interoperable)

These should be readable and verifiable by *any* verifier:

* `intent`: `event_access_admit`
* `event_id`
* `ticket_id`
* `issued_at`
* `valid_from`, `valid_to`
* `issuer` identity (via signing certificate)

### 4.2 Integrity commitments (recommended)

Commit to hashes so the verifier can detect tampering/substitution:

* `image_sha256`: hash of the final PNG bytes
* `l0_payload_sha256`: hash of the visible payload (decoded URI string or canonical payload bytes)
* `hidden_payload_sha256`: hash of the compressed hidden bitstream (or per-role hashes)

> Note: These commitments let a verifier detect changes even if it cannot decode issuer-private layers.

### 4.3 Hidden layers remain issuer-private (capability-gated)

Your VIP/Staff/Admin layers remain:

* decodable only by authorized verifiers
* encrypted as you currently do

C2PA does not need to expose their contents; it only optionally binds their integrity.

---

## 5) Issuance flow (Generate → Hash → Manifest → Sign → Embed)

### 5.1 Inputs

* Event data (JSON)
* Role payloads (VIP/Staff/Admin)
* Issuer credential:

  * signing cert + private key (local file for MVP)

### 5.2 Steps

1. Build protobuf `Event` from input JSON.
2. Strip VIP/Staff/Admin from public JSON.
3. Render Fractal QR image (existing pipeline) → `ticket.png`.
4. Compute commitments:

   * `image_sha256(ticket.png bytes)`
   * `l0_payload_sha256(canonical_l0_payload)`
   * `hidden_payload_sha256(compressed_hidden_bytes)`
5. Build C2PA manifest with:

   * intent + identifiers + validity
   * integrity commitments
6. Use `c2pa-python` to:

   * sign the manifest
   * embed it into the PNG
7. Output:

   * `ticket_signed.png` (canonical distributable)
   * optional `manifest_debug.json` (for audit/dev)

---

## 6) Verification flow (Verify → Read claims → Decide)

### 6.1 Inputs

* Uploaded/scanned PNG (`ticket_signed.png`)
* Local trust store (issuer certs)

### 6.2 Steps

1. Use `c2pa-python` `Reader` to:

   * detect manifest presence
   * validate signature
   * validate issuer is trusted
   * extract claims
2. Evaluate claims:

   * intent must match `event_access_admit`
   * must be within validity window
   * event_id must match current event (scanner-config)
3. (Optional) Validate integrity commitments:

   * verify `image_sha256` matches
   * verify `hidden_payload_sha256` matches recomputed value (if decoded)
4. Resolve outcome:

   * **ALLOW (Admit):** valid signature + valid claims
   * **WARN:** missing manifest or unknown issuer
   * **DENY:** invalid signature/tampered/expired/wrong event

---

## 7) Streamlit UI plan

### 7.1 Page A — Issue Ticket (Generate + Sign)

* Input: event JSON + optional VIP/Staff/Admin fields
* Buttons:

  * **Generate Fractal QR** (existing)
  * **Attach C2PA + Sign** (new)
* Outputs:

  * Preview: unsigned vs signed
  * Download: `ticket_signed.png`
  * Debug panel: extracted claims (optional)

### 7.2 Page B — Verify Ticket

* Upload PNG
* Show:

  * Manifest: present/missing
  * Signature: valid/invalid
  * Issuer: trusted/untrusted
  * Intent + validity: pass/fail
  * Final decision: **Admit/Warn/Deny**
* Optional: decode hidden layers by role and show decoded fields

---

## 8) Code changes (recommended structure)

Add a new package:

* `c2pa_integration/`

  * `manifest_builder.py` — builds the manifest payload and custom assertions
  * `signer.py` — signs + embeds manifest into PNG
  * `verifier.py` — reads + verifies manifest and returns structured results
  * `trust_store/` — PEM certs for accepted issuers

Touch points:

* `main.py.encode_from_dict(...)`

  * add `sign_c2pa: bool = False`
  * add `issuer_profile` (path to cert/key, issuer name)
* Streamlit pages

  * new “Attach C2PA + Sign” button
  * new Verify page/tab

---

## 9) Credential model (MVP)

### 9.1 MVP

* Local issuer keypair + certificate
* Stored on issuer machine/server only
* Verifier ships with issuer certificate(s)

### 9.2 Later

* Move signing key to KMS/HSM
* Certificate rotation per event

---

## 10) Testing plan

### 10.1 Unit tests

* Manifest construction (fields present, expected values)
* Signing/embedding round-trip
* Verification failure cases

### 10.2 Golden fixtures

* `ticket_signed_depth1.png`, `ticket_signed_depth2.png`
* Tamper cases:

  * modified pixel region
  * replaced visible payload
  * manifest stripped

### 10.3 End-to-end

* Issue ticket → verify → decode layers → decision

---

## 11) Open questions

* Confirm PNG attach/write support in the chosen `c2pa-python` version.
* Decide how strict hash checks should be under screenshots/resizes.
* Decide Warn vs Deny policy for missing C2PA in different event tiers.
* Whether to add a sidecar manifest export for audit.
