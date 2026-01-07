# IntentMark – Open Platform QR Trust Framework

*IntentMark is a screen-native, offline-verifiable, capability-based trust framework for machine-readable visual artifacts.*

---

## 1. Purpose and Design Goals

**IntentMark** defines a non-proprietary, ecosystem-friendly trust architecture for QR codes and similar visual machine-readable artifacts.

The framework is designed to:

* Avoid issuer lock-in or mandatory app control
* Support both **open** and **enforced** trust models
* Operate **offline-first** where required
* Remain backward-compatible with standard QR readers
* Allow incremental adoption across industries

At its core, IntentMark treats a QR code not merely as a locator, but as a **signed assertion of intent** whose trustworthiness depends on verifiable signals rather than reader identity alone.

---

## 2. Architectural Overview

The framework is composed of four strictly separated layers:

| Layer                    | Responsibility                           |
| ------------------------ | ---------------------------------------- |
| Visual Carrier           | Camera-readable symbol (standard QR)     |
| Optional Covert Capacity | Restricted or privileged data extraction |
| Provenance & Intent      | Issuer identity, policy, and claims      |
| Trust Resolution         | Reader-side evaluation and action        |

This separation ensures extensibility without forcing adoption of all components.

---

## 3. Visual Carrier Layer

### 3.1 Standard QR Encoding

* Generated using standard QR libraries
* Encodes a URI or structured payload
* Fully readable by any generic QR scanner

Examples:

* `https://example.com/verify`
* `ticket://event/EVT123`
* `pay://request?id=abc`

No custom symbology or proprietary encoding is required.

---

## 4. Optional Covert Capacity (Enforcement Extension)

IntentMark optionally supports **covert or restricted payload layers**, such as fractal-encoded tiles embedded within visually standard QR codes.

Characteristics:

* Screen-native only
* Visually indistinguishable from normal QR modules
* Decodable only by capable readers
* Used exclusively when enforcement or privilege separation is required

This layer is **not mandatory** and is never required for baseline compatibility.

### 4.1 Progressive Disclosure via Capability Layers

An IntentMark MAY include **multiple covert disclosure layers**, each independently encrypted and gated by a distinct capability requirement.

Each layer represents a progressively stronger or more privileged level of disclosure. Readers decode layers **sequentially** and MUST stop decoding when a layer cannot be validated.

Conceptually:

* Public QR payload (always readable)
* Covert Layer L1 (weak or signal-level capability)
* Covert Layer L2 (authorization or role-based capability)
* Covert Layer L3+ (high-assurance or hardware-backed capability)

Lower layers do not reveal information about higher layers, and failure to decode a layer must not leak sensitivity or layer count.

### 4.2 Layer Boundary Markers (LBM)

Covert layers MAY be separated by a **Layer Boundary Marker (LBM)**.

An LBM is a structural parsing aid that:

* Delimits covert payload layers
* Assists reader synchronization and alignment
* Indicates completion of the current layer

LBMs MUST NOT:

* Visually indicate privilege level
* Reveal the total number of layers
* Encode policy or sensitivity information

### 4.3 Key Derivation and Capability Gating

Each covert layer MUST be encrypted using a **layer-specific derived key**.

Keys are derived independently per layer using issuer-controlled secrets combined with contextual and capability-bound inputs, such as:

* Intent identifier
* Issuance metadata
* Capability claims (e.g., scopes, roles)
* Device or environment attestations (if required)

Readers that cannot derive or validate the required key for a given layer MUST treat decoding as complete and report the highest successfully validated disclosure level.

Progressive disclosure is an **enforcement extension** and does not alter baseline IntentMark compatibility.

---

## 5. Provenance and Intent Layer (C2PA)

### 5.1 Role of C2PA

C2PA is used as a **signed trust envelope**, binding issuer intent and policy to the visual artifact.

The manifest does not enforce behavior; it **declares expectations and constraints**.

### 5.2 Claims Typically Included

* Issuer identity and certificate chain
* Intended use (e.g., payment, ticketing, identity)
* Issuance timestamp and validity window
* Context hints (region, venue, environment)
* Visual integrity references (hashes)
* Declared trust requirements

### 5.3 Offline Operation

* Certificate chains may be cached
* Manifest verification does not require continuous network access
* Trust decisions are performed locally by the reader

---

## 10) Alignment with IntentMark Framework

The Fractal QR System is a **reference implementation** of the *IntentMark* framework’s **Optional Covert Capacity** and **Progressive Disclosure via Capability Layers**.

This section clarifies how the existing implementation maps to IntentMark concepts and identifies concrete refactors to bring the system into full alignment.

### 10.1 IntentMark Mapping

| Fractal QR Concept            | IntentMark Concept                 |
| ----------------------------- | ---------------------------------- |
| Public URL payload            | Public IntentMark payload          |
| Header tiles                  | Covert metadata (non-policy)       |
| Hidden protobuf sections      | Covert disclosure layers           |
| General / VIP / Staff / Admin | Capability-gated disclosure levels |
| RSA role keys                 | Capability-derived layer keys      |
| Recursive tile decoding       | Covert capacity decoding           |

