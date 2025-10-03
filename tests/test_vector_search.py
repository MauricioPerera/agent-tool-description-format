#!/usr/bin/env python3
"""Pruebas unitarias para el almacén vectorial ATDF."""

import json
import os
import shutil
import sys
import tempfile
import unittest
from typing import List
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from sdk.atdf_sdk import ATDFToolbox
from sdk.vector_search import ATDFVectorStore

# Variable global para detectar si las dependencias están instaladas
VECTOR_DEPENDENCIES_AVAILABLE = False
try:  # pragma: no cover - se verifica mediante los decoradores skipIf
    import lancedb
    import sentence_transformers

    VECTOR_DEPENDENCIES_AVAILABLE = True
except ImportError:  # pragma: no cover - cuando faltan dependencias
    pass

# Herramientas de ejemplo utilizadas en las pruebas
SAMPLE_TOOLS: List[dict] = [
    {
        "tool_id": "test_tool_1",
        "description": "Una herramienta para enviar correos electrónicos",
        "when_to_use": "Cuando necesites enviar un mensaje a alguien por correo electrónico",
        "how_to_use": {
            "inputs": [
                {"name": "to", "type": "string", "description": "Destinatario"},
                {"name": "subject", "type": "string", "description": "Asunto"},
                {"name": "body", "type": "string", "description": "Cuerpo del mensaje"},
            ],
            "outputs": {
                "success": "Correo enviado correctamente",
                "failure": [{"error": "invalid_email", "message": "Correo inválido"}],
            },
        },
        "metadata": {"tags": ["comunicación", "correo", "mensaje"]},
    },
    {
        "tool_id": "test_tool_2",
        "description": "Una herramienta para buscar información en internet",
        "when_to_use": "Cuando necesites buscar información actualizada en la web",
        "how_to_use": {
            "inputs": [
                {
                    "name": "query",
                    "type": "string",
                    "description": "Consulta de búsqueda",
                }
            ],
            "outputs": {
                "success": "Resultados de búsqueda",
                "failure": [
                    {"error": "no_results", "message": "No se encontraron resultados"}
                ],
            },
        },
        "metadata": {"tags": ["búsqueda", "información", "internet"]},
    },
    {
        "tool_id": "test_tool_3",
        "description": "Una herramienta para traducir texto entre idiomas",
        "when_to_use": "Cuando necesites traducir un texto de un idioma a otro",
        "how_to_use": {
            "inputs": [
                {"name": "text", "type": "string", "description": "Texto a traducir"},
                {
                    "name": "source_lang",
                    "type": "string",
                    "description": "Idioma de origen",
                },
                {
                    "name": "target_lang",
                    "type": "string",
                    "description": "Idioma de destino",
                },
            ],
            "outputs": {
                "success": "Texto traducido",
                "failure": [
                    {"error": "unsupported_language", "message": "Idioma no soportado"}
                ],
            },
        },
        "metadata": {"tags": ["traducción", "idioma", "lenguaje"]},
    },
]


