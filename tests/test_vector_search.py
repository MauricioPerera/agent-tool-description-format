#!/usr/bin/env python3
"""
Pruebas unitarias para el módulo de búsqueda vectorial de ATDF.

Estas pruebas verifican la funcionalidad básica del módulo de búsqueda
vectorial, incluyendo la inicialización, creación de embeddings y búsqueda.

Para ejecutar estas pruebas específicas:
    python -m unittest tests.test_vector_search
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np
import pandas as pd
import types

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from sdk.atdf_sdk import ATDFTool, ATDFToolbox
from sdk.vector_search import ATDFVectorStore
from sdk.vector_search import vector_store as vector_store_module

# Variable global para detectar si las dependencias están instaladas
VECTOR_DEPENDENCIES_AVAILABLE = False
try:
    import lancedb
    import sentence_transformers

    VECTOR_DEPENDENCIES_AVAILABLE = True
except ImportError:
    pass

if not VECTOR_DEPENDENCIES_AVAILABLE:
    if getattr(vector_store_module, "lancedb", None) is None:
        vector_store_module.lancedb = types.SimpleNamespace(connect=lambda *a, **k: None)
    elif not hasattr(vector_store_module.lancedb, "connect"):
        vector_store_module.lancedb.connect = lambda *a, **k: None  # type: ignore[attr-defined]
    if getattr(vector_store_module, "sentence_transformers", None) is None:
        vector_store_module.sentence_transformers = types.SimpleNamespace(
            SentenceTransformer=lambda *a, **k: None
        )
    elif not hasattr(vector_store_module.sentence_transformers, "SentenceTransformer"):
        vector_store_module.sentence_transformers.SentenceTransformer = (
            lambda *a, **k: None
        )
    vector_store_module.Table = object
    vector_store_module.VECTOR_SEARCH_AVAILABLE = True
    VECTOR_DEPENDENCIES_AVAILABLE = True

# Herramientas de ejemplo para las pruebas
SAMPLE_TOOLS = [
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


class TestATDFVectorStore(unittest.TestCase):
    """Pruebas para la clase ATDFVectorStore"""

    def setUp(self):
        """Configuración para las pruebas"""
        # Crear directorio temporal para la base de datos
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_vector_db")

        # Crear herramientas de prueba
        self.tools = [ATDFTool(tool_data) for tool_data in SAMPLE_TOOLS]

        # Evitar la descarga del modelo en las pruebas que no lo necesitan
        self.model_patcher = mock.patch(
            "sdk.vector_search.vector_store.sentence_transformers.SentenceTransformer"
        )
        self.mock_model = self.model_patcher.start()
        self.mock_model_instance = self.mock_model.return_value
        self.mock_model_instance.get_sentence_embedding_dimension.return_value = 4
        self.embedding = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32)

    def tearDown(self):
        """Limpieza después de las pruebas"""
        # Eliminar directorio temporal
        shutil.rmtree(self.test_dir)

        # Detener el patcher
        self.model_patcher.stop()

    def test_initialization(self):
        """Probar la inicialización básica del almacén vectorial"""
        vector_store = ATDFVectorStore(db_path=self.db_path, table_name="test_table")
        self.assertEqual(vector_store.db_path, self.db_path)
        self.assertEqual(vector_store.table_name, "test_table")
        self.assertFalse(vector_store.initialized)

    def test_check_dependencies(self):
        """Probar la verificación de dependencias"""
        vector_store = ATDFVectorStore(db_path=self.db_path)
        self.assertTrue(vector_store.has_dependencies)

    @mock.patch("sdk.vector_search.vector_store.lancedb.connect")
    def test_initialize(self, mock_connect):
        """Probar la inicialización del almacén vectorial"""
        # Configurar mocks
        mock_db = mock.MagicMock()
        mock_connect.return_value = mock_db
        mock_db.table_names.return_value = []

        # Crear y inicializar almacén vectorial
        vector_store = ATDFVectorStore(db_path=self.db_path)
        result = vector_store.initialize_sync()

        # Verificar
        self.assertTrue(result)
        self.assertTrue(vector_store.initialized)
        mock_connect.assert_called_once_with(self.db_path)
        self.mock_model.assert_called_once()

    @mock.patch("sdk.vector_search.vector_store.lancedb.connect")
    def test_create_from_tools(self, mock_connect):
        """Probar la creación de la base de datos a partir de herramientas"""
        # Configurar mocks
        mock_db = mock.MagicMock()
        mock_connect.return_value = mock_db
        mock_db.table_names.return_value = []
        mock_db.create_table.return_value = mock.MagicMock()

        # Crear y configurar almacén vectorial
        vector_store = ATDFVectorStore(db_path=self.db_path)
        # Inicializar manualmente algunos componentes
        vector_store.initialized = True
        vector_store.db = mock_db
        vector_store.embedding_dim = 4
        vector_store._embed_text = mock.AsyncMock(return_value=self.embedding)

        # Ejecutar
        result = vector_store.create_from_tools_sync(self.tools)

        # Verificar
        self.assertTrue(result)
        mock_db.create_table.assert_called_once()
        # Verificar que el primer argumento es el nombre de la tabla
        self.assertEqual(mock_db.create_table.call_args[0][0], "tools")

    @mock.patch("sdk.vector_search.vector_store.lancedb.connect")
    def test_add_tool(self, mock_connect):
        """Probar añadir una herramienta individual"""
        # Configurar mocks
        mock_db = mock.MagicMock()
        mock_connect.return_value = mock_db
        mock_table = mock.MagicMock()
        mock_db.table_names.return_value = ["tools"]
        mock_db.open_table.return_value = mock_table

        mock_existing = mock.MagicMock()
        mock_existing.limit.return_value = mock_existing
        mock_existing.where.return_value = mock_existing
        mock_existing.to_pandas.return_value = pd.DataFrame()
        mock_table.search.return_value = mock_existing

        # Crear y configurar almacén vectorial
        vector_store = ATDFVectorStore(db_path=self.db_path)
        # Inicializar manualmente
        vector_store.initialized = True
        vector_store.db = mock_db
        vector_store.table = mock_table
        vector_store._embed_text = mock.AsyncMock(return_value=self.embedding)

        # Ejecutar
        result = vector_store.add_tool_sync(self.tools[0])

        # Verificar
        self.assertTrue(result)
        mock_table.add.assert_called_once()

    @mock.patch("sdk.vector_search.vector_store.lancedb.connect")
    def test_search_tools(self, mock_connect):
        """Probar la búsqueda de herramientas"""
        # Configurar mocks
        mock_db = mock.MagicMock()
        mock_connect.return_value = mock_db
        mock_table = mock.MagicMock()
        mock_db.open_table.return_value = mock_table

        # Crear resultados simulados
        mock_search = mock.MagicMock()
        mock_table.search.return_value = mock_search
        mock_search.limit.return_value = mock_search
        mock_search.where.return_value = mock_search

        # Simular los resultados como un DataFrame
        results_data = {
            "id": ["test_tool_1", "test_tool_2"],
            "score": [0.9, 0.7],
            "data": [json.dumps(SAMPLE_TOOLS[0]), json.dumps(SAMPLE_TOOLS[1])],
        }
        mock_results = pd.DataFrame(results_data)
        mock_search.to_df.return_value = mock_results

        # Crear y configurar almacén vectorial
        vector_store = ATDFVectorStore(db_path=self.db_path)
        # Inicializar manualmente
        vector_store.initialized = True
        vector_store.db = mock_db
        vector_store.table = mock_table
        vector_store._embed_text = mock.AsyncMock(return_value=self.embedding)

        # Ejecutar
        results = vector_store.search_tools_sync(
            "buscar correo electrónico", {"language": "es", "limit": 2}
        )

        # Verificar
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["tool_id"], "test_tool_1")
        self.assertEqual(results[1]["tool_id"], "test_tool_2")
        mock_table.search.assert_called_once()
        mock_search.limit.assert_called_once_with(2)
        mock_search.where.assert_called_once()

    @mock.patch("sdk.vector_search.vector_store.lancedb.connect")
    def test_find_best_tool(self, mock_connect):
        """Probar encontrar la mejor herramienta para un objetivo"""
        # Configurar mocks para simular una búsqueda exitosa
        vector_store = ATDFVectorStore(db_path=self.db_path)

        # Mock del método search_tools
        async def mock_search_tools(query, options=None):
            if query == "enviar email":
                return [SAMPLE_TOOLS[0]]
            return []

        vector_store.search_tools = mock_search_tools

        # Ejecutar y verificar un caso exitoso
        result = vector_store.find_best_tool_sync("enviar email")
        self.assertIsNotNone(result)
        self.assertEqual(result["tool_id"], "test_tool_1")

        # Ejecutar y verificar un caso sin resultados
        result = vector_store.find_best_tool_sync("algo inexistente")
        self.assertIsNone(result)

    @mock.patch("sdk.vector_search.vector_store.lancedb.connect")
    def test_count_tools(self, mock_connect):
        """Probar el conteo de herramientas en la tabla."""
        mock_db = mock.MagicMock()
        mock_connect.return_value = mock_db
        mock_table = mock.MagicMock()
        mock_db.open_table.return_value = mock_table
        mock_table.count_rows.return_value = 3

        vector_store = ATDFVectorStore(db_path=self.db_path)
        vector_store.initialized = True
        vector_store.db = mock_db
        vector_store.table = mock_table

        count = vector_store.count_tools_sync()
        self.assertEqual(count, 3)


class TestVectorSearchIntegration(unittest.TestCase):
    """Pruebas de integración para la búsqueda vectorial con ATDFToolbox"""

    def setUp(self):
        """Configuración para las pruebas"""
        # Crear directorio temporal para la base de datos
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_vector_db")

        # Crear toolbox con herramientas de prueba
        self.toolbox = ATDFToolbox()
        for tool_data in SAMPLE_TOOLS:
            self.toolbox.add_tool(tool_data)

    def tearDown(self):
        """Limpieza después de las pruebas"""
        shutil.rmtree(self.test_dir)

    @mock.patch.object(ATDFVectorStore, "search_tools_sync")
    def test_find_tools_with_vector_search(self, mock_search_tools):
        """Probar la integración de búsqueda vectorial en ATDFToolbox"""

        mock_search_tools.return_value = [dict(SAMPLE_TOOLS[0], score=0.85)]

        # Crear vector store
        vector_store = ATDFVectorStore(db_path=self.db_path)

        # Asignar a toolbox
        self.toolbox.set_vector_store(vector_store)

        # Ejecutar búsqueda con vector_search=True
        results = self.toolbox.find_tools_by_text(
            "enviar mensaje", use_vector_search=True
        )

        # Verificar
        self.assertEqual(len(results), 1)
        tool, score = results[0]
        self.assertEqual(tool.tool_id, "test_tool_1")
        self.assertIsInstance(score, float)
        mock_search_tools.assert_called_once()

    @mock.patch.object(ATDFVectorStore, "search_tools_sync")
    def test_select_tool_for_task_with_vector_search(self, mock_search_tools):
        """Probar la selección de herramientas con búsqueda vectorial"""

        mock_search_tools.return_value = [dict(SAMPLE_TOOLS[2], score=0.92)]

        # Crear vector store
        vector_store = ATDFVectorStore(db_path=self.db_path)

        # Asignar a toolbox
        self.toolbox.set_vector_store(vector_store)

        # Ejecutar selección con vector_search=True
        tool = self.toolbox.select_tool_for_task(
            "traducir un texto", use_vector_search=True
        )

        # Verificar
        self.assertIsNotNone(tool)
        self.assertEqual(tool.tool_id, "test_tool_3")
        mock_search_tools.assert_called_once()

    @mock.patch.object(ATDFVectorStore, "search_tools_sync")
    def test_fallback_to_normal_search(self, mock_search_tools):
        """Probar que hay fallback a búsqueda normal si la vectorial falla"""

        mock_search_tools.side_effect = RuntimeError("Error simulado en búsqueda vectorial")

        # Crear vector store
        vector_store = ATDFVectorStore(db_path=self.db_path)

        # Asignar a toolbox
        self.toolbox.set_vector_store(vector_store)

        # Ejecutar búsqueda con vector_search=True, debería caer en fallback
        results = self.toolbox.find_tools_by_text("correo", use_vector_search=True)

        # Verificar que encontró resultados usando la búsqueda normal
        self.assertTrue(len(results) > 0)
        # Verificar que al menos uno de los resultados es sobre correo
        has_email_tool = any(tool.tool_id == "test_tool_1" for tool, _ in results)
        self.assertTrue(all(isinstance(score, float) for _, score in results))
        self.assertTrue(has_email_tool)
        mock_search_tools.assert_called_once()

    def test_find_tools_without_scores_for_legacy_consumers(self):
        """Permite recuperar solo herramientas para código legado."""

        results = self.toolbox.find_tools_by_text(
            "correo",
            use_vector_search=False,
            return_scores=False,
        )

        self.assertTrue(results)
        self.assertTrue(all(isinstance(tool, ATDFTool) for tool in results))


if __name__ == "__main__":
    unittest.main()
