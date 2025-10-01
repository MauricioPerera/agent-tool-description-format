#!/usr/bin/env python3
import os
import sqlite3

DB_DIR = r"C:\Users\Rckflr\.n8n"
DB_CANDIDATES = [
    "database.sqlite",
    "n8n.sqlite",
    "database.db",
    "n8n.db",
]

def find_db_path():
    for name in DB_CANDIDATES:
        p = os.path.join(DB_DIR, name)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"No se encontró base de datos en {DB_DIR}")

def query_workflow_id(db_path, name_like):
    con = sqlite3.connect(db_path)
    try:
        cur = con.cursor()
        cur.execute(
            "SELECT id, name FROM workflow_entity WHERE name LIKE ? ORDER BY updatedAt DESC",
            (f"%{name_like}%",),
        )
        rows = cur.fetchall()
        return rows
    finally:
        con.close()

def main():
    db_path = find_db_path()
    print(f"DB encontrada: {db_path}")
    targets = [
        "Complete Travel Booking via ATDF-MCP",
        "Travel Booking",
        "ATDF-MCP",
    ]
    for t in targets:
        rows = query_workflow_id(db_path, t)
        if rows:
            print("Resultados:")
            for r in rows:
                print(f" - id={r[0]} name={r[1]}")
            return
    print("No se encontró el workflow por nombre. Exporta y revisa manualmente.")

if __name__ == "__main__":
    main()