import sqlite3
import unicodedata
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)
DB = "avistamientos.db"
CAMPOS = ["especie", "lugar", "fecha", "observador"]

def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def datos_validos(datos):
    return (
        bool(datos)
        and all(isinstance(datos.get(c), str) and datos[c].strip() for c in CAMPOS)
        and fecha_valida(datos["fecha"])
    )

def fecha_valida(texto):
    try:
        datetime.strptime(texto, "%Y-%m-%d")
    except ValueError:
        return False
    return len(texto) == 10

def clave_especie(texto):
    """Clave de comparación: sin tildes, minúsculas y espacios simples."""
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    return " ".join(sin_tildes.lower().split())


def especie_canonica(conn, texto):
    """Si la especie ya existe (ignorando tildes/mayúsculas/espacios), usa la guardada."""
    clave = clave_especie(texto)
    for fila in conn.execute("SELECT DISTINCT especie FROM avistamientos"):
        if clave_especie(fila["especie"]) == clave:
            return fila["especie"]
    return " ".join(texto.lower().split())

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS avistamientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                especie TEXT NOT NULL,
                lugar TEXT NOT NULL,
                fecha TEXT NOT NULL,
                observador TEXT NOT NULL
            )
        """)


@app.get("/avistamientos")
def listar():
    with get_conn() as conn:
        filas = conn.execute("SELECT * FROM avistamientos").fetchall()
    return jsonify([dict(f) for f in filas]), 200

@app.post("/avistamientos")
def crear():
    datos = request.get_json(silent=True)
    if not datos_validos(datos):
     return jsonify({"error": "Se requieren: especie, lugar, fecha (AAAA-MM-DD) y observador"}), 400
    with get_conn() as conn:
        especie = especie_canonica(conn, datos["especie"])
        cur = conn.execute(
            "INSERT INTO avistamientos (especie, lugar, fecha, observador) VALUES (?, ?, ?, ?)",
            (especie, datos["lugar"], datos["fecha"], datos["observador"]),
        )
        fila = conn.execute(
            "SELECT * FROM avistamientos WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
    return jsonify(dict(fila)), 201

@app.get("/avistamientos/<int:id>")
def ver(id):
    with get_conn() as conn:
        fila = conn.execute(
            "SELECT * FROM avistamientos WHERE id = ?", (id,)
        ).fetchone()
    if fila is None:
        return jsonify({"error": "Avistamiento no encontrado"}), 404
    return jsonify(dict(fila)), 200

@app.get("/avistamientos/resumen")
def resumen():
    with get_conn() as conn:
        filas = conn.execute(
            "SELECT especie, COUNT(*) AS total FROM avistamientos GROUP BY especie"
        ).fetchall()
    return jsonify([dict(f) for f in filas]), 200

@app.put("/avistamientos/<int:id>")
def actualizar(id):
    datos = request.get_json(silent=True)
    if not datos_validos(datos):
     return jsonify({"error": "Se requieren: especie, lugar, fecha (AAAA-MM-DD) y observador"}), 400
    with get_conn() as conn:
        especie = especie_canonica(conn, datos["especie"])
        cur = conn.execute(
            "UPDATE avistamientos SET especie = ?, lugar = ?, fecha = ?, observador = ? WHERE id = ?",
            (especie, datos["lugar"], datos["fecha"], datos["observador"], id),
        )
        if cur.rowcount == 0:
            return jsonify({"error": "Avistamiento no encontrado"}), 404
        fila = conn.execute(
            "SELECT * FROM avistamientos WHERE id = ?", (id,)
        ).fetchone()
    return jsonify(dict(fila)), 200

@app.delete("/avistamientos/<int:id>")
def eliminar(id):
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM avistamientos WHERE id = ?", (id,))
    if cur.rowcount == 0:
        return jsonify({"error": "Avistamiento no encontrado"}), 404
    return "", 204
    
if __name__ == "__main__":
    init_db()
    app.run(debug=True)