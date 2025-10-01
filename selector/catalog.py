"""Catalog utilities for ATDF tool discovery, persistence, and ranking."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import jsonschema

from .storage import CatalogStorage

LOGGER = logging.getLogger(__name__)


@dataclass
class ATDFToolRecord:
    """Normalized summary of an ATDF tool descriptor."""

    tool_id: str
    description: str
    when_to_use: Optional[str]
    schema_version: str
    languages: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    source: str = "local"
    raw_descriptor: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        """Return a JSON-serializable representation of the record."""
        return {
            "tool_id": self.tool_id,
            "description": self.description,
            "when_to_use": self.when_to_use,
            "schema_version": self.schema_version,
            "languages": list(self.languages),
            "tags": list(self.tags),
            "source": self.source,
        }


class ToolCatalog:
    """Catalog that aggregates ATDF tool descriptors with optional persistence."""

    def __init__(
        self,
        schema_dir: Optional[Path] = None,
        storage: Optional[CatalogStorage] = None,
    ) -> None:
        self.schema_dir = schema_dir or (Path(__file__).resolve().parent.parent / "schema")
        self._basic_schema = self._load_schema("atdf_schema.json")
        self._enhanced_schema = self._load_schema("enhanced_atdf_schema.json")
        self._tools: Dict[str, ATDFToolRecord] = {}
        self._errors: List[str] = []
        self.storage = storage
        if self.storage:
            self._bootstrap_from_storage()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @property
    def tools(self) -> Dict[str, ATDFToolRecord]:
        return self._tools

    @property
    def errors(self) -> List[str]:
        return self._errors

    def add_tool(
        self,
        descriptor: Dict[str, object],
        source: str,
        *,
        server_id: Optional[int] = None,
    ) -> Optional[ATDFToolRecord]:
        """Validate and add a descriptor to the catalog."""
        try:
            record = self._normalize_descriptor(descriptor, source=source)
        except ValueError as exc:  # pragma: no cover - defensive, logged below
            LOGGER.warning("Skipping tool due to normalization error: %s", exc)
            self._errors.append(str(exc))
            return None

        key = self._record_key(record.tool_id, record.source)
        if key in self._tools:
            LOGGER.info("Replacing existing descriptor for key=%s", key)
        self._tools[key] = record

        if self.storage and server_id is not None:
            self.storage.upsert_tool(
                server_id,
                record.tool_id,
                record.raw_descriptor,
                description=record.description,
                when_to_use=record.when_to_use,
                languages=record.languages,
                tags=record.tags,
            )
        return record

    def load_directory(
        self,
        directory: Path,
        *,
        recursive: bool = True,
        server_label: Optional[str] = None,
    ) -> int:
        """Load ATDF descriptors from a directory of JSON/YAML files."""
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        patterns = ("*.json", "*.yaml", "*.yml")
        if recursive:
            files = [p for pattern in patterns for p in directory.rglob(pattern)]
        else:
            files = [p for pattern in patterns for p in directory.glob(pattern)]

        server_ref = server_label or f"file://{directory.resolve()}"
        server_id = None
        if self.storage:
            server_id = self.storage.register_server(server_ref, name=directory.name)

        count = 0
        active_ids: List[str] = []
        for path in files:
            descriptor = self._read_descriptor(path)
            if not descriptor:
                continue
            record = self.add_tool(
                descriptor,
                source=server_ref if server_id is not None else str(path.resolve()),
                server_id=server_id,
            )
            if record:
                count += 1
                active_ids.append(record.tool_id)

        if self.storage and server_id is not None:
            self.storage.mark_inactive(server_id, active_ids)
            self.storage.update_server_metadata(server_id, last_sync=datetime.utcnow())
        return count

    def load_from_mcp(
        self,
        url: str,
        *,
        server_name: Optional[str] = None,
        timeout: float = 10.0,
    ) -> int:
        """Fetch tool metadata from an MCP bridge `/tools` endpoint."""
        request = Request(url, headers={"Accept": "application/json"})
        try:
            with urlopen(request, timeout=timeout) as response:  # nosec B310 - controlled URL
                payload = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, json.JSONDecodeError) as exc:
            message = f"Failed to load tools from MCP endpoint {url}: {exc}"
            LOGGER.warning(message)
            self._errors.append(message)
            return 0

        tools = payload.get("tools") if isinstance(payload, dict) else None
        if not tools:
            LOGGER.info("No tools returned by MCP endpoint %s", url)
            return 0

        server_id = None
        if self.storage:
            server_id = self.storage.register_server(url, name=server_name)

        count = 0
        active_ids: List[str] = []
        for tool in tools:
            if not isinstance(tool, dict):
                continue
            descriptor = self._convert_mcp_tool(tool)
            record = self.add_tool(descriptor, source=url, server_id=server_id)
            if record:
                count += 1
                active_ids.append(record.tool_id)

        cache_timestamp = payload.get("cache_timestamp") if isinstance(payload, dict) else None
        if self.storage and server_id is not None:
            self.storage.mark_inactive(server_id, active_ids)
            self.storage.update_server_metadata(
                server_id,
                cache_timestamp=cache_timestamp,
                last_sync=datetime.utcnow(),
            )
        return count

    def list_tools(
        self,
        *,
        sources: Optional[Sequence[str]] = None,
        tool_ids: Optional[Sequence[str]] = None,
    ) -> List[ATDFToolRecord]:
        """Return a list of registered tools, optionally filtered."""
        if self.storage:
            records: List[ATDFToolRecord] = []
            for data in self.storage.fetch_records(server_urls=sources, tool_ids=tool_ids):
                record = ATDFToolRecord(
                    tool_id=data["tool_id"],
                    description=data.get("description", ""),
                    when_to_use=data.get("when_to_use"),
                    schema_version=str(data.get("schema_version", "1.0.0")),
                    languages=list(data.get("languages", [])),
                    tags=list(data.get("tags", [])),
                    source=data.get("source", "remote"),
                    raw_descriptor=data.get("descriptor", {}),
                )
                key = self._record_key(record.tool_id, record.source)
                self._tools[key] = record
                records.append(record)
            return records

        # In-memory fallback
        records = list(self._tools.values())
        if sources:
            sources_lower = {value.lower() for value in sources}
            records = [record for record in records if record.source.lower() in sources_lower]
        if tool_ids:
            tool_id_set = set(tool_ids)
            records = [record for record in records if record.tool_id in tool_id_set]
        return sorted(records, key=lambda record: (record.source, record.tool_id))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _bootstrap_from_storage(self) -> None:
        for data in self.storage.bootstrap_records():
            record = ATDFToolRecord(
                tool_id=data["tool_id"],
                description=data.get("description", ""),
                when_to_use=data.get("when_to_use"),
                schema_version=str(data.get("schema_version", "1.0.0")),
                languages=list(data.get("languages", [])),
                tags=list(data.get("tags", [])),
                source=data.get("source", "remote"),
                raw_descriptor=data.get("descriptor", {}),
            )
            key = self._record_key(record.tool_id, record.source)
            self._tools[key] = record

    @staticmethod
    def _record_key(tool_id: str, source: str) -> str:
        return f"{source}::{tool_id}"

    def _load_schema(self, filename: str) -> Optional[Dict[str, object]]:
        path = Path(self.schema_dir) / filename
        if not path.exists():
            LOGGER.debug("Schema not found: %s", path)
            return None
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def _read_descriptor(self, path: Path) -> Optional[Dict[str, object]]:
        try:
            text = path.read_text(encoding="utf-8")
            if path.suffix.lower() in {".yaml", ".yml"}:
                import yaml  # Lazy import to avoid mandatory dependency

                return yaml.safe_load(text)
            return json.loads(text)
        except Exception as exc:  # pragma: no cover - defensive logging
            message = f"Failed to read descriptor {path}: {exc}"
            LOGGER.warning(message)
            self._errors.append(message)
            return None

    def _normalize_descriptor(self, descriptor: Dict[str, object], source: str) -> ATDFToolRecord:
        schema_version = str(descriptor.get("schema_version") or "1.0.0")
        self._validate_descriptor(descriptor, schema_version)

        tool_id = self._extract_tool_id(descriptor)
        if not tool_id:
            raise ValueError("ATDF descriptor missing `tool_id` or `id`")

        description = self._extract_description(descriptor)
        when_to_use = self._extract_when_to_use(descriptor)
        languages = self._extract_languages(descriptor)
        tags = self._extract_tags(descriptor)

        return ATDFToolRecord(
            tool_id=tool_id,
            description=description,
            when_to_use=when_to_use,
            schema_version=schema_version,
            languages=languages,
            tags=tags,
            source=source,
            raw_descriptor=descriptor,
        )

    def _validate_descriptor(self, descriptor: Dict[str, object], schema_version: str) -> None:
        enhanced_keys = {"metadata", "localization", "examples", "prerequisites", "feedback"}
        is_enhanced = schema_version.startswith("2") or bool(enhanced_keys.intersection(descriptor.keys()))
        schema = None
        if is_enhanced and self._enhanced_schema:
            schema = self._enhanced_schema
        elif self._basic_schema:
            schema = self._basic_schema
        else:  # pragma: no cover - configuration fallback
            LOGGER.debug("No schema available for validation; skipping")
            return
        try:
            jsonschema.validate(descriptor, schema)
        except jsonschema.ValidationError as exc:
            raise ValueError(f"ATDF descriptor validation error: {exc.message}") from exc

    @staticmethod
    def _extract_tool_id(descriptor: Dict[str, object]) -> Optional[str]:
        for key in ("tool_id", "id", "name"):
            value = descriptor.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    @staticmethod
    def _extract_description(descriptor: Dict[str, object]) -> str:
        description = descriptor.get("description")
        if isinstance(description, str) and description.strip():
            return description.strip()
        localization = descriptor.get("localization")
        if isinstance(localization, dict):
            for value in localization.values():
                text = value.get("description") if isinstance(value, dict) else value
                if isinstance(text, str) and text.strip():
                    return text.strip()
        return ""

    @staticmethod
    def _extract_when_to_use(descriptor: Dict[str, object]) -> Optional[str]:
        when = descriptor.get("when_to_use")
        if isinstance(when, str) and when.strip():
            return when.strip()
        localization = descriptor.get("localization")
        if isinstance(localization, dict):
            for value in localization.values():
                text = value.get("when_to_use") if isinstance(value, dict) else None
                if isinstance(text, str) and text.strip():
                    return text.strip()
        return None

    @staticmethod
    def _extract_languages(descriptor: Dict[str, object]) -> List[str]:
        languages: List[str] = []
        localization = descriptor.get("localization")
        if isinstance(localization, dict):
            languages.extend(sorted(localization.keys()))
        if not languages:
            languages.append("default")
        return languages

    @staticmethod
    def _extract_tags(descriptor: Dict[str, object]) -> List[str]:
        metadata = descriptor.get("metadata")
        if isinstance(metadata, dict):
            tags = metadata.get("tags")
            if isinstance(tags, list):
                return [str(tag) for tag in tags if isinstance(tag, (str, int))]
        return []

    @staticmethod
    def _convert_mcp_tool(tool: Dict[str, object]) -> Dict[str, object]:
        """Convert an MCP tool entry into an ATDF-like structure."""
        descriptor: Dict[str, object] = {
            "tool_id": tool.get("name"),
            "description": tool.get("description", ""),
            "schema_version": "1.0.0",
            "how_to_use": {
                "inputs": [],
                "outputs": {
                    "success": "",
                    "failure": [],
                },
            },
        }
        input_schema = tool.get("inputSchema")
        if isinstance(input_schema, dict):
            descriptor["input_schema"] = input_schema
        return descriptor
