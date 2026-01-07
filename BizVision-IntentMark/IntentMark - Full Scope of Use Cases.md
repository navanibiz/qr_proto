# IntentMark – The Full Scope of Use Cases

> **Context: QR codes are already ubiquitous and growing**

Public industry data shows that QR codes are now a *normalized interaction surface* across consumer, enterprise, and public infrastructure:

* QR usage accelerated sharply post‑pandemic and continues to grow globally
* Hundreds of millions of users scan QR codes regularly via native phone cameras
* QR codes are embedded across marketing, payments, hospitality, retail, logistics, healthcare, transport, and entertainment

A useful public snapshot of this scale and trend is maintained by QRCodeChimp:

* [https://www.qrcodechimp.com/qr-code-statistics/](https://www.qrcodechimp.com/qr-code-statistics/)

This matters because **IntentMark does not introduce a new interface** — it strengthens an interface that already sits at massive scale.

---

**How IntentMark applies across human and AI-driven QR interactions**

---

## Scope Clarification: Digital‑First QR Scanning (Let’s Be Honest)

IntentMark is **not** claiming to secure every QR code in every physical context.

Some of IntentMark’s strongest capabilities — such as provenance binding, progressive disclosure, covert layers, and AI‑agent interpretation — **work best when the QR is presented digitally**:

* on screens (phones, kiosks, terminals)
* inside apps
* on devices, robots, or machines
* within digital workflows (emails, dashboards, wallets)

### Why digital‑first matters

When a QR is digitally displayed:

* the visual artifact can be integrity‑bound to metadata
* the display context (device, app, session) can be trusted
* AI agents can safely interpret intent before acting
* replay, screenshot, and relay risks can be mitigated

By contrast, **purely printed QRs**:

* are easier to tamper with or replace
* lose display-context guarantees
* limit enforcement of advanced IntentMark features

### Image as the Source of Truth (QR + Layers + C2PA)

IntentMark treats the **QR image itself as the primary artifact**.

That image may include:

* the visible QR
* optional layered / covert data
* optional embedded C2PA metadata

**That image is the source of truth.**

When the image is **printed**:

* layered or covert data may be lost
* metadata may be stripped
* visual fidelity may degrade

👉 This is **acceptable and expected**.

### Role of the NFC Adjunct (Print-Only Recovery)

The NFC tag’s role is deliberately minimal and **only required in print-QR scenarios**.

The NFC tag’s **only job** is to store:

> **the canonical digital IntentMark image (or a compact, lossless representation of it)**

This enables:

* recovery of layers and metadata lost during printing
* integrity-preserving rehydration of the original artifact
* consistent verification across scan, tap, and share

Importantly:

* if the QR is **naturally shared digitally** (image file, app, wallet, screen)
* the NFC adjunct is **not required at all**

In effect:

* **Digital sharing = full fidelity by default**
* **Printed QR = visual handle**
* **NFC = optional digital fidelity anchor**

No secrets, wallets, or logic are stored on the tag.

This keeps the system:

* cheap
* battery-free
* resilient
* compatible with existing printable NFC cards and tags

IntentMark does not rely on the printed medium to be perfect — it relies on the **image being recoverable when needed**.
(QR + Layers + C2PA)

IntentMark treats the **QR image itself as the primary artifact**.

That image may contain:

* the visible QR
* optional covert / layered data
* optional embedded C2PA metadata

When the image is **printed**, some of this information (layers, metadata) may be lost or degraded. That is expected and acceptable.

### Role of the NFC Adjunct

The NFC tag does **not** need to hold secrets, wallets, or logic. It only needs to hold:

> **The canonical IntentMark image file (or a compact, lossless representation of it)**

This enables:

* full recovery of layers and metadata
* integrity-preserving rehydration of the original artifact
* consistent verification whether scanned, tapped, or shared

In effect:

* **Print = human-visible affordance**
* **NFC = digital fidelity anchor**

### Practical Implications

* Printing may discard advanced features — this is fine
* Tapping NFC restores the full digital artifact
* Saving or sharing the image digitally preserves full IntentMark capability
* No large payloads are required; the image remains compact

This keeps the system:

* cheap
* battery-free
* resilient
* compatible with existing NFC cards and tags

IntentMark does not rely on the printed medium to be perfect — it relies on the **image being recoverable when needed**.

In real-world use, QR codes are often **shared as images** — screenshots, photos, message attachments, or embedded files. This is acceptable for IntentMark **as long as the image file remains reasonably small**.

Key points:

* Standard QR images (PNG/JPEG/WebP) are compact and widely supported
* IntentMark does **not** depend on large or high-resolution images
* Core intent and provenance data remain lightweight
* Rich or sensitive data stays off-image (manifest resolution, NFC adjunct, verifier-side logic)

This keeps IntentMark compatible with:

* messaging apps

* email attachments

* document embeds

* low-bandwidth or constrained environments

* are easier to tamper with or replace

* lose display‑context guarantees

* limit enforcement of advanced IntentMark features

### What this means in practice

IntentMark is **most effective** when:

* the QR represents something valuable
* the action is high‑impact or irreversible
* the scan happens in a digital or semi‑digital context

Examples:

* digital payments and wallet flows
* login, pairing, and authorization screens
* AI agent instructions and identity presentation
* tickets, passes, and credentials shown on devices
* machine, robot, or kiosk identity surfaces

Printed QRs can still benefit from **basic intent declaration and provenance**, but IntentMark is intentionally optimized for the **digital sharing and screen‑native future**.

This focus keeps IntentMark:

* realistic
* deployable today
* aligned with where QR usage is already moving

---

## Core Idea

QR codes are no longer just shortcuts to websites. They are now used to:

* move money
* grant physical access
* unlock digital accounts
* trigger workflows
* identify people, machines, and AI agents

As QR usage scales, **the cost of unclear intent scales with it**.

IntentMark addresses this growing gap by making intent, provenance, and disclosure explicit *at scan time* — before action occurs.

Whether scanned by a **human** or an **AI agent**, a QR code is increasingly:

> **A trigger for something valuable to change hands**

Value may be money, access, authority, control, data, time, or safety.

IntentMark exists to remove ambiguity **before** action is taken.

---

# PART A: NON‑AI (HUMAN‑SCANNED) SITUATIONS

These are already mainstream, high-volume, and high-risk.

---

## 1. Payments & Monetary Exchange

### Example situations

* Scan to pay at a store or restaurant
* QR on invoices or emails
* Tips, donations, refunds
* Loyalty or voucher redemption

### What goes wrong today

* Fake payment QRs
* Redirection to wrong accounts
* Hidden amounts or recipients

### IntentMark mapping

**Must-have features**

* Explicit intent declaration (payment request)
* Issuer provenance (who created it)
* Offline-verifiable signature
* Validity window / expiry

**Nice-to-have features**

* Progressive disclosure (amount, invoice hash)
* Context binding (merchant, location)
* Scanner-side warnings or blocks

---

## 2. Physical Access (Tickets, Buildings, Transport)

### Example situations

* Event tickets
* Office or campus entry
* Boarding passes
* Parking access

### What goes wrong today

* Screenshot reuse
* Forwarded QRs
* Over-disclosure of staff or security data
* Gate disputes

### IntentMark mapping

**Must-have features**

* Declared access intent (entry / boarding)
* Issuer identity
* Time-bound validity
* Offline verification

**Nice-to-have features**

* Progressive disclosure (attendee vs staff)
* Silent escalation paths for security
* Contextual enforcement (time, gate)

---

## 3. Digital Access & Login

### Example situations

* Device pairing
* Account login
* App or service activation
* Private group invitations

### What goes wrong today

* Phishing via fake login QRs
* Users unaware of permissions granted
* Session hijacking

### IntentMark mapping

**Must-have features**

* Explicit login / pairing intent
* Issuer provenance
* Scope declaration (what is being linked)

**Nice-to-have features**

* Progressive disclosure of permissions
* Device or environment binding

---

## 4. Identity & Credential Presentation

### Example situations

* ID checks
* Age or eligibility proof
* Membership verification
* Education or work credentials

### What goes wrong today

* Oversharing
* Fake credentials
* Verifier uncertainty

### IntentMark mapping

**Must-have features**

* Declared identity intent
* Signed issuer claims
* Offline verification

**Nice-to-have features**

* Progressive disclosure of attributes
* Verifier-side policy enforcement

---

## 5. Consent & Data Sharing

### Example situations

* KYC onboarding
* Surveys
* Health or financial data capture

### What goes wrong today

* Users unaware of data scope
* Consent without clarity

### IntentMark mapping

**Must-have features**

* Explicit consent intent
* Declared data categories
* Issuer provenance

**Nice-to-have features**

* Time-limited consent
* Layered data disclosure

---

# PART B: AI‑SCANNED / AI‑ASSISTED SITUATIONS

These are growing rapidly and amplify risk due to automation speed.

---

## 6. Delegated Authority to AI Agents

### Example situations

* Approving workflows
* Authorizing transactions
* Granting permissions

### What goes wrong today

* AI executes unclear or overbroad authority
* No human “gut check”

### IntentMark mapping

**Must-have features**

* Explicit authorization intent
* Declared scope and limits
* Signed provenance

**Nice-to-have features**

* Agent-side refusal or escalation rules
* Audit-friendly intent logs

---

## 7. Triggering Autonomous Actions

### Example situations

* Refunds or reversals
* Account onboarding
* Credential rotation

### What goes wrong today

* QR becomes a silent remote trigger

### IntentMark mapping

**Must-have features**

* Action-class declaration
* Verifier-side policy hooks

**Nice-to-have features**

* Context-aware gating
* Rate or replay limits

---

## 8. Robotics, Industrial & Physical Systems

### Example situations

* Warehouse robots
* Maintenance systems
* Industrial equipment

### What goes wrong today

* Confusing inspection vs control
* Safety incidents

### IntentMark mapping

**Must-have features**

* Explicit control vs observe intent
* Offline verification
* Hardware-compatible trust

**Nice-to-have features**

* Progressive privilege layers
* Safety-bound refusal modes

---

## 9. Smart Buildings, Vehicles & Infrastructure

### Example situations

* Smart parking
* HVAC systems
* Autonomous shuttles

### What goes wrong today

* Temporary instructions mistaken as permanent

### IntentMark mapping

**Must-have features**

* Contextual intent declaration
* Time and location binding

**Nice-to-have features**

* Cross-system trust consistency

---

## 10. AI Configuration & Behavior Control

### Example situations

* Model or policy switching
* Tool access changes
* Prompt or mode updates

### What goes wrong today

* Visual prompt injection
* Undetected behavior changes

### IntentMark mapping

**Must-have features**

* Declared configuration intent
* Signed issuer identity

**Nice-to-have features**

* Human-in-the-loop enforcement
* Capability-based gating

---

# Summary Table (Mental Model)

| QR Scan Leads To | IntentMark Is Critical When…   |
| ---------------- | ------------------------------ |
| Money            | Funds can move                 |
| Access           | Someone or something can enter |
| Authority        | Decisions are approved         |
| Control          | Devices or systems act         |
| Data             | Sensitive info is shared       |
| Automation       | AI acts without pause          |

---

## 11. Marketing, Information & Low-Risk Discovery (What IntentMark *Does* and *Does Not* Target)

### Why this category matters

QR codes are everywhere for **discovery and convenience**, not just high-risk actions. This includes:

* Marketing campaigns
* Product information
* Museum guides
* Menus
* Recipes, games, puzzles
* Virtual tours (real estate, travel)

These uses are **not inherently dangerous**, but they still benefit from clarity and provenance.

### Example situations

* Product packaging linking to brand sites
* Flyers and billboards linking to promotions or reviews
* Museum exhibits linking to audio guides
* Sustainable clothing or food traceability pages
* Digital menus in hospitality

### What goes wrong today

* Brand impersonation via fake QRs
* Malicious redirects from physical locations
* Users unsure if a QR is “safe” to scan

### IntentMark mapping

**Must-have features**

* Explicit low-risk intent declaration (information / marketing)
* Issuer provenance (brand or institution)
* Visual-to-manifest integrity binding

**Nice-to-have features**

* Reputation signals for scanners
* Analytics without tracking abuse
* Progressive disclosure for richer content

**Important clarification**
IntentMark does **not** aim to over-secure playful or low-stakes QRs. Its role here is:

> *Clarity, authenticity, and trust — not friction.*

---

## 12. Logistics, Inventory & Supply Chain

### Example situations

* Manufacturing and warehouse tracking
* Asset identification
* Shipment status linking
* Cold-chain monitoring

### What goes wrong today

* Label swapping
* Counterfeit goods
* Loss of provenance

### IntentMark mapping

**Must-have features**

* Declared tracking / identification intent
* Issuer and chain-of-custody provenance
* Offline verification

**Nice-to-have features**

* Progressive disclosure (public vs internal data)
* Integration with audit and compliance systems

---

## 13. Authentication & Certification

### Example situations

* Degree certificates
* Professional licenses
* Training credentials
* Compliance documents

### What goes wrong today

* Fake certificates
* Verifier confusion
* Over-sharing personal data

### IntentMark mapping

**Must-have features**

* Explicit authentication intent
* Signed issuer claims
* Offline verification

**Nice-to-have features**

* Layered disclosure of attributes
* Verifier-side policy enforcement

---

## 14. Gaming, Crypto & Metaverse (High-Value Digital Worlds)

These domains combine **money, identity, access, and automation**, making them especially sensitive to unclear QR intent.

---

### 14.1 Gaming (Online, Mobile, AR)

#### Example situations

* Claiming in-game rewards
* Redeeming promo codes
* Linking game accounts
* Entering tournaments or private servers
* AR games triggered by physical locations

#### What goes wrong today

* Fake reward QRs stealing accounts
* Players tricked into linking wallets or accounts
* Exploits via unofficial QR drops

#### IntentMark mapping

**Must-have features**

* Explicit gaming intent (reward, login, link, entry)
* Issuer provenance (game studio / publisher)
* Scope declaration (what is being granted)

**Nice-to-have features**

* Progressive disclosure (cosmetic vs competitive rewards)
* Anti-replay and time-bound claims
* Reputation signals for community-created QRs

---

### 14.2 Crypto & Web3

#### Example situations

* Wallet connection QRs
* Signing transactions
* NFT minting or claiming
* Airdrops and staking
* DAO voting

#### What goes wrong today

* Malicious wallet-drain QRs
* Users signing transactions they don’t understand
* Fake airdrops and phishing

#### IntentMark mapping

**Must-have features**

* Explicit transaction / signing intent
* Clear declaration of action type (sign vs transfer)
* Issuer or contract provenance

**Nice-to-have features**

* Progressive disclosure (gas fees, contract risks)
* Wallet-side policy enforcement
* Human-readable intent summaries for agents

---

### 14.3 Metaverse & Virtual Worlds

#### Example situations

* Entering virtual spaces or events
* Claiming virtual land or assets
* Linking physical locations to virtual twins
* Granting moderator or creator rights

#### What goes wrong today

* Impersonation of official spaces
* Accidental granting of admin privileges
* Loss of valuable digital assets

#### IntentMark mapping

**Must-have features**

* Explicit access or ownership intent
* Issuer provenance (platform or creator)
* Time and context binding

**Nice-to-have features**

* Progressive disclosure of privileges
* Cross-world identity consistency

---

## 15. AI Agent Identity & Delegated Trust (A New Identity Class)

As AI agents act autonomously, they increasingly need to **identify themselves**, prove authority, and respect boundaries. QR codes are emerging as a **lightweight identity and delegation surface** between humans, agents, and systems.

---

### 15.1 AI Agent Identity ("Who is acting?")

#### Example situations

* An AI agent identifying itself to a human or system
* A robot or assistant presenting its identity on a screen
* An agent proving it belongs to a specific organization or user

#### What goes wrong today

* Humans cannot tell *which* agent is acting
* Agents spoof each other
* No portable, scan-friendly way to verify agent provenance

#### IntentMark mapping

**Must-have features**

* Explicit identity intent ("AI agent identity presentation")
* Signed issuer or owner provenance
* Offline-verifiable claims

**Nice-to-have features**

* Reputation or trust tier signals
* Time-bound or session-bound identity

---

### 15.2 Delegation of Authority to AI Agents ("Who may act?")

#### Example situations

* Granting an agent permission to spend money
* Allowing an agent to access systems or data
* Temporarily empowering an agent during a task

#### What goes wrong today

* Over-broad permissions
* No clear boundary on scope or duration
* Hard to revoke or audit

#### IntentMark mapping

**Must-have features**

* Explicit delegation intent
* Declared scope, limits, and duration
* Issuer-signed delegation claims

**Nice-to-have features**

* Progressive disclosure of authority
* Verifier-side enforcement by agents and systems

---

### 15.3 Agent-to-Agent Trust & Handoffs

#### Example situations

* One agent handing off a task to another
* Multi-agent workflows across vendors
* AI services interacting across trust boundaries

#### What goes wrong today

* No shared trust vocabulary
* Broken accountability chains
* Blind acceptance of tasks

#### IntentMark mapping

**Must-have features**

* Explicit handoff intent
* Signed provenance of the originating agent
* Capability-based acceptance rules

**Nice-to-have features**

* Audit-friendly intent chains
* Cross-agent trust policies

---

### 15.4 Human ↔ AI Identity Boundary

#### Example situations

* Human verifying an agent before approving actions
* Agent verifying a human before accepting instructions

#### What goes wrong today

* Humans trust "the interface", not the actor
* Agents trust inputs without provenance

#### IntentMark mapping

**Must-have features**

* Declared interaction intent (human approval, AI execution)
* Mutual provenance verification

**Nice-to-have features**

* Human-readable summaries of agent intent
* Escalation or refusal modes

---

## 16. Physical AI Identity (Robots, Machines, Embodied Agents)

As AI moves into the physical world, **identity is no longer abstract**. Robots, machines, vehicles, kiosks, and smart infrastructure increasingly need to *present who they are* in a way that humans and other machines can quickly verify.

QR codes displayed on screens, panels, or devices are becoming a **practical identity surface** for physical AI.

---

### 16.1 Physical AI Identifying Itself to Humans

#### Example situations

* A delivery robot presenting its identity at a building entrance
* A service robot asking for elevator access
* A hospital robot identifying itself to staff
* A public kiosk or smart machine showing a QR for verification

#### What goes wrong today

* Humans cannot tell if a machine is legitimate
* Spoofed or rogue devices appear identical
* Trust is based on branding or uniforms, not cryptographic proof

#### IntentMark mapping

**Must-have features**

* Explicit physical-AI identity intent ("robot identity presentation")
* Signed manufacturer / operator provenance
* Offline-verifiable identity claims

**Nice-to-have features**

* Human-readable identity summary
* Session- or task-bound identity refresh

---

### 16.2 Physical AI Requesting Access or Cooperation

#### Example situations

* A robot requesting entry to a secure area
* An autonomous vehicle requesting gate access
* A machine requesting maintenance mode

#### What goes wrong today

* Over-trusting devices based on appearance
* Manual overrides without accountability

#### IntentMark mapping

**Must-have features**

* Explicit access or cooperation intent
* Declared scope and duration
* Signed operator authorization

**Nice-to-have features**

* Progressive disclosure (operator vs security)
* Silent escalation paths

---

### 16.3 Machine-to-Machine Identity & Trust

#### Example situations

* Robots coordinating in warehouses
* Industrial machines handing off tasks
* Smart infrastructure interacting autonomously

#### What goes wrong today

* Implicit trust on networks
* Weak or static identifiers

#### IntentMark mapping

**Must-have features**

* Explicit machine identity intent
* Signed provenance and capability claims

**Nice-to-have features**

* Capability-based trust negotiation
* Audit-friendly interaction logs

---

### 16.4 Physical–Digital Boundary Enforcement

#### Example situations

* Physical robot triggering digital workflows
* Digital approval unlocking physical actions

#### What goes wrong today

* Broken accountability between physical and digital systems

#### IntentMark mapping

**Must-have features**

* Declared cross-boundary intent
* Verifier-side enforcement

**Nice-to-have features**

* Context-aware safety gating
  n

---

## 17. NFC Wristbands & Wearables (Healthcare as a Canonical Example)

NFC wristbands are already widely deployed in **hospitals, events, and secure facilities**. They provide a durable, low-friction, always-on identity surface that aligns naturally with IntentMark’s print-plus-NFC model.

---

### 17.1 Hospital Patient Identification

#### Example situations

* Patient check-in and bed assignment
* Medication administration
* Lab sample tracking
* Movement across departments

#### What goes wrong today

* Barcode-only wristbands lose context
* Backend lookups required for meaning
* Overexposure of patient data

#### IntentMark mapping

**Must-have features**

* Explicit identity intent ("patient identity presentation")
* Signed issuer provenance (hospital or health system)
* Offline-verifiable identity and status claims

**Nice-to-have features**

* Progressive disclosure (nurse vs doctor vs admin)
* Time- or episode-bound identity scopes

---

### 17.2 Consent, Treatment & Workflow Triggers

#### Example situations

* Consent confirmation before procedures
* Treatment or medication verification
* AI-assisted workflow routing

#### What goes wrong today

* Ambiguous confirmation flows
* Human error under time pressure

#### IntentMark mapping

**Must-have features**

* Explicit consent or workflow intent
* Scope and validity declaration

**Nice-to-have features**

* Human-readable summaries
* AI-side refusal or escalation rules

---

### 17.3 Why Wristbands Matter Strategically

NFC wristbands demonstrate that:

* **identity does not require phones or screens**
* passive, wearable artifacts scale well
* physical presence and digital intent can coexist

With IntentMark:

* the **printed QR** provides universal visual access
* the **NFC wristband** preserves the canonical digital image when print degrades

This makes healthcare a **canonical proof point** for IntentMark’s physical–digital trust model.

---

As AI moves into the physical world, **identity is no longer abstract**. Robots, machines, vehicles, kiosks, and smart infrastructure increasingly need to *present who they are* in a way that humans and other machines can quickly verify.

QR codes displayed on screens, panels, or devices are becoming a **practical identity surface** for physical AI.

---

### 16.1 Physical AI Identifying Itself to Humans

#### Example situations

* A delivery robot presenting its identity at a building entrance
* A service robot asking for elevator access
* A hospital robot identifying itself to staff
* A public kiosk or smart machine showing a QR for verification

#### What goes wrong today

* Humans cannot tell if a machine is legitimate
* Spoofed or rogue devices appear identical
* Trust is based on branding or uniforms, not cryptographic proof

#### IntentMark mapping

**Must-have features**

* Explicit physical-AI identity intent ("robot identity presentation")
* Signed manufacturer / operator provenance
* Offline-verifiable identity claims

**Nice-to-have features**

* Human-readable identity summary
* Session- or task-bound identity refresh

---

### 16.2 Physical AI Requesting Access or Cooperation

#### Example situations

* A robot requesting entry to a secure area
* An autonomous vehicle requesting gate access
* A machine requesting maintenance mode

#### What goes wrong today

* Over-trusting devices based on appearance
* Manual overrides without accountability

#### IntentMark mapping

**Must-have features**

* Explicit access or cooperation intent
* Declared scope and duration
* Signed operator authorization

**Nice-to-have features**

* Progressive disclosure (operator vs security)
* Silent escalation paths

---

### 16.3 Machine-to-Machine Identity & Trust

#### Example situations

* Robots coordinating in warehouses
* Industrial machines handing off tasks
* Smart infrastructure interacting autonomously

#### What goes wrong today

* Implicit trust on networks
* Weak or static identifiers

#### IntentMark mapping

**Must-have features**

* Explicit machine identity intent
* Signed provenance and capability claims

**Nice-to-have features**

* Capability-based trust negotiation
* Audit-friendly interaction logs

---

### 16.4 Physical–Digital Boundary Enforcement

#### Example situations

* Physical robot triggering digital workflows
* Digital approval unlocking physical actions

#### What goes wrong today

* Broken accountability between physical and digital systems

#### IntentMark mapping

**Must-have features**

* Declared cross-boundary intent
* Verifier-side enforcement

**Nice-to-have features**

* Context-aware safety gating

---

## Why Physical AI Identity Needs IntentMark

Physical AI:

* acts in shared human spaces
* creates safety and liability risks
* must be trusted *at a glance*

IntentMark provides a **screen-native, scan-first identity and intent layer** that:

* works offline
* is human-verifiable
* is machine-verifiable
* does not require new hardware standards

---

## Why AI Agent Identity Changes Everything

AI agents are not just tools — they are **actors**. Once they:

* control resources
* make decisions
* interact with the world

identity, intent, and delegation become inseparable.

IntentMark provides a **screen-native, scan-first identity and delegation primitive** that works:

* offline
* across vendors
* for humans *and* machines

---

## Reframing the "QR Everywhere" Reality

QR codes already bridge the **physical and digital world across nearly every industry**:

* Retail
* Healthcare
* Transport
* Logistics
* Marketing
* Entertainment

**IntentMark does not replace QR usage** — it adds a missing semantic layer:

> *What is this QR intended to do, and under what conditions should it be trusted?*

IntentMark becomes critical as soon as a QR:

* moves money
* grants access
* shares sensitive data
* triggers automation
* or represents authority

---

## One-Line Summary

> **IntentMark turns QR codes from silent triggers into explicit, verifiable instructions—safe for humans and AI alike.**

---

*This document is designed to be reused as a blog series, deck outline, or product explainer with minimal modification.*
