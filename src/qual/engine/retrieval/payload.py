from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Protocol


class RetrievalDownstreamPayloadSource(Protocol):
    def to_downstream_payload(self) -> dict[str, object]:
        """Return the stable retrieval payload consumed by downstream engine flows."""


class RetrievalCitationBundleSource(Protocol):
    def citation_bundle(self) -> dict[str, object]:
        """Return the deterministic citation snapshot consumed by downstream engine flows."""


class RetrievalSourceBundleSource(Protocol):
    def source_bundle(self) -> dict[str, object]:
        """Return the deterministic doc and excerpt snapshot consumed by engine flows."""


class RetrievalContextBundleSource(Protocol):
    def retrieval_context_bundle(self) -> dict[str, object]:
        """Return the deterministic retrieval context consumed by engine flows."""


@dataclass(frozen=True)
class RetrievalDownstreamPayload:
    """Deterministic downstream retrieval contract for engine consumers."""

    query: dict[str, object]
    policy: dict[str, object]
    audit_ref: str
    result_fingerprint: str
    retrieval_backend: str
    retrieval_mode: str
    citation_status: dict[str, object]
    retrieval_citation_bundle: dict[str, object]
    retrieval_summary: dict[str, object]
    doc_hits: list[dict[str, object]]
    excerpt_hits: list[dict[str, object]]
    retrieval_diagnostics: dict[str, object]
    retrieval_manifest: dict[str, object]
    retrieval_evidence: dict[str, object]
    retrieval_provenance: dict[str, object]
    retrieval_source_bundle: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        policy = copy.deepcopy(self.policy)
        diagnostics = copy.deepcopy(self.retrieval_diagnostics)
        manifest = copy.deepcopy(self.retrieval_manifest)
        evidence = copy.deepcopy(self.retrieval_evidence)
        provenance = copy.deepcopy(self.retrieval_provenance)
        summary = copy.deepcopy(self.retrieval_summary)
        source_bundle = copy.deepcopy(self.retrieval_source_bundle)
        return {
            "query": copy.deepcopy(self.query),
            "policy": policy,
            "retrieval_policy": copy.deepcopy(policy),
            "audit_ref": self.audit_ref,
            "result_fingerprint": self.result_fingerprint,
            "retrieval_backend": self.retrieval_backend,
            "retrieval_mode": self.retrieval_mode,
            "citation_status": copy.deepcopy(self.citation_status),
            "retrieval_citation_bundle": copy.deepcopy(self.retrieval_citation_bundle),
            "retrieval_summary": summary,
            "doc_hits": [copy.deepcopy(doc_hit) for doc_hit in self.doc_hits],
            "excerpt_hits": [copy.deepcopy(hit) for hit in self.excerpt_hits],
            "retrieval_diagnostics": diagnostics,
            "retrieval_manifest": manifest,
            "retrieval_evidence": evidence,
            "retrieval_provenance": provenance,
            "retrieval_source_bundle": source_bundle,
        }


def build_retrieval_provenance_from_result(
    result: RetrievalDownstreamPayloadSource,
) -> dict[str, object]:
    """Return the deterministic retrieval provenance snapshot for a result."""

    payload = build_retrieval_downstream_payload_from_result(result)
    provenance = payload.get("retrieval_provenance")
    if isinstance(provenance, dict):
        return copy.deepcopy(provenance)
    return {}


def build_retrieval_downstream_payload(
    *,
    query: dict[str, object],
    policy: dict[str, object],
    audit_ref: str,
    result_fingerprint: str,
    retrieval_backend: str,
    retrieval_mode: str,
    citation_status: dict[str, object],
    retrieval_citation_bundle: dict[str, object],
    retrieval_summary: dict[str, object],
    doc_hits: list[dict[str, object]],
    excerpt_hits: list[dict[str, object]],
    retrieval_diagnostics: dict[str, object],
    retrieval_manifest: dict[str, object],
    retrieval_evidence: dict[str, object],
    retrieval_provenance: dict[str, object],
    retrieval_source_bundle: dict[str, object],
) -> dict[str, object]:
    return RetrievalDownstreamPayload(
        query=query,
        policy=policy,
        audit_ref=audit_ref,
        result_fingerprint=result_fingerprint,
        retrieval_backend=retrieval_backend,
        retrieval_mode=retrieval_mode,
        citation_status=citation_status,
        retrieval_citation_bundle=retrieval_citation_bundle,
        retrieval_summary=retrieval_summary,
        doc_hits=doc_hits,
        excerpt_hits=excerpt_hits,
        retrieval_diagnostics=retrieval_diagnostics,
        retrieval_manifest=retrieval_manifest,
        retrieval_evidence=retrieval_evidence,
        retrieval_provenance=retrieval_provenance,
        retrieval_source_bundle=retrieval_source_bundle,
    ).as_dict()


def build_retrieval_downstream_payload_from_result(
    result: RetrievalDownstreamPayloadSource,
) -> dict[str, object]:
    """Return a snapshot-safe copy of a retrieval result payload.

    Engine callers use this helper when they want the canonical downstream
    retrieval contract without holding onto the mutable service object that
    produced it.
    """
    payload_source = getattr(result, "as_downstream_payload", None)
    if callable(payload_source):
        return copy.deepcopy(payload_source())
    payload_source = getattr(result, "as_dict", None)
    if callable(payload_source):
        return copy.deepcopy(payload_source())
    return copy.deepcopy(result.to_downstream_payload())


