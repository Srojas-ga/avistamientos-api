from datetime import date, datetime

CAMPOS = ["especie", "lugar", "fecha", "observador"]
ESPECIE_MIN = 3
ESPECIE_MAX = 50


class RelojSistema:
    """Reloj real. En las pruebas se reemplaza por uno fijo."""

    def hoy(self):
        return date.today()


class ValidadorDeAvistamiento:
    def __init__(self, reloj=None):
        self.reloj = reloj or RelojSistema()

    def validar(self, datos):
        """Devuelve una lista de errores. Lista vacía = avistamiento válido."""
        if not isinstance(datos, dict):
            return ["cuerpo: debe ser un JSON con especie, lugar, fecha y observador"]

        errores = []
        for campo in CAMPOS:
            valor = datos.get(campo)
            if not isinstance(valor, str) or not valor.strip():
                errores.append(f"{campo}: es obligatorio y debe ser texto")
            elif campo == "especie":
                error = self._error_especie(valor)
                if error:
                    errores.append(error)
            elif campo == "fecha":
                error = self._error_fecha(valor)
                if error:
                    errores.append(error)
        return errores

    def _error_especie(self, texto):
        largo = len(texto.strip())
        if largo < ESPECIE_MIN or largo > ESPECIE_MAX:
            return f"especie: debe tener entre {ESPECIE_MIN} y {ESPECIE_MAX} caracteres"
        return None

    def _error_fecha(self, texto):
        try:
            fecha = datetime.strptime(texto, "%Y-%m-%d").date()
        except ValueError:
            return "fecha: debe ser una fecha real con formato AAAA-MM-DD"
        if len(texto) != 10:
            return "fecha: debe tener formato AAAA-MM-DD (con ceros)"
        if fecha > self.reloj.hoy():
            return "fecha: no puede ser posterior a hoy"
        return None