import pytest

import app as modulo_app


@pytest.fixture
def client(tmp_path):
    # Base de datos temporal: no toca avistamientos.db
    modulo_app.DB = str(tmp_path / "test.db")
    modulo_app.init_db()
    modulo_app.app.config["TESTING"] = True
    with modulo_app.app.test_client() as c:
        yield c


AVISTAMIENTO = {
    "especie": "colibri",
    "lugar": "Parque Simon Bolivar",
    "fecha": "2026-10-12",
    "observador": "Ana",
}


def test_listar_vacio(client):
    r = client.get("/avistamientos")
    assert r.status_code == 200
    assert r.get_json() == []


def test_crear_devuelve_201(client):
    r = client.post("/avistamientos", json=AVISTAMIENTO)
    assert r.status_code == 201
    assert r.get_json()["id"] == 1
    assert r.get_json()["especie"] == "colibri"


def test_crear_incompleto_devuelve_400(client):
    r = client.post("/avistamientos", json={"especie": "colibri"})
    assert r.status_code == 400


def test_ver_existente_y_no_existente(client):
    client.post("/avistamientos", json=AVISTAMIENTO)
    assert client.get("/avistamientos/1").status_code == 200
    assert client.get("/avistamientos/999").status_code == 404


def test_actualizar(client):
    client.post("/avistamientos", json=AVISTAMIENTO)
    nuevo = {**AVISTAMIENTO, "lugar": "Jardin Botanico"}
    r = client.put("/avistamientos/1", json=nuevo)
    assert r.status_code == 200
    assert r.get_json()["lugar"] == "Jardin Botanico"
    assert client.put("/avistamientos/1", json={"especie": "x"}).status_code == 400
    assert client.put("/avistamientos/999", json=nuevo).status_code == 404


def test_eliminar(client):
    client.post("/avistamientos", json=AVISTAMIENTO)
    assert client.delete("/avistamientos/1").status_code == 204
    assert client.delete("/avistamientos/1").status_code == 404
    assert client.get("/avistamientos").get_json() == []


def test_resumen(client):
    client.post("/avistamientos", json=AVISTAMIENTO)
    client.post("/avistamientos", json=AVISTAMIENTO)
    client.post("/avistamientos", json={**AVISTAMIENTO, "especie": "condor"})
    r = client.get("/avistamientos/resumen")
    assert r.status_code == 200
    conteo = {f["especie"]: f["total"] for f in r.get_json()}
    assert conteo == {"colibri": 2, "condor": 1}

def test_especie_reutiliza_la_existente(client):
    client.post("/avistamientos", json={**AVISTAMIENTO, "especie": "Cóndor"})
    r = client.post("/avistamientos", json={**AVISTAMIENTO, "especie": "  CONDOR "})
    assert r.get_json()["especie"] == "cóndor"
    client.post("/avistamientos", json={**AVISTAMIENTO, "especie": "condor andino"})
    r = client.get("/avistamientos/resumen")
    conteo = {f["especie"]: f["total"] for f in r.get_json()}
    assert conteo == {"cóndor": 2, "condor andino": 1}

@pytest.mark.parametrize("fecha", ["12-10-2026", "2026-1-5", "2026-02-30", "ayer", "2026-13-01"])
def test_fecha_invalida_devuelve_400(client, fecha):
    r = client.post("/avistamientos", json={**AVISTAMIENTO, "fecha": fecha})
    assert r.status_code == 400


def test_fecha_invalida_en_put_devuelve_400(client):
    client.post("/avistamientos", json=AVISTAMIENTO)
    r = client.put("/avistamientos/1", json={**AVISTAMIENTO, "fecha": "12/10/2026"})
    assert r.status_code == 400