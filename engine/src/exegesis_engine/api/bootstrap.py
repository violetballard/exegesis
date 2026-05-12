from __future__ import annotations

from exegesis_engine.api.app_service import EngineRuntime, EngineService
from exegesis_engine.config import default_config


def build_runtime(*, project_name: str | None = None) -> EngineRuntime:
    config = default_config()
    config.app_data_dir.mkdir(parents=True, exist_ok=True)
    engine = EngineService()
    selected_project = project_name if project_name else config.default_project_name
    return engine.bootstrap(
        app_data_dir=config.app_data_dir,
        project_name=selected_project,
    )
