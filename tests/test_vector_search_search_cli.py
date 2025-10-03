"""Pruebas para la CLI de búsqueda vectorial de ATDF."""

import asyncio
import sys
from pathlib import Path
from unittest import mock, TestCase


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from sdk.vector_search.search_cli import ATDFSearchCLI  # noqa: E402


class TestATDFSearchCLI(TestCase):
    """Pruebas mínimas para detectar cambios de firma en la CLI."""

    def test_initialize_uses_table_name_argument(self) -> None:
        """La inicialización debe usar el argumento soportado ``table_name``."""

        cli = ATDFSearchCLI()
        self.assertEqual(cli.table_name, "atdf_tools")

        vector_store_instance = mock.MagicMock()
        vector_store_instance.initialize = mock.AsyncMock(return_value=True)

        with mock.patch(
            "sdk.vector_search.search_cli.ATDFVectorStore",
            return_value=vector_store_instance,
        ) as mock_store_cls:
            result = asyncio.run(cli.initialize())

        self.assertTrue(result)
        mock_store_cls.assert_called_once_with(
            db_path=cli.db_path,
            model_name=cli.model_name,
            table_name=cli.table_name,
        )
        vector_store_instance.initialize.assert_awaited()
