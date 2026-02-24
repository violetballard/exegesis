# Collaboration 2.0 Spec

## Goal

- Add realtime editing for text documents (sections/memos/notes) with end-to-end encryption.
- Keep 1.0 DVCS layer as durable history:
  - realtime produces live state
  - periodic snapshots become signed commits (audit-friendly)
- Server remains a relay/persistence layer for encrypted deltas, not a trusted editor.

## Non-Goals

- Realtime editing for PDFs (sync as blobs via 1.0).
- Server-side plaintext indexing or conflict resolution.
- Infinite-document CRDT for entire dissertation; use section-level CRDT.

## A) Realtime Scope

Realtime applies to:
- section text files
- comments/annotations
- presence (who is editing)
- optional: shared cursor/selection (nice-to-have)

Not realtime:
- PDFs, large binaries
- export
- model runs (those remain artifacts/patches)

## B) Document Model (CRDT per section)

- Each editable document (for example, section) is represented as a CRDT state.
- Choose a proven text CRDT:
  - `Yjs` is the practical default if JS in the realtime layer is acceptable, or
  - a Rust/Swift-native CRDT for deeper integration later.
- Store CRDT updates as encrypted deltas.
- Periodic compaction:
  - snapshot CRDT state to reduce delta replay cost
  - snapshot is also encrypted

## C) Group Crypto (E2EE messaging)

Requirements:
- authenticated devices
- forward secrecy (preferably)
- membership changes (add/remove)
- replay protection
- message integrity

Recommended approach:
- MLS-style group messaging (ideal) OR
- pragmatic v1: per-project session keys rotated periodically + per-message nonces + signatures

Key components:
- Project Identity: device public keys + membership list
- Session Key(s): used to encrypt realtime messages (separate from DVCS PDK if desired)
- On membership changes:
  - rotate session keys
  - optionally rotate DVCS PDK for future commits (ties into 1.0 rotation)

## D) Realtime Server Role (dumb relay + optional storage)

Server does:
- authenticate user/device
- authorize project membership
- relay encrypted messages over WebSockets
- optionally persist encrypted deltas for offline catch-up

Server does NOT:
- decrypt messages
- resolve conflicts
- inspect document content

## E) Realtime Protocol (high-level)

Client connects:
- WS connect with device auth
- join project channel
- join document channel(s)

Message types (all encrypted payloads):
- `presence_update`
- `crdt_update` (delta)
- `crdt_snapshot` (compressed state)
- `ack` / `receipt` (optional)
- `key_update` (on rotation)

Ordering:
- CRDT tolerates out-of-order; still track sequence numbers to optimize.

Offline catch-up:
- server can provide last-known delta sequence since client watermark
- all deltas encrypted; server just stores blobs

## F) Bridging to DVCS (1.0): snapshots into commits

Commit strategy:
- Every N minutes, or on milestone action, create a DVCS commit from CRDT materialized text.
- Commit includes:
  - rendered text blob (for diff/patch workflows)
  - optional: encrypted CRDT snapshot blob as an internal object
  - signatures as in 1.0

Audit:
- Commits remain durable, reviewable history.
- Realtime stream is ephemeral; do not rely on it for audit trails.

## G) UI/UX (Studio)

- Presence indicators in editor (subtle)
- Live badge when realtime connected
- Conflict handling is mostly unnecessary (CRDT), but show:
  - Concurrent edits merged automatically
- Create snapshot/commit button (optional) + automatic periodic commits
- Permission UI:
  - invite collaborator
  - device verification (fingerprints/QR) for trust

## H) Security and Failure Modes

- Key verification:
  - show device fingerprints
  - allow out-of-band verification
- Compromise handling:
  - rotate keys
  - mark device revoked
  - future data protected
- Data retention:
  - server stores only encrypted deltas
  - retention policy configurable
- Denial-of-service:
  - rate limit per device
  - cap delta sizes
  - backpressure

## I) Acceptance Criteria (2.0)

1. Two devices can co-edit the same section in realtime with E2EE, server sees only ciphertext.
2. Offline client can reconnect and catch up using encrypted deltas.
3. Periodic snapshots produce signed DVCS commits (audit trail preserved).
4. Membership changes rotate session keys; revoked devices cannot decrypt new realtime traffic.
5. System remains section-scoped (no massive whole-doc CRDT performance collapse).
