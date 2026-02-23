from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeCapabilities:
    image_input: bool
    tool_calling: bool
    json_schema_mode: bool = False


@dataclass(frozen=True)
class ModelCapabilities:
    model_id: str
    supports_vision: bool
    max_ctx: int
    default_kv_cache: int


class OpenAICompatClient:
    """Local deterministic OpenAI-compatible client facade used by retrieval/docindex flows."""

    def __init__(
        self,
        *,
        base_url: str,
        model_id: str,
        runtime_capabilities: RuntimeCapabilities,
        model_capabilities: ModelCapabilities,
        prompt_template_hash: str = "pageindex_prompt_v2",
    ) -> None:
        self.base_url = base_url
        self.model_id = model_id
        self.runtime_capabilities = runtime_capabilities
        self.model_capabilities = model_capabilities
        self.prompt_template_hash = prompt_template_hash
        self.query_calls = 0

    def build_pageindex_tree(
        self,
        *,
        doc_id: str,
        text: str,
        max_depth: int,
        target_granularity: str,
        include_node_summaries: bool,
    ) -> tuple[list[dict[str, object]], dict[str, str]]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        chunks: list[str] = []
        chunk_size = 1200 if target_granularity == "subsection" else 2200
        if not lines:
            chunks = ["<empty-document>"]
        else:
            buf = ""
            for line in lines:
                if len(buf) + len(line) + 1 > chunk_size and buf:
                    chunks.append(buf)
                    buf = line
                else:
                    buf = f"{buf}\n{line}" if buf else line
            if buf:
                chunks.append(buf)

        tree: list[dict[str, object]] = []
        summaries: dict[str, str] = {}
        cursor = 0
        for idx, chunk in enumerate(chunks, start=1):
            node_id = f"{doc_id}:n{idx}"
            node = {
                "node_id": node_id,
                "title": f"Section {idx}",
                "depth": min(max_depth, 2),
                "page_start": idx,
                "page_end": idx,
                "char_start": cursor,
                "char_end": cursor + len(chunk),
                "children": [],
            }
            tree.append(node)
            cursor += len(chunk) + 1
            if include_node_summaries:
                summaries[node_id] = chunk[:160]
        return tree, summaries

    def query_pageindex_tree(
        self,
        *,
        tree: list[dict[str, object]],
        node_summaries: dict[str, str],
        query: str,
        section_hint: str | None,
        max_results: int,
    ) -> tuple[list[dict[str, object]], dict[str, object]]:
        self.query_calls += 1
        lowered = query.lower()
        ranked: list[tuple[int, dict[str, object]]] = []
        visited: list[str] = []
        for node in tree:
            node_id = str(node["node_id"])
            visited.append(node_id)
            title = str(node["title"]).lower()
            summary = node_summaries.get(node_id, "").lower()
            score = 0
            for token in lowered.split():
                if token in title:
                    score += 2
                if token in summary:
                    score += 1
            if section_hint and section_hint.lower() in title:
                score += 2
            ranked.append((score, node))
        ranked.sort(key=lambda item: item[0], reverse=True)
        best = [node for score, node in ranked if score > 0][:max_results]
        if not best:
            best = [node for _, node in ranked[:max_results]]
        trace = {"visited_node_ids": visited[:50], "decision_log": f"ranked:{len(ranked)}"}
        return best, trace

    def vision_read_pages(
        self,
        *,
        source_bytes: bytes,
        page_numbers: tuple[int, ...],
        output_format: str,
    ) -> dict[int, str]:
        text = source_bytes.decode("utf-8", errors="ignore")
        segments = [x.strip() for x in text.split("\n\n") if x.strip()]
        if not segments:
            segments = ["<scanned-page-content-unavailable>"]
        out: dict[int, str] = {}
        for page in page_numbers:
            idx = (page - 1) % len(segments)
            body = segments[idx]
            out[page] = body if output_format == "text" else f"## Page {page}\n\n{body}"
        return out
