#!/usr/bin/env python3
"""
Script para importar workflows de n8n automáticamente usando la API REST
"""

import json
import requests
import os
from pathlib import Path

# Configuración
N8N_BASE_URL = "http://localhost:5678"
WORKFLOWS_DIR = "n8n-workflows"

def import_workflow(workflow_file_path):
    """Importa un workflow a n8n"""
    try:
        # Leer el archivo JSON del workflow
        with open(workflow_file_path, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        
        # Preparar los datos para la API de n8n
        import_data = {
            "workflow": workflow_data
        }
        
        # Hacer la petición POST a n8n
        response = requests.post(
            f"{N8N_BASE_URL}/api/v1/workflows",
            json=import_data,
            headers={
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 201:
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
        response = requests.get(f"{N8N_BASE_URL}/api/v1/workflows")
        if response.status_code != 200:
            print(f"❌ n8n no está accesible en {N8N_BASE_URL}")
            return
    except requests.exceptions.ConnectionError:
        print(f"❌ No se puede conectar a n8n en {N8N_BASE_URL}")
        print("   Asegúrate de que n8n esté corriendo")
        return
    
    # Buscar archivos de workflow
    workflows_path = Path(WORKFLOWS_DIR)
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
    
    print(f"\n🎉 Importación completada: {success_count}/{len(workflow_files)} workflows importados exitosamente")
    
    if success_count > 0:
        print(f"\n🌐 Puedes ver los workflows en: {N8N_BASE_URL}")

if __name__ == "__main__":
    main()