The Fractal QR System SHOULD be described externally as an **IntentMark Covert Decoder**, not as a standalone QR variant.

---

### 10.2 Progressive Disclosure Refactor

Current implementation packs all hidden sections into a single compressed bitstream. To align with IntentMark:

* Hidden data SHOULD be split into **independent covert layers (L1, L2, L3…)**
* Each layer MUST:

  * Be encrypted independently
  * Have its own derived key
  * Be decodable without knowledge of higher layers

Recommended mapping:

* L1: Integrity / authenticity marker (weak or signal-only)
* L2: VIP / privileged event data
* L3: Staff or Admin-only operational data

Readers MUST stop decoding when a layer cannot be decrypted or validated and report the highest verified layer.

---

### 10.3 Layer Boundary Markers (LBM)

The existing use of header tiles and filler bits SHOULD be generalized into **Layer Boundary Markers (LBMs)**:

* LBMs delimit covert layers within the fractal bitstream
* LBMs assist synchronization and alignment
* LBMs MUST NOT encode role names, sensitivity, or layer count

LBMs replace implicit assumptions about tile ordering with explicit structural boundaries.

---

### 10.4 Capability-Based Keying Model

Role-based RSA keys SHOULD be abstracted into a **capability-based key derivation interface**, supporting:

* IAM-issued access tokens (JWT / OAuth2)
* Verifiable Credentials (VCs)
* Hardware-backed attestations (optional)

Conceptual derivation:

```
K_layer = KDF(K_root, intent_id, layer_id, capability_claims)
```

RSA MAY remain as an internal encryption primitive, but key selection MUST be capability-driven rather than role-hardcoded.

---

### 10.5 C2PA Integration (Planned)

The Fractal QR System does not currently authenticate the public payload or header.

To align with IntentMark:

* A C2PA manifest SHOULD be generated at encode time
* The manifest SHOULD:

  * Declare issuer identity
  * Bind visual hashes to the rendered QR
  * Declare accepted capability proofs
  * Declare whether covert layers are present

Manifest verification SHOULD occur before covert decoding.

---

### 10.6 Updated Non-Goals (Clarified)

The following remain **explicit non-goals** of the Fractal QR System:

* Perfect steganographic invisibility
* Defense against nation-state adversaries
* Mandatory app-level enforcement

The system is designed for **progressive trust resolution**, not absolute secrecy.

---

### 10.8 Optional Binding Between C2PA and Covert Capacity

When both **C2PA manifests** and **Optional Covert Capacity** are present, the system MAY cryptographically bind the two to strengthen integrity guarantees while preserving backward compatibility.

These bindings are **optional**, additive, and do not change baseline QR readability.

#### Option A: Manifest Commitment to Covert Layers (One-Way)

* The issuer computes a cryptographic commitment (e.g., hash or Merkle root) over the covert layers.
* This commitment is embedded as a claim in the C2PA manifest.
* A verifier that can decode covert layers recomputes the commitment and compares it against the manifest.

This option provides tamper-evidence when covert content is readable.

---

#### Option B: Covert Layer Pointer to Manifest (One-Way)

* A designated covert layer (typically L1) embeds a digest or identifier of the C2PA manifest.
* The verifier checks that the decoded covert layer references the active manifest.

This option prevents mix-and-match attacks between unrelated manifests and covert payloads.

---

#### Option C: Mutual Binding (Two-Way Commitment)

* The C2PA manifest includes a commitment to covert layers.
* A covert layer embeds a digest of the C2PA manifest.

Any substitution or recombination of either component invalidates verification.

---

#### Option D: Manifest-Bound Key Derivation

* Layer encryption keys are derived using a Key Derivation Function (KDF) that incorporates the manifest digest.

Example:

```
K_layer = KDF(K_root, intent_id, layer_id, manifest_digest, capability_claims)
```

If the manifest is altered or replaced, covert layers cannot be decrypted.

---

#### Option E: Privacy-Preserving Proof of Covert Presence

* Covert layers are hashed into a Merkle tree.
* Only the Merkle root is embedded in the C2PA manifest.
* Verifiers may validate individual layers using Merkle proofs without learning:

  * the number of layers
  * layer sizes
  * semantic meaning of other layers

This option supports progressive disclosure without leaking structure.

---

These binding mechanisms MAY be used independently or in combination. Implementations SHOULD treat them as enforcement extensions rather than mandatory requirements.

---

### 10.9 Cryptographic Considerations

IntentMark deliberately separates **cryptographic strength** from **covert data volume**. The architecture ensures that stronger cryptography (including elliptic-curve or post-quantum algorithms) does not materially increase QR payload size.

#### 10.9.1 Cryptographic Role Separation

IntentMark distinguishes between three cryptographic roles:

