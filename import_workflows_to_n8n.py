#!/usr/bin/env python3
"""
Script para importar workflows de n8n automáticamente usando la API REST
"""

import json
import os
from pathlib import Path

import requests

# Configuración
N8N_BASE_URL = "http://localhost:5678"
WORKFLOWS_DIR = "n8n-workflows"
WORKFLOW_FILE = os.environ.get("WORKFLOW_FILE")
N8N_API_KEY = os.environ.get("N8N_API_KEY")


def import_workflow(workflow_file_path):
    """Importa un workflow a n8n"""
    try:
        # Leer el archivo JSON del workflow
        with open(workflow_file_path, "r", encoding="utf-8") as f:
            workflow_data = json.load(f)

        # Preparar los datos para la API de n8n: el endpoint de creación
        # espera únicamente propiedades permitidas (p.ej. name, nodes, connections, settings)
        allowed_keys = {"name", "nodes", "connections", "settings"}
        import_data = {k: v for k, v in workflow_data.items() if k in allowed_keys}

        # Hacer la petición POST a n8n
        headers = {"Content-Type": "application/json"}
        if N8N_API_KEY:
            headers["X-N8N-API-KEY"] = N8N_API_KEY

        response = requests.post(
            f"{N8N_BASE_URL}/api/v1/workflows", json=import_data, headers=headers
        )

        if response.status_code in (200, 201):
            result = response.json()
            print(f"✅ Workflow '{workflow_data['name']}' importado exitosamente")
            print(f"   ID: {result.get('id', 'N/A')}")
            return True
        else:
            print(f"❌ Error importando '{workflow_data['name']}':")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error procesando {workflow_file_path}: {str(e)}")
        return False


def main():
    """Función principal"""
    print("🚀 Importando workflows a n8n...")
    print(f"📍 n8n URL: {N8N_BASE_URL}")

    # Verificar que n8n esté corriendo
    try:
        headers = {"Content-Type": "application/json"}
        if N8N_API_KEY:
            headers["X-N8N-API-KEY"] = N8N_API_KEY
        response = requests.get(f"{N8N_BASE_URL}/api/v1/workflows", headers=headers)
        if response.status_code != 200:
            print(f"❌ n8n no está accesible en {N8N_BASE_URL}")
            return
    except requests.exceptions.ConnectionError:
        print(f"❌ No se puede conectar a n8n en {N8N_BASE_URL}")
        print("   Asegúrate de que n8n esté corriendo")
        return

    # Buscar archivos de workflow
    workflows_path = Path(WORKFLOWS_DIR)
    if WORKFLOW_FILE:
        # Importar solo un archivo específico
        wf_path = Path(WORKFLOW_FILE)
        if not wf_path.exists():
            print(f"❌ Archivo específico no encontrado: {WORKFLOW_FILE}")
            return
        workflow_files = [wf_path]
    else:
        if not workflows_path.exists():
            print(f"❌ Directorio {WORKFLOWS_DIR} no encontrado")
            return
        workflow_files = list(workflows_path.glob("*.json"))
        if not workflow_files:
            print(f"❌ No se encontraron archivos .json en {WORKFLOWS_DIR}")
            return

    print(f"📁 Encontrados {len(workflow_files)} workflows para importar")

    # Importar cada workflow
    success_count = 0
    for workflow_file in workflow_files:
        print(f"\n📄 Procesando: {workflow_file.name}")
        if import_workflow(workflow_file):
            success_count += 1

    print(
        f"\n🎉 Importación completada: {success_count}/{len(workflow_files)} workflows importados exitosamente"
    )

    if success_count > 0:
        print(f"\n🌐 Puedes ver los workflows en: {N8N_BASE_URL}")


if __name__ == "__main__":
    main()
