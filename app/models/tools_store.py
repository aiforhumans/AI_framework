from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


DATA_FILE = Path("app/data/tools.json")


class ToolConfig(BaseModel):
    id: int = Field(..., description="Unique tool identifier")
    name: str
    description: str = ""
    input_schema: dict = Field(default_factory=dict)
    endpoint: str = ""
    enabled: bool = True
    models: List[str] = Field(default_factory=list)
    agents: List[str] = Field(default_factory=list)


class ToolStore:
    def __init__(self, data_file: Path | None = None) -> None:
        self.data_file = data_file or DATA_FILE
        if not self.data_file.parent.exists():
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self._write_all([])

    def _read_all(self) -> List[ToolConfig]:
        import json

        if not self.data_file.exists():
            return []
        with self.data_file.open("r", encoding="utf-8") as f:
            raw = json.load(f) or []
        return [ToolConfig(**item) for item in raw]

    def _write_all(self, tools: List[ToolConfig]) -> None:
        import json

        with self.data_file.open("w", encoding="utf-8") as f:
            json.dump([t.model_dump() for t in tools], f, indent=2)

    def list_tools(self) -> List[ToolConfig]:
        return self._read_all()

    def get_tool(self, tool_id: int) -> Optional[ToolConfig]:
        for tool in self._read_all():
            if tool.id == tool_id:
                return tool
        return None

    def _next_id(self, tools: List[ToolConfig]) -> int:
        if not tools:
            return 1
        return max(t.id for t in tools) + 1

    def create_tool(self, tool: ToolConfig) -> ToolConfig:
        tools = self._read_all()
        tool.id = self._next_id(tools)
        tools.append(tool)
        self._write_all(tools)
        return tool

    def update_tool(self, tool_id: int, update: dict) -> Optional[ToolConfig]:
        tools = self._read_all()
        updated_tool: Optional[ToolConfig] = None
        for idx, tool in enumerate(tools):
            if tool.id == tool_id:
                data = tool.model_dump()
                data.update(update)
                updated_tool = ToolConfig(**data)
                tools[idx] = updated_tool
                break
        if updated_tool is not None:
            self._write_all(tools)
        return updated_tool

    def delete_tool(self, tool_id: int) -> bool:
        tools = self._read_all()
        new_tools = [t for t in tools if t.id != tool_id]
        if len(new_tools) == len(tools):
            return False
        self._write_all(new_tools)
        return True

    def toggle_tool(self, tool_id: int) -> Optional[ToolConfig]:
        tool = self.get_tool(tool_id)
        if tool is None:
            return None
        return self.update_tool(tool_id, {"enabled": not tool.enabled})
