"""Almacenamiento vectorial asíncrono para herramientas ATDF."""

from __future__ import annotations

import asyncio
import inspect
import json
import logging
import tempfile
from typing import Any, Dict, Iterable, List, Optional, Sequence

import numpy as np

# Importación opcional de dependencias
try:  # pragma: no cover - import guard exercised via unit tests
    import lancedb
    import sentence_transformers
    from lancedb.table import Table

    VECTOR_SEARCH_AVAILABLE = True
except ImportError:  # pragma: no cover - ejecutado cuando faltan dependencias
    VECTOR_SEARCH_AVAILABLE = False
    lancedb = None  # type: ignore
    sentence_transformers = None  # type: ignore
    Table = Any  # type: ignore

logger = logging.getLogger(__name__)


class ATDFVectorStore:
    """Administrar embeddings y búsqueda semántica de herramientas ATDF."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        db_path: Optional[str] = None,
        table_name: str = "tools",
    ) -> None:
        if not VECTOR_SEARCH_AVAILABLE:
            raise ImportError(
                "Las dependencias para búsqueda vectorial no están instaladas. "
                "Instálalas con: pip install lancedb sentence-transformers"
            )

        self.model_name = model_name
        self.table_name = table_name
        self.has_dependencies = True

        if db_path is None:
            self._temp_dir = tempfile.TemporaryDirectory()
            self.db_path = self._temp_dir.name
            self._is_temp = True
        else:
            self.db_path = db_path
            self._temp_dir = None
            self._is_temp = False

        self.model: Optional[sentence_transformers.SentenceTransformer] = None
        self.embedding_dim: Optional[int] = None
        self.db = None
        self.table: Optional[Table] = None
        self.initialized = False

    # ------------------------------------------------------------------
    # Ciclo de vida
    async def initialize(self) -> bool:
        """Inicializar el modelo de embeddings y la conexión LanceDB."""

        if self.initialized:
            return True

        await self._ensure_model()
        await self._ensure_database()

        self.initialized = True
        return True

    async def _ensure_model(self) -> None:
        if self.model is not None:
            return

        self.model = sentence_transformers.SentenceTransformer(self.model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

    async def _ensure_database(self) -> None:
        if self.db is not None:
            return

        self.db = lancedb.connect(self.db_path)

    async def _ensure_table(self) -> None:
        if self.db is None:
            raise RuntimeError("La base de datos LanceDB no está inicializada")

        if self.table_name in self.db.table_names():
            self.table = self.db.open_table(self.table_name)
            return

        if self.embedding_dim is None:
            raise RuntimeError("La dimensión del embedding es desconocida")

        init_vector = np.zeros(self.embedding_dim, dtype=np.float32)
        init_data = [
            {
                "id": "_init_",
                "name": "_init_",
                "description": "_init_",
                "parameters": [],
                "vector": init_vector,
                "raw_data": "{}",
            }
        ]

        self.table = self.db.create_table(self.table_name, data=init_data)
        # Limpiar el registro temporal utilizado para infiriar el esquema
        self.table.delete("id = '_init_'")

    # ------------------------------------------------------------------
    # Utilidades internas
    def _normalize_tool(self, tool: Any) -> Dict[str, Any]:
        if hasattr(tool, "to_dict"):
            data = tool.to_dict()  # type: ignore[attr-defined]
        elif isinstance(tool, dict):
            data = dict(tool)
        else:
            raise TypeError(
                "Las herramientas deben ser diccionarios o exponer to_dict()."
            )

        if "name" not in data:
            fallback = data.get("tool_id") or data.get("id")
            if not fallback:
                raise ValueError("La herramienta necesita un campo 'name' o 'tool_id'.")
            data["name"] = fallback

        if "description" not in data:
            data["description"] = ""

        if "tool_id" not in data and data.get("id"):
            data["tool_id"] = data["id"]
        elif "id" not in data and data.get("tool_id"):
            data["id"] = data["tool_id"]

        parameters = data.get("parameters")
        if parameters:
            normalized_params: List[Dict[str, Any]] = []
            for param in parameters:
                if hasattr(param, "model_dump"):
                    normalized_params.append(param.model_dump(exclude_none=True))  # type: ignore[attr-defined]
                elif hasattr(param, "dict"):
                    normalized_params.append(param.dict(exclude_none=True))  # type: ignore[attr-defined]
                elif isinstance(param, dict):
                    normalized_params.append(dict(param))
            data["parameters"] = normalized_params

        return data

    def _create_text_representation(self, tool: Dict[str, Any]) -> str:
        text = f"{tool['name']}: {tool.get('description', '')}"

        parameters = tool.get("parameters") or []
        for param in parameters:
            if hasattr(param, "name"):
                name = getattr(param, "name")
                description = getattr(param, "description", "")
            else:
                name = param.get("name", "")  # type: ignore[assignment]
                description = param.get("description", "")  # type: ignore[assignment]
            text += f" {name}: {description}"

        return text

    async def _embed_text(self, text: str) -> np.ndarray:
        if self.model is None:
            await self._ensure_model()

        embedding = self._generate_embedding(text)
        if inspect.isawaitable(embedding):
            embedding = await embedding  # type: ignore[assignment]

        return np.asarray(embedding, dtype=np.float32)

    def _generate_embedding(self, text: str):
        if self.model is None:
            raise RuntimeError("El modelo de embeddings no está inicializado")

        return self.model.encode(text, show_progress_bar=False)

    async def _prepare_record(self, tool: Any) -> Dict[str, Any]:
        normalized = self._normalize_tool(tool)
        tool_id = normalized.get("id") or normalized.get("tool_id")
        if not tool_id:
            tool_id = normalized["name"].lower().replace(" ", "_")
            normalized["id"] = tool_id
            normalized.setdefault("tool_id", tool_id)

        text_repr = self._create_text_representation(normalized)
        vector = await self._embed_text(text_repr)

        return {
            "id": tool_id,
            "name": normalized["name"],
            "description": normalized.get("description", ""),
            "parameters": normalized.get("parameters", []),
            "vector": vector,
            "raw_data": json.dumps(normalized),
        }

    async def _ensure_ready(self, require_table: bool = True) -> None:
        if not self.initialized:
            await self.initialize()
        if require_table and self.table is None:
            await self._ensure_table()

    # ------------------------------------------------------------------
    # Compatibilidad síncrona
    def _run_blocking(self, coroutine):
        try:
            return asyncio.run(coroutine)
        except RuntimeError as exc:
            if "asyncio.run() cannot be called from a running event loop" not in str(
                exc
            ):
                raise

        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coroutine)
        finally:
            loop.close()

    def initialize_sync(self) -> bool:
        """Inicializar el almacén vectorial desde un contexto síncrono."""

        return self._run_blocking(self.initialize())

    # ------------------------------------------------------------------
    # Operaciones públicas
    async def create_from_tools(self, tools: Sequence[Any]) -> bool:
        await self._ensure_ready(require_table=False)

        if not tools:
            return False

        records: List[Dict[str, Any]] = []
        for tool in tools:
            record = await self._prepare_record(tool)
            records.append(record)

        if not records:
            return False

        if self.db is None:
            raise RuntimeError("La base de datos LanceDB no está inicializada")

        self.table = self.db.create_table(
            self.table_name, data=records, mode="overwrite"
        )
        return True

    async def add_tool(self, tool: Any) -> bool:
        await self._ensure_ready()

        if self.table is None:
            raise RuntimeError("La tabla LanceDB no está lista")

        record = await self._prepare_record(tool)

        existing = self.table.search().where(f"id = '{record['id']}'").limit(1)

        if hasattr(existing, "to_pandas"):
            existing_df = existing.to_pandas()
        elif hasattr(existing, "to_df"):
            existing_df = existing.to_df()
        else:
            existing_df = existing

        has_existing = False
        if hasattr(existing_df, "empty"):
            has_existing = not bool(existing_df.empty)
        else:
            try:
                has_existing = len(existing_df) > 0  # type: ignore[arg-type]
            except TypeError:
                has_existing = False

        if has_existing:
            self.table.delete(f"id = '{record['id']}'")

        self.table.add([record])
        return True

    async def add_tools(self, tools: Iterable[Any]) -> int:
        count = 0
        for tool in tools:
            added = await self.add_tool(tool)
            if added:
                count += 1
        return count

    async def search_tools(
        self,
        query: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        await self._ensure_ready()

        if self.table is None:
            raise RuntimeError("La tabla LanceDB no está lista")

        options = options or {}
        limit = int(options.get("limit", 5))
        score_threshold = options.get("score_threshold")

        query_vector = await self._embed_text(query)

        search = self.table.search(query_vector).limit(limit)

        filter_clause = options.get("filter")
        if not filter_clause and options.get("language"):
            filter_clause = "true"

        if filter_clause:
            search = search.where(filter_clause)

        results_df = search.to_df() if hasattr(search, "to_df") else search.to_pandas()

        matches: List[Dict[str, Any]] = []
        for _, row in results_df.iterrows():
            score = row.get("score")
            if score is None and "_distance" in row:
                distance = float(row["_distance"])
                score = 1.0 - min(distance, 2.0) / 2.0

            if score is not None:
                try:
                    score_value = float(score)
                except (TypeError, ValueError):
                    logger.debug(
                        "No se pudo convertir la puntuación a float; se usará 0.0"
                    )
                    score_value = 0.0
            else:
                score_value = 0.0

            if (
                score_threshold is not None
                and score is not None
                and score_value < score_threshold
            ):
                continue

            payload = row.get("raw_data") or row.get("data")
            if isinstance(payload, str):
                try:
                    tool_data = json.loads(payload)
                except json.JSONDecodeError:
                    logger.debug("No se pudo decodificar el payload de la herramienta")
                    continue
            elif isinstance(payload, dict):
                tool_data = payload
            else:
                continue

            tool_data = self._normalize_tool(tool_data)
            tool_data["score"] = score_value
            matches.append(tool_data)

        return matches

    async def find_best_tool(
        self,
        query: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        options = dict(options or {})
        options.setdefault("limit", 1)

        results = await self.search_tools(query, options)
        return results[0] if results else None

    async def get_all_tools(self) -> List[Dict[str, Any]]:
        await self._ensure_ready()

        if self.table is None:
            raise RuntimeError("La tabla LanceDB no está lista")

        raw_results = (
            self.table.to_pandas()
            if hasattr(self.table, "to_pandas")
            else self.table.to_df()
        )

        iterable = (
            raw_results.iterrows()
            if hasattr(raw_results, "iterrows")
            else enumerate(raw_results)
        )

        tools: List[Dict[str, Any]] = []
        for _, row in iterable:
            payload = (
                row.get("raw_data") or row.get("data") if hasattr(row, "get") else row
            )
            if isinstance(payload, str):
                try:
                    tool_data = json.loads(payload)
                except json.JSONDecodeError:
                    continue
            elif isinstance(payload, dict):
                tool_data = payload
            else:
                continue

            tools.append(self._normalize_tool(tool_data))

        return tools

    async def get_tool_by_id(self, tool_id: str) -> Optional[Dict[str, Any]]:
        await self._ensure_ready()

        if self.table is None:
            raise RuntimeError("La tabla LanceDB no está lista")

        search = self.table.search().where(f"id = '{tool_id}'").limit(1)

        if hasattr(search, "to_pandas"):
            results = search.to_pandas()
        elif hasattr(search, "to_df"):
            results = search.to_df()
        else:
            results = []

        try:
            has_rows = len(results) > 0  # type: ignore[arg-type]
        except TypeError:
            has_rows = False

        if not has_rows:
            return None

        row = results.iloc[0] if hasattr(results, "iloc") else results[0]
        payload = row.get("raw_data") or row.get("data") if hasattr(row, "get") else row
        if isinstance(payload, str):
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                return None
        elif isinstance(payload, dict):
            data = payload
        else:
            return None

        return self._normalize_tool(data)

    async def delete_tool(self, tool_id: str) -> bool:
        await self._ensure_ready()

        if self.table is None:
            raise RuntimeError("La tabla LanceDB no está lista")

        deleted = self.table.delete(f"id = '{tool_id}'")

        try:
            return bool(deleted)
        except TypeError:
            return False

    # Métodos síncronos delegando a las versiones asíncronas -----------------
    def create_from_tools_sync(self, tools: Sequence[Any]) -> bool:
        return self._run_blocking(self.create_from_tools(tools))

    def add_tool_sync(self, tool: Any) -> bool:
        return self._run_blocking(self.add_tool(tool))

    def add_tools_sync(self, tools: Iterable[Any]) -> int:
        return self._run_blocking(self.add_tools(tools))

    def search_tools_sync(
        self,
        query: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        return self._run_blocking(self.search_tools(query, options))

    def find_best_tool_sync(
        self,
        query: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        return self._run_blocking(self.find_best_tool(query, options))

    def get_all_tools_sync(self) -> List[Dict[str, Any]]:
        return self._run_blocking(self.get_all_tools())

    def get_tool_by_id_sync(self, tool_id: str) -> Optional[Dict[str, Any]]:
        return self._run_blocking(self.get_tool_by_id(tool_id))

    def delete_tool_sync(self, tool_id: str) -> bool:
        return self._run_blocking(self.delete_tool(tool_id))

    # ------------------------------------------------------------------
    # Limpieza
    def __del__(self) -> None:  # pragma: no cover - destructor defensivo
        if self._is_temp and self._temp_dir is not None:
            self._temp_dir.cleanup()
