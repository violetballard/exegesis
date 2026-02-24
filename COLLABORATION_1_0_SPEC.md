# Collaboration 1.0 Spec

## Goal

- Ship collaboration as version control only for 1.0: `clone/commit/push/pull/merge`.
- End-to-end encrypted: server never sees plaintext.
- Works with the repo-like vault model (text + PDF).
- Audit-friendly: signed commits, deterministic provenance.

## Non-Goals

- Real-time co-editing.
- Server-side conflict resolution.
- Perfect revocation (cannot claw back data already pulled by a collaborator).

## A) Data Model (content-addressed objects)

Objects (all encrypted at rest on remote):

1. `blob`
- raw bytes of a file (text or PDF) OR chunked blobs for large files
- `id = hash(plaintext bytes)` OR `hash(ciphertext bytes)` (choose one and be consistent; recommended: hash plaintext for integrity + store ciphertext separately)

2. `tree`
- directory listing mapping `name -> (object_id, type)`
- `id = hash(serialized tree)`

3. `commit`
- fields:
  - `tree_id`
  - `parent_commit_ids[]`
  - `author_device_id`
  - `timestamp`
  - `message` (optional; avoid sensitive default)
  - `metadata` (optional; no content)
- `id = hash(serialized commit)`

4. `refs`
- named pointers to commits:
  - `main`, branches, tags

## B) Crypto (E2EE)

Keys:
- Project Data Key (PDK): symmetric key used to encrypt all objects (AEAD).
- Device Identity Keypair: `Ed25519` (sign commits).
- Device Encryption Keypair: `X25519` (encrypt PDK envelope to devices).

Encryption:
- Objects encrypted with AEAD (`XChaCha20-Poly1305` recommended).
- Nonce: random per object.
- Associated Data (AAD): `{project_id, object_type, object_id/hash}` for binding.

Key distribution (membership):
- Each collaborator device has:
  - `device_id`
  - `public_sign_key` (`Ed25519`)
  - `public_enc_key` (`X25519`)
- PDK is shared by creating envelopes:
  - `envelope = seal(PDK, recipient_public_enc_key)`
- Membership list stored on remote as metadata (not secret), but PDK envelopes are encrypted.

Revocation / rotation:
- Removing a collaborator:
  - rotate PDK for future commits (new `PDK2`)
  - future objects encrypted with `PDK2`
  - old objects already pulled remain readable to removed collaborator (expected limitation)

## C) Local Vault Mapping

Vault is the working directory; sync is a remote mirror of encrypted objects.

- Vault contents are canonical locally.
- Export for sync:
  - serialize file contents into blobs
  - update trees and commits
- PDFs treated as blobs (optionally chunked)

Granularity:
- Prefer section-level files for text (already part of workflow). This reduces merge pain.

## D) Operations

1. `init` / create remote project
- create `project_id`
- generate `PDK`
- upload initial refs + envelopes for creator device

2. `clone`
- download refs, commits, trees, blobs (ciphertext)
- decrypt using `envelope(PDK)`
- materialize working tree into local vault (or map into vault store)

3. `commit`
- compute blobs/trees
- build commit object
- sign commit with device sign key
- store locally

4. `push`
- upload missing objects (ciphertext) + signed commits + ref updates
- remote is dumb: accepts objects, validates signatures optionally, stores

5. `pull` / `fetch`
- download new objects + refs
- verify signatures
- decrypt objects
- update local refs

6. `merge`
- default: 3-way merge on text files (section-level)
- PDFs: choose one version (no merge) or keep both
- store merge result as new commit

## E) Remote (server) requirements

Remote is dumb storage + auth:

- store objects by `object_id`
- store refs per project
- store membership metadata and PDK envelopes
- provide list-missing endpoints (like git pack)
- enforce access control (who can read/write)

Backend options:
- S3 object store + small API for refs/envelopes (recommended)
- self-hosted Exegesis Remote service that wraps object storage

## F) Auditability

- Every commit is signed by device.
- Engine records:
  - `commit_id`, `device_id`, `timestamp`, parents
  - merge events
  - push/pull events (no content)
- Optional: record section-changed summaries as hashes/IDs, not text.

## G) UI/UX (Studio)

Sync panel:
- remote connected status
- last push/pull times
- pending commits count
- conflict list with per-section diff review

Invite collaborator:
- add their device public keys
- create encrypted PDK envelope
- upload envelope to remote

## H) Acceptance Criteria (1.0)

1. Two devices can clone/pull/push encrypted objects with no plaintext on remote.
2. Commits are signed and verified on pull.
3. Section-level text merges work; conflicts surface with diff UI.
4. Removing a collaborator rotates PDK for future commits; old data limitation is documented.
5. Entire system works offline; sync occurs when remote reachable.
