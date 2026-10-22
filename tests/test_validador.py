from datetime import date

import pytest

from validador import ValidadorDeAvistamiento


class RelojFijo:
    """Stub: siempre dice que hoy es 21 de octubre de 2026."""

    def hoy(self):
        return date(2026, 10, 21)


def avistamiento(**cambios):
    base = {
        "especie": "colibri",
        "lugar": "Parque",
        "fecha": "2026-10-20",
        "observador": "Ana",
    }
    return {**base, **cambios}


@pytest.fixture
def validador():
    return ValidadorDeAvistamiento(reloj=RelojFijo())


# ---------- Especie ----------

def test_especie_vacia_es_invalida(validador):
    # Arrange
    datos = avistamiento(especie="")

    # Act
    errores = validador.validar(datos)

    # Assert
    assert any(e.startswith("especie") for e in errores)


@pytest.mark.parametrize("especie", ["ab", "  ab  "])
def test_especie_de_2_caracteres_es_invalida(validador, especie):
    # Arrange
    datos = avistamiento(especie=especie)

    # Act
    errores = validador.validar(datos)

    # Assert
    assert any(e.startswith("especie") for e in errores)


@pytest.mark.parametrize("especie", ["abc", "colibri", "a" * 50])
def test_especie_entre_3_y_50_es_valida(validador, especie):
    # Arrange
    datos = avistamiento(especie=especie)

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == []


def test_especie_de_51_caracteres_es_invalida(validador):
    # Arrange
    datos = avistamiento(especie="a" * 51)

    # Act
    errores = validador.validar(datos)

    # Assert
    assert any(e.startswith("especie") for e in errores)


# ---------- Fecha (usa el reloj fijo: hoy = 2026-10-21) ----------

@pytest.mark.parametrize("fecha", ["2026-10-20", "2026-10-21"])
def test_fecha_de_ayer_y_de_hoy_es_valida(validador, fecha):
    # Arrange
    datos = avistamiento(fecha=fecha)

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == []


def test_fecha_de_manana_es_invalida(validador):
    # Arrange
    datos = avistamiento(fecha="2026-10-22")

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == ["fecha: no puede ser posterior a hoy"]


@pytest.mark.parametrize("fecha", ["12-10-2026", "2026-1-5", "2026-02-30"])
def test_fecha_con_formato_incorrecto_es_invalida(validador, fecha):
    # Arrange
    datos = avistamiento(fecha=fecha)

    # Act
    errores = validador.validar(datos)

    # Assert
    assert any(e.startswith("fecha") for e in errores)


# ---------- Lugar, observador y tipos ----------

@pytest.mark.parametrize("campo", ["lugar", "observador"])
@pytest.mark.parametrize("valor", ["", "   "])
def test_lugar_y_observador_vacios_son_invalidos(validador, campo, valor):
    # Arrange
    datos = avistamiento(**{campo: valor})

    # Act
    errores = validador.validar(datos)

    # Assert
    assert any(e.startswith(campo) for e in errores)


def test_campo_que_no_es_texto_es_invalido(validador):
    # Arrange
    datos = avistamiento(lugar=123)

    # Act
    errores = validador.validar(datos)

    # Assert
    assert any(e.startswith("lugar") for e in errores)


def test_observador_ausente_es_invalido(validador):
    # Arrange
    datos = avistamiento()
    del datos["observador"]

    # Act
    errores = validador.validar(datos)

    # Assert
    assert any(e.startswith("observador") for e in errores)


def test_avistamiento_completo_y_correcto_no_tiene_errores(validador):
    # Arrange
    datos = avistamiento()

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores == []


def test_cuerpo_que_no_es_json_objeto_es_invalido(validador):
    # Arrange
    datos = None

    # Act
    errores = validador.validar(datos)

    # Assert
    assert errores != []