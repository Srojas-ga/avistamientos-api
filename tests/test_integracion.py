import pytest

import app as modulo_app

AVISTAMIENTO = {
    "especie": "colibri",
    "lugar": "Parque Simon Bolivar",
    "fecha": "2026-10-12",
    "observador": "Ana",
}


@pytest.fixture
def client(tmp_path):
    # Base de datos temporal y vacía para cada prueba
    modulo_app.DB = str(tmp_path / "integracion.db")
    modulo_app.init_db()
    modulo_app.app.config["TESTING"] = True
    with modulo_app.app.test_client() as c:
        yield c


# ---------- GET /avistamientos ----------

def test_listar_devuelve_los_avistamientos_creados(client):
    # Arrange
    client.post("/avistamientos", json=AVISTAMIENTO)

    # Act
    r = client.get("/avistamientos")

    # Assert
    assert r.status_code == 200
    lista = r.get_json()
    assert len(lista) == 1
    assert lista[0]["especie"] == "colibri"


# ---------- POST /avistamientos ----------

def test_crear_devuelve_201_y_el_avistamiento_completo(client):
    # Act
    r = client.post("/avistamientos", json=AVISTAMIENTO)

    # Assert
    assert r.status_code == 201
    assert r.get_json() == {"id": 1, **AVISTAMIENTO}


def test_crear_y_luego_ver_por_id_devuelve_el_mismo_avistamiento(client):
    # Arrange
    creado = client.post("/avistamientos", json=AVISTAMIENTO).get_json()

    # Act
    r = client.get(f"/avistamientos/{creado['id']}")

    # Assert
    assert r.status_code == 200
    assert r.get_json() == creado


def test_crear_con_datos_invalidos_devuelve_400_y_dice_que_campo_fallo(client):
    # Arrange
    datos = {**AVISTAMIENTO, "especie": "ab"}

    # Act
    r = client.post("/avistamientos", json=datos)

    # Assert
    assert r.status_code == 400
    assert any(e.startswith("especie") for e in r.get_json()["error"])


def test_crear_con_datos_invalidos_no_guarda_nada(client):
    # Arrange
    datos = {**AVISTAMIENTO, "especie": "ab"}

    # Act
    client.post("/avistamientos", json=datos)

    # Assert
    assert client.get("/avistamientos").get_json() == []


# ---------- GET /avistamientos/{id} ----------

def test_ver_id_inexistente_devuelve_404_con_mensaje(client):
    # Act
    r = client.get("/avistamientos/999")

    # Assert
    assert r.status_code == 404
    assert r.get_json() == {"error": "Avistamiento no encontrado"}


# ---------- PUT /avistamientos/{id} ----------

def test_actualizar_cambia_los_datos_y_se_ven_al_consultar(client):
    # Arrange
    client.post("/avistamientos", json=AVISTAMIENTO)
    nuevo = {**AVISTAMIENTO, "lugar": "Jardin Botanico"}

    # Act
    r = client.put("/avistamientos/1", json=nuevo)

    # Assert
    assert r.status_code == 200
    assert r.get_json() == {"id": 1, **nuevo}
    assert client.get("/avistamientos/1").get_json()["lugar"] == "Jardin Botanico"


def test_actualizar_con_datos_invalidos_devuelve_400_y_no_cambia_nada(client):
    # Arrange
    client.post("/avistamientos", json=AVISTAMIENTO)
    malo = {**AVISTAMIENTO, "fecha": "2099-01-01"}

    # Act
    r = client.put("/avistamientos/1", json=malo)

    # Assert
    assert r.status_code == 400
    assert client.get("/avistamientos/1").get_json()["fecha"] == "2026-10-12"


def test_actualizar_id_inexistente_devuelve_404(client):
    # Act
    r = client.put("/avistamientos/999", json=AVISTAMIENTO)

    # Assert
    assert r.status_code == 404


# ---------- DELETE /avistamientos/{id} ----------

def test_eliminar_devuelve_204_y_luego_el_id_da_404(client):
    # Arrange
    client.post("/avistamientos", json=AVISTAMIENTO)

    # Act
    r = client.delete("/avistamientos/1")

    # Assert
    assert r.status_code == 204
    assert client.get("/avistamientos/1").status_code == 404


def test_eliminar_id_inexistente_devuelve_404(client):
    # Act
    r = client.delete("/avistamientos/999")

    # Assert
    assert r.status_code == 404


def test_conexion_revierte_los_cambios_si_ocurre_un_error(client):
    # Arrange: un INSERT seguido de un fallo simulado dentro del with
    with pytest.raises(RuntimeError):
        with modulo_app.get_conn() as conn:
            conn.execute(
                "INSERT INTO avistamientos (especie, lugar, fecha, observador) "
                "VALUES ('colibri', 'Parque', '2026-10-12', 'Ana')"
            )

            # Act
            raise RuntimeError("fallo simulado")

    # Assert: el INSERT se deshizo, no quedó nada guardado
    assert client.get("/avistamientos").get_json() == []