def build_retrieval_citation_bundle_from_result(
    result: RetrievalDownstreamPayloadSource | RetrievalCitationBundleSource,
) -> dict[str, object]:
    """Return the deterministic doc and excerpt citation snapshot for a result."""
    bundle_source = getattr(result, "citation_bundle", None)
    if callable(bundle_source):
        return copy.deepcopy(bundle_source())
    payload = build_retrieval_downstream_payload_from_result(result)
    provenance = payload.get("retrieval_provenance", {})
    summary = payload.get("retrieval_summary", {})
    diagnostics = payload.get("retrieval_diagnostics", {})
    if not isinstance(provenance, dict):
        provenance = {}
    if not isinstance(summary, dict):
        summary = {}
    if not isinstance(diagnostics, dict):
        diagnostics = {}
    active_strategy_ids = provenance.get(
        "active_strategy_ids",
        summary.get("active_strategy_ids", diagnostics.get("active_strategy_ids", [])),
    )
    deferred_strategy_ids = provenance.get(
        "deferred_strategy_ids",
        summary.get("deferred_strategy_ids", diagnostics.get("deferred_strategy_ids", [])),
    )
    return {
        "query_fingerprint": provenance.get("query_fingerprint", summary.get("query_fingerprint", diagnostics.get("query_fingerprint"))),
        "result_fingerprint": provenance.get("result_fingerprint", summary.get("result_fingerprint", diagnostics.get("result_fingerprint"))),
        "retrieval_backend": provenance.get("retrieval_backend", summary.get("retrieval_backend", diagnostics.get("retrieval_backend"))),
        "retrieval_mode": provenance.get("retrieval_mode", summary.get("retrieval_mode", diagnostics.get("retrieval_mode"))),
        "retrieval_policy": copy.deepcopy(
            provenance.get(
                "retrieval_policy",
                summary.get("retrieval_policy", diagnostics.get("retrieval_policy", {})),
            )
        ),
        "active_strategy_ids": list(active_strategy_ids) if isinstance(active_strategy_ids, (list, tuple)) else [],
        "deferred_strategy_ids": list(deferred_strategy_ids) if isinstance(deferred_strategy_ids, (list, tuple)) else [],
        "citation_status": copy.deepcopy(summary.get("citation_status", provenance.get("citation_status", {}))),
        "doc_count": provenance.get("doc_count", summary.get("doc_count")),
        "excerpt_count": provenance.get("excerpt_count", summary.get("excerpt_count")),
        "doc_hits_fingerprint": provenance.get(
            "doc_hits_fingerprint", summary.get("doc_hits_fingerprint", diagnostics.get("doc_hits_fingerprint"))
        ),
        "excerpt_hits_fingerprint": provenance.get(
            "excerpt_hits_fingerprint",
            summary.get("excerpt_hits_fingerprint", diagnostics.get("excerpt_hits_fingerprint")),
        ),
        "doc_citations": copy.deepcopy(provenance.get("doc_citations", [])),
        "excerpt_citations": copy.deepcopy(provenance.get("excerpt_citations", [])),
    }


def build_retrieval_source_bundle_from_result(
    result: RetrievalDownstreamPayloadSource | RetrievalSourceBundleSource,
) -> dict[str, object]:
    """Return the deterministic retrieval source bundle for downstream engine flows."""
    bundle_source = getattr(result, "source_bundle", None)
    if callable(bundle_source):
        return copy.deepcopy(bundle_source())
    payload = build_retrieval_downstream_payload_from_result(result)
    source_bundle = payload.get("retrieval_source_bundle")
    if isinstance(source_bundle, dict):
        return copy.deepcopy(source_bundle)
    return {
        "query": copy.deepcopy(payload.get("query", {})),
        "policy": copy.deepcopy(payload.get("policy", payload.get("retrieval_policy", {}))),
        "retrieval_backend": payload.get("retrieval_backend"),
        "retrieval_mode": payload.get("retrieval_mode"),
        "citation_status": copy.deepcopy(payload.get("citation_status", {})),
        "retrieval_citation_bundle": copy.deepcopy(payload.get("retrieval_citation_bundle", {})),
        "retrieval_summary": copy.deepcopy(payload.get("retrieval_summary", {})),
        "doc_hits": copy.deepcopy(payload.get("doc_hits", [])),
        "excerpt_hits": copy.deepcopy(payload.get("excerpt_hits", [])),
        "retrieval_manifest": copy.deepcopy(payload.get("retrieval_manifest", {})),
        "retrieval_evidence": copy.deepcopy(payload.get("retrieval_evidence", {})),
        "retrieval_provenance": copy.deepcopy(payload.get("retrieval_provenance", {})),
    }


def build_retrieval_context_bundle_from_result(
    result: (
        RetrievalDownstreamPayloadSource
        | RetrievalCitationBundleSource
        | RetrievalSourceBundleSource
        | RetrievalContextBundleSource
    ),
) -> dict[str, object]:
    """Return the deterministic retrieval context bundle for downstream engine flows."""

    context_source = getattr(result, "retrieval_context_bundle", None)
    if callable(context_source):
        return copy.deepcopy(context_source())
    payload = build_retrieval_downstream_payload_from_result(result)
    return {
        "retrieval_downstream_payload": payload,
        "retrieval_citation_bundle": build_retrieval_citation_bundle_from_result(result),
        "retrieval_provenance": build_retrieval_provenance_from_result(result),
        "retrieval_source_bundle": build_retrieval_source_bundle_from_result(result),
    }