@unittest.skipIf(
    not VECTOR_DEPENDENCIES_AVAILABLE,
    "Dependencias de búsqueda vectorial no instaladas",
)
class TestATDFVectorStore(unittest.TestCase):
    """Pruebas para la clase ATDFVectorStore usando su API síncrona."""

    def setUp(self) -> None:
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_vector_db")

        self.model_patcher = mock.patch("sentence_transformers.SentenceTransformer")
        self.mock_model_cls = self.model_patcher.start()
        self.mock_model = mock.MagicMock()
        self.mock_model.encode.return_value = [0.1, 0.2, 0.3, 0.4]
        self.mock_model.get_sentence_embedding_dimension.return_value = 4
        self.mock_model_cls.return_value = self.mock_model

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir)
        self.model_patcher.stop()

    def test_basic_configuration(self) -> None:
        """Verificar que la configuración inicial se conserva."""

        vector_store = ATDFVectorStore(db_path=self.db_path, table_name="test_table")

        self.assertEqual(vector_store.db_path, self.db_path)
        self.assertEqual(vector_store.table_name, "test_table")

    @mock.patch("lancedb.connect")
    def test_add_tool_sync_initializes_and_adds(self, mock_connect) -> None:
        """Añadir una herramienta debe preparar la base de datos y almacenarla."""

        mock_db = mock.MagicMock()
        mock_table = mock.MagicMock()
        mock_connect.return_value = mock_db
        mock_db.table_names.return_value = []
        mock_db.create_table.return_value = mock_table

        mock_search = mock.MagicMock()
        mock_table.search.return_value = mock_search
        mock_search.where.return_value = mock_search
        mock_search.limit.return_value = mock_search
        mock_search.to_pandas.return_value = mock.Mock(empty=True)

        vector_store = ATDFVectorStore(db_path=self.db_path)
        vector_store._generate_embedding = lambda text: [0.1, 0.2, 0.3, 0.4]

        result = vector_store.add_tool_sync(SAMPLE_TOOLS[0])

        self.assertTrue(result)
        mock_connect.assert_called_once_with(self.db_path)
        mock_table.add.assert_called_once()

    @mock.patch("lancedb.connect")
    def test_add_tools_sync_counts_inserted_records(self, mock_connect) -> None:
        """La inserción en lote debe añadir todas las herramientas proporcionadas."""

        mock_db = mock.MagicMock()
        mock_table = mock.MagicMock()
        mock_connect.return_value = mock_db
        mock_db.table_names.return_value = []
        mock_db.create_table.return_value = mock_table

        mock_search = mock.MagicMock()
        mock_table.search.return_value = mock_search
        mock_search.where.return_value = mock_search
        mock_search.limit.return_value = mock_search
        mock_search.to_pandas.return_value = mock.Mock(empty=True)

        vector_store = ATDFVectorStore(db_path=self.db_path)
        vector_store._generate_embedding = lambda text: [0.1, 0.2, 0.3, 0.4]

        count = vector_store.add_tools_sync(SAMPLE_TOOLS)

        self.assertEqual(count, len(SAMPLE_TOOLS))
        self.assertEqual(mock_table.add.call_count, len(SAMPLE_TOOLS))

    def test_search_returns_matches_with_scores(self) -> None:
        """La búsqueda síncrona debe devolver resultados normalizados."""

        import pandas as pd

        mock_db = mock.MagicMock()
        mock_table = mock.MagicMock()

        mock_search = mock.MagicMock()
        mock_table.search.return_value = mock_search
        mock_search.limit.return_value = mock_search
        mock_search.where.return_value = mock_search

        results_data = {
            "id": ["test_tool_1", "test_tool_2"],
            "score": [0.9, 0.7],
            "data": [json.dumps(SAMPLE_TOOLS[0]), json.dumps(SAMPLE_TOOLS[1])],
        }
        mock_results = pd.DataFrame(results_data)
        mock_search.to_df.return_value = mock_results

        vector_store = ATDFVectorStore(db_path=self.db_path)
        vector_store.initialized = True
        vector_store.db = mock_db
        vector_store.table = mock_table
        vector_store.embedding_dim = 4
        vector_store.model = self.mock_model
        vector_store._generate_embedding = lambda text: [0.1, 0.2, 0.3, 0.4]

        results = vector_store.search("buscar correo", {"limit": 2})

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["tool_id"], "test_tool_1")
        self.assertEqual(results[1]["tool_id"], "test_tool_2")

    def test_get_all_tools_sync_returns_normalized_tools(self) -> None:
        """Obtener todas las herramientas debe devolver datos normalizados."""

        import pandas as pd

        mock_db = mock.MagicMock()
        mock_table = mock.MagicMock()

        payload = pd.DataFrame({"raw_data": [json.dumps(SAMPLE_TOOLS[0])]})
        mock_table.to_pandas.return_value = payload

        vector_store = ATDFVectorStore(db_path=self.db_path)
        vector_store.initialized = True
        vector_store.db = mock_db
        vector_store.table = mock_table

        tools = vector_store.get_all_tools_sync()

        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0]["tool_id"], "test_tool_1")


@unittest.skipIf(
    not VECTOR_DEPENDENCIES_AVAILABLE,
    "Dependencias de búsqueda vectorial no instaladas",
)
class TestVectorSearchIntegration(unittest.TestCase):
    """Pruebas de integración para la búsqueda vectorial con ATDFToolbox."""

    def setUp(self) -> None:
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_vector_db")

        self.toolbox = ATDFToolbox()
        for tool_data in SAMPLE_TOOLS:
            self.toolbox.add_tool(tool_data)

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir)

    @mock.patch.object(ATDFVectorStore, "search")
    def test_find_tools_with_vector_search(self, mock_search) -> None:
        """La búsqueda vectorial debe integrarse con el toolbox."""

        def fake_search(query, options=None):
            if query == "enviar mensaje":
                return [SAMPLE_TOOLS[0]]
            return []

        mock_search.side_effect = fake_search

        vector_store = ATDFVectorStore(db_path=self.db_path)
        self.toolbox.set_vector_store(vector_store)

        results = self.toolbox.find_tools_by_text(
            "enviar mensaje", use_vector_search=True
        )

        self.assertEqual(len(results), 1)
        tool, score = results[0]
        self.assertEqual(tool.tool_id, "test_tool_1")
        self.assertIsInstance(score, float)
        mock_search.assert_called_once()

    @mock.patch.object(ATDFVectorStore, "search")
    def test_select_tool_for_task_with_vector_search(self, mock_search) -> None:
        """Seleccionar herramientas debe aprovechar la búsqueda vectorial."""

        def fake_search(query, options=None):
            if query == "traducir un texto":
                return [SAMPLE_TOOLS[2]]
            return []

        mock_search.side_effect = fake_search

        vector_store = ATDFVectorStore(db_path=self.db_path)
        self.toolbox.set_vector_store(vector_store)

        tool = self.toolbox.select_tool_for_task(
            "traducir un texto", use_vector_search=True
        )

        self.assertIsNotNone(tool)
        assert tool is not None  # ayuda para mypy/linters
        self.assertEqual(tool.tool_id, "test_tool_3")
        mock_search.assert_called_once()

    @mock.patch.object(ATDFVectorStore, "search")
    def test_fallback_to_normal_search(self, mock_search) -> None:
        """Si la búsqueda vectorial falla debe usarse la búsqueda tradicional."""

        mock_search.side_effect = RuntimeError("Error simulado en búsqueda vectorial")

        vector_store = ATDFVectorStore(db_path=self.db_path)
        self.toolbox.set_vector_store(vector_store)

        results = self.toolbox.find_tools_by_text("correo", use_vector_search=True)

        self.assertTrue(len(results) > 0)
        mock_search.assert_called_once()


if __name__ == "__main__":  # pragma: no cover - ejecución directa
    unittest.main()
