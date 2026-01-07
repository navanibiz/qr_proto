# Why IntentMark Exists — Novelty and Importance

## 1. Executive Summary

IntentMark exists to address a **structural trust gap** in how QR codes are used today.

Modern QR codes are widely used to initiate **high‑impact actions**—payments, access control, identity verification—yet they lack any native ability to declare intent, prove provenance, or enforce disclosure boundaries. As a result, users and applications are forced to **infer meaning and trust after the fact**, creating systemic vulnerability.

IntentMark introduces a new class of artifact: a **self‑describing, verifiable, intent‑aware visual code** that enables safer, clearer, and more controlled interactions—without modifying the QR standard or underlying systems.

---

## 2. The Problem: QR Codes as Blind Action Triggers

A QR code today is effectively an **unlabeled executable input**:

* It initiates an action when scanned
* The action may be irreversible (payment, access, disclosure)
* The user often does not know *what will happen* until after scanning

Unlike other interfaces:

* Software binaries are signed
* Web links show domains and permissions
* Identity proofs declare scope and purpose

QR codes do none of these.

This is not a user‑education failure—it is a **design omission**.

---

## 3. Why Existing Approaches Fall Short

Current mitigations treat symptoms rather than the root cause.

### 3.1 Backend Validation

* Occurs after scan
* Requires connectivity
* Too late for many scams or misuse cases

### 3.2 App‑Level Heuristics

* Non‑deterministic
* Inconsistent across apps
* Easily bypassed by social engineering

### 3.3 Multiple QRs or Role‑Specific Codes

* Operationally complex
* Leaks structure and intent
* Poor user experience

### 3.4 Interactive SSI Flows

* Require protocol handshakes
* Wallet‑dependent
* Not scan‑only or universal

None of these approaches give the QR artifact itself **agency or intent**.

---

## 4. What Does Not Exist Today

There is currently no widely deployed system that provides all of the following:

1. **Explicit, verifiable intent declaration** for a QR‑initiated action
2. **Offline‑verifiable provenance** for a QR code
3. **Progressive, access‑controlled disclosure** within a single QR artifact
4. **Verifier‑side policy enforcement** based on cryptographic proof

Notably:

* QR standards do not support disclosure layers
* C2PA is not used for QR codes
* Existing systems assume trust is resolved server‑side

IntentMark is designed specifically to fill this gap.

---

## 5. Intent as a First‑Class Property

IntentMark treats intent as **explicit, signed data**, not an inferred side‑effect.

An IntentMark artifact can declare:

* what kind of action it is intended to initiate
* what constraints apply (time, scope, context)
* how a verifier should behave if verification is partial or fails

This allows scanners to make **deterministic decisions** rather than guesses.

---

## 6. Provenance Without Changing QR

IntentMark pairs an unmodified QR code with a **cryptographic provenance manifest**.

Key properties:

* The QR image itself is not altered
* Provenance is expressed via signed metadata
* Verification can occur offline

This model mirrors how content authenticity is handled for media, but applies it to **transactional visual artifacts**, which has not been done before.

---

## 7. Progressive Disclosure Within a Single Artifact

IntentMark enables a single QR to contain **multiple encrypted disclosure tiers**, each independently accessible based on verifier capability.

Important characteristics:

* Layers are ordered by data sensitivity, not by role
* Each layer is cryptographically sealed
* Verifiers stop at the highest layer they can validate

This allows:

* minimal disclosure by default
* stronger assurance when needed
* one artifact to serve many contexts

This capability does not exist in current QR systems.

---

## 8. Verifier‑Side Enforcement (A Key Shift)

Most QR systems assume that:

* trust is resolved by a backend, or
* the issuer controls access at scan time

IntentMark shifts enforcement to the **verifier**, based on what the verifier can prove:

* authorization credentials
* assurance level (e.g., attestation)
* local policy

This enables:

* offline enforcement
* graded trust outcomes (allow / warn / escalate / deny)
* clearer accountability

---

## 9. Why This Matters for High‑Impact Use Cases

### High‑Value Events

* Prevents silent tier leakage
* Reduces staff confrontation
* Enables quiet escalation paths

### QR‑Based Payments

* Makes payment intent explicit before action
* Reduces ambiguity exploited in scams
* Enables deterministic warnings or blocks

In both cases, the problem is not lack of encryption, but **lack of declared intent and trust semantics**.

---

## 10. Nature of the Novelty

IntentMark’s novelty lies in the **combination** of ideas, not any single component:

* QR as a visual carrier
* Intent declaration as signed data
* Provenance applied to transactional artifacts
* Progressive disclosure within one code
* Verifier‑side capability enforcement

Each element exists elsewhere; their integration into a single, screen‑native system does not.

---

## 11. Why This Is Durable

IntentMark’s value does not depend on:

* a specific payment rail
* a specific identity framework
* changes to QR standards

It addresses a persistent boundary problem: **how humans safely initiate actions from visual cues**.

As long as QR codes are used to trigger real‑world consequences, this gap remains.

---

## 12. Summary

IntentMark is important because it turns QR codes from **blind action triggers** into **self‑describing, verifiable trust artifacts**.

It introduces intent, provenance, and controlled disclosure at the exact point where ambiguity is currently exploited—without breaking compatibility or requiring new standards.

This makes IntentMark not just a feature, but a **new trust primitive for visual interactions**.
