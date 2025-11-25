from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


DATA_FILE = Path("app/data/prompt_templates.json")


class PromptTemplate(BaseModel):
    id: int = Field(..., description="Unique template identifier")
    name: str
    description: str = ""
    system_prompt: str = ""
    user_prompt: str = ""
    variables: list[str] = Field(default_factory=list)


class PromptTemplateStore:
    def __init__(self, data_file: Path | None = None) -> None:
        self.data_file = data_file or DATA_FILE
        if not self.data_file.parent.exists():
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self._write_all([])

    def _read_all(self) -> List[PromptTemplate]:
        import json

        if not self.data_file.exists():
            return []
        with self.data_file.open("r", encoding="utf-8") as f:
            raw = json.load(f) or []
        return [PromptTemplate(**item) for item in raw]

    def _write_all(self, templates: List[PromptTemplate]) -> None:
        import json

        with self.data_file.open("w", encoding="utf-8") as f:
            json.dump([t.model_dump() for t in templates], f, indent=2)

    def list_templates(self) -> List[PromptTemplate]:
        return self._read_all()

    def get_template(self, template_id: int) -> Optional[PromptTemplate]:
        for t in self._read_all():
            if t.id == template_id:
                return t
        return None

    def _next_id(self, templates: List[PromptTemplate]) -> int:
        if not templates:
            return 1
        return max(t.id for t in templates) + 1

    def create_template(self, template: PromptTemplate) -> PromptTemplate:
        templates = self._read_all()
        template.id = self._next_id(templates)
        templates.append(template)
        self._write_all(templates)
        return template

    def update_template(self, template_id: int, update: dict) -> Optional[PromptTemplate]:
        templates = self._read_all()
        updated: Optional[PromptTemplate] = None
        for idx, t in enumerate(templates):
            if t.id == template_id:
                data = t.model_dump()
                data.update(update)
                updated = PromptTemplate(**data)
                templates[idx] = updated
                break
        if updated is not None:
            self._write_all(templates)
        return updated

    def delete_template(self, template_id: int) -> bool:
        templates = self._read_all()
        new_templates = [t for t in templates if t.id != template_id]
        if len(new_templates) == len(templates):
            return False
        self._write_all(new_templates)
        return True