* **Symmetric encryption**: used for encrypting covert payload layers
* **Asymmetric / post-quantum cryptography**: used for signing, key agreement, and capability proofs
* **Key derivation**: used to derive per-layer symmetric keys without transporting keys

Only **symmetric ciphertext** appears inside covert layers.

---

#### 10.9.2 Symmetric Encryption for Covert Layers

* Covert layers MUST use authenticated symmetric encryption (e.g., AES-GCM, ChaCha20-Poly1305).
* Encryption overhead is constant (e.g., IV + authentication tag) and independent of algorithm strength.
* Post-quantum safety of symmetric encryption is preserved without increasing payload size.

As a result, upgrading cryptographic strength does not increase covert capacity requirements.

---

#### 10.9.3 Use of Elliptic Curve and Post-Quantum Cryptography

* Elliptic-curve cryptography (ECC) and post-quantum cryptography (PQC) MAY be used for:

  * signing C2PA manifests
  * verifying issuer authenticity
  * capability proofs and attestations
* Such cryptographic material SHOULD NOT be embedded in covert payload layers.

Larger key sizes or signatures (e.g., PQC) affect only manifest size or verifier-side state, not QR covert capacity.

---

#### 10.9.4 Manifest-Bound Key Derivation

IntentMark RECOMMENDS deriving covert layer keys using contextual inputs rather than embedding encrypted keys.

Example:

```
K_layer = KDF(K_root, intent_id, layer_id, manifest_digest, capability_claims)
```

This approach:

* avoids transporting public keys or certificates
* keeps key material off the QR
* ensures cryptographic agility without format changes

---

#### 10.9.5 Cryptographic Agility and Future-Proofing

IntentMark is designed to be cryptographically agile:

* Symmetric encryption remains stable across generations
* Asymmetric and post-quantum algorithms may evolve independently
* QR payload formats do not change as cryptography is upgraded

This mirrors proven patterns used in TLS and modern secure messaging systems.

---

#### 10.9.6 Explicit Anti-Patterns

Implementations SHOULD avoid:

* embedding certificates or public keys inside covert layers
* embedding asymmetric or post-quantum signatures in covert payloads
* per-layer asymmetric encryption
* transporting encrypted symmetric keys within the QR

These practices unnecessarily increase payload size and reduce robustness.

## Design Rationale: Covert Layers and Progressive Disclosure

### Purpose of Layers

In IntentMark, covert layers are **not merely a way to increase QR data capacity**.  
They serve three simultaneous purposes:

1. **Capacity Expansion** — enabling a single QR to carry more data than a standard payload
2. **Disclosure Boundaries** — enforcing cryptographic separation between data of different sensitivity
3. **Progressive Trust Resolution** — allowing verifiers to stop at the highest layer they are authorized to validate

This combination allows one visual artifact to support multiple verification contexts without duplication.

---

### Layers Are Not Roles

Covert layers **do not map one-to-one to roles** (e.g., “doctor layer”, “pharmacist layer”).

Instead, layers map to **data sensitivity tiers and assurance levels**.

Access to a layer is determined by:
- verifier capability (e.g., authorization credentials)
- verifier assurance level (e.g., attestation)
- issuer-defined policy

This avoids role explosion and keeps the system extensible.

---

### Conceptual Model

Each covert layer can be viewed as a **cryptographically sealed compartment** within the QR:

- Each layer is encrypted independently
- Each layer has its own access policy
- Decryption failure at any layer halts further disclosure (“stop-on-failure”)

All layers may be present in the artifact, but only some may be accessible to a given verifier.

---

### Example: Healthcare Context (Illustrative)

| Layer | Data Sensitivity Tier | Example Contents | Typical Access |
|------|----------------------|------------------|----------------|
| Public | Contextual | “Health credential presentation” | Anyone |
| L1 | Low sensitivity, high utility | Allergies, blood type | Most medical verifiers |
| L2 | Clinical | Conditions, medications | Licensed clinicians |
| L3 | Regulated | Prescriptions, dispensing rules | Licensed pharmacists |
| L4 | Administrative | Billing or coverage proofs | Authorized payers |

A single verifier may be authorized to access **non-contiguous layers** (e.g., L1 + L3).

---

### Layers vs. Selective Disclosure

While SSI systems support selective disclosure, covert layers add value by enabling:

- **Screen-native, scan-only verification**
- **Offline progressive disclosure**
- **Pre-packaged disclosure tiers**
- **Clear verifier UX boundaries**

Layers complement SSI proofs rather than replacing them.

---

### What Layers Are — and Are Not

**Layers are:**
- A structured way to embed multiple disclosure tiers
- Enforced by cryptography, not UI convention
- Compatible with offline and constrained environments

**Layers are not:**
- Merely a storage hack
- Hardcoded role partitions
- A replacement for credential issuance or revocation

---

### Summary

In IntentMark, covert layers provide a mechanism to combine **capacity, policy, and privacy** in a single QR artifact.  
They allow different verifiers to see different truths—**without changing the artifact itself**—based solely on what the verifier can legitimately prove.
