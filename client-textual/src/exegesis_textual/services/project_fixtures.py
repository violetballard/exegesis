from __future__ import annotations

from pathlib import Path
import shutil

from exegesis_textual.panes.document_pane import DOCUMENT_FIXTURES, load_document_fixture_content
from exegesis_textual.panes.project_pane import PROJECT_NAME, ProjectEntry
from exegesis_textual.services.projects import safe_project_dir_name, textual_projects_dir

DEFAULT_PROJECT_NAMES = (
    PROJECT_NAME,
    "Field Notes Project",
    "Archive Review Project",
)
PROJECT_MANIFEST_PATH = Path(".exegesis") / "project.json"
DEFAULT_EMPTY_PROJECT_NAME = "Untitled Project"
DEFAULT_PROJECT_DOCUMENT_IDS = {
    "current-draft": "drafts/current_draft.md",
    "project-demo-essay": "memos/fieldwork/round_1/data_memo_1.md",
    "project-root-memo": "memos/root_memo_example.md",
    "project-compaction-filler-1": "memos/compaction_test_files/compaction_filler_1.md",
    "project-compaction-filler-2": "memos/compaction_test_files/compaction_filler_2.md",
    "project-compaction-filler-3": "memos/compaction_test_files/compaction_filler_3.md",
    "project-compaction-filler-4": "memos/compaction_test_files/compaction_filler_4.md",
    "project-longform-essay": "summaries/summary_1.md",
    "project-notebook": "transcripts/interviews/2026/participant_1/transcript_1_participant_1_5_1_26.md",
    "project-root-transcript": "transcripts/transcript_root_example.md",
    "project-lit-review": "literature/literature_reviews/leadership/article_1_last_first_title.md",
    "project-root-literature": "literature/article_root_example.md",
}
DEFAULT_PROJECT_FIXTURE_SOURCES = {
    "current-draft": "current_draft.md",
    "project-demo-essay": "data_memo_1.md",
    "project-root-memo": "data_memo_1.md",
    "project-longform-essay": "summary_1.md",
    "project-notebook": "transcript_1_participant_1_5_1_26.md",
    "project-root-transcript": "transcript_1_participant_1_5_1_26.md",
    "project-lit-review": "article_1_last_first_title.md",
    "project-root-literature": "article_1_last_first_title.md",
}
COMPACTION_FILLER_SLUG_PREFIX = "project-compaction-filler-"
NEW_PROJECT_CURRENT_DRAFT_CONTENT = """# Current Draft

Welcome to your Exegesis project.

Start writing here, or import supporting markdown files into the project browser. Drafts are your working outputs; memos, summaries, transcripts, and literature are supporting materials for the notebook and basket.
"""
NEW_PROJECT_CURRENT_DRAFT_ENTRY = ProjectEntry(
    "current-draft",
    "Drafts",
    "current_draft.md",
    "drafts/current_draft.md",
    "Your main writing draft for this project.",
    (
        "Start writing here.",
        "Import supporting markdown files when you are ready.",
        "Notebook actions use this draft with the current basket context.",
    ),
)
def reset_default_demo_project() -> None:
    shutil.rmtree(textual_projects_dir() / safe_project_dir_name(PROJECT_NAME), ignore_errors=True)


def default_project_fixture_content(slug: str) -> str:
    if slug.startswith(COMPACTION_FILLER_SLUG_PREFIX):
        try:
            index = int(slug.removeprefix(COMPACTION_FILLER_SLUG_PREFIX))
        except ValueError:
            index = 1
        return compaction_filler_content(index)
    source_name = DEFAULT_PROJECT_FIXTURE_SOURCES.get(slug)
    if source_name is not None:
        return load_document_fixture_content(source_name)
    fixture = DOCUMENT_FIXTURES.get(slug)
    return fixture.content if fixture is not None else ""


def compaction_filler_content(index: int) -> str:
    paragraph = (
        f"Compaction filler {index} repeats a non-confidential synthetic research memo paragraph. "
        "It discusses project planning, coded observations, basket context, retrieval notes, and "
        "drafting decisions without including participant data. This text exists only to fill the "
        "notebook request budget for manual compaction testing. "
    )
    repeated = "\n\n".join(
        f"{paragraph} Section {section:04d} keeps the wording stable for deterministic token estimates."
        for section in range(1, 701)
    )
    return f"# Compaction Filler {index}\n\n{repeated}\n"
