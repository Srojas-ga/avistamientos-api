# API de Avistamientos de Aves

API REST para registrar avistamientos de aves. Taller API REST y Taller de pruebas de Ingeniería de Software 2.

Hecha con **Python 3 + Flask + SQLite** (la base de datos es el archivo `avistamientos.db`, que se crea sola al ejecutar).

## Requisitos

- Python 3.10 o superior

## Instalación y ejecución

```bash
# 1. Clonar el repositorio
git clone https://github.com/Srojas-ga/avistamientos-api
cd avistamientos-api

# 2. Crear y activar el entorno virtual
python -m venv venv
# Windows (PowerShell):
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la API
python app.py
```

La API queda en `http://127.0.0.1:5000`.

## Estructura del proyecto

```
avistamientos-api/
├── app.py                    # endpoints y acceso a la base de datos
├── validador.py              # regla de negocio (ValidadorDeAvistamiento y reloj)
├── requirements.txt          # dependencias
├── peticiones.http           # pruebas manuales (REST Client de VS Code)
├── cobertura.txt             # reporte de cobertura
└── tests/
    ├── test_validador.py     # pruebas unitarias del validador
    ├── test_integracion.py   # pruebas de integración por HTTP
    └── test_api.py           # pruebas de los endpoints
```

## Modelo: avistamiento

| Campo | Descripción |
|---|---|
| `id` | Lo asigna el sistema |
| `especie` | Nombre de la especie, entre 3 y 50 caracteres (ej. "colibri") |
| `lugar` | Dónde se observó, texto no vacío |
| `fecha` | Texto AAAA-MM-DD, debe ser una fecha real y no posterior a hoy |
| `observador` | Quién lo registró, texto no vacío |

## Regla de negocio

Un avistamiento es válido si:

- La especie tiene entre 3 y 50 caracteres (sin contar espacios al inicio y al final).
- La fecha es real, tiene el formato AAAA-MM-DD y no es posterior a hoy.
- El lugar y el observador son texto no vacío.

Si no es válido, POST y PUT responden 400 con una lista de mensajes que indica qué campo falló. Por ejemplo:

```json
{"error": ["especie: debe tener entre 3 y 50 caracteres", "fecha: no puede ser posterior a hoy"]}
```

La validación vive en la clase `ValidadorDeAvistamiento` (`validador.py`), separada del controlador.

La `especie` se compara ignorando mayúsculas, tildes y espacios sobrantes: si ya existe una especie registrada (por ejemplo "condor"), "Cóndor" o " CONDOR " se guardan con ese mismo nombre. Un nombre distinto como "condor andino" cuenta como otra especie. Si la especie es nueva, se guarda en minúsculas y con los espacios arreglados.

## Endpoints

| Método | Ruta | Respuesta |
|---|---|---|
| GET | `/avistamientos` | 200 con la lista |
| GET | `/avistamientos/{id}` | 200, o 404 si no existe |
| POST | `/avistamientos` | 201 con el creado, o 400 si el avistamiento no es válido |
| PUT | `/avistamientos/{id}` | 200, 400 si el avistamiento no es válido, o 404 si no existe |
| DELETE | `/avistamientos/{id}` | 204, o 404 si no existe |
| GET | `/avistamientos/resumen` | 200 con el conteo por especie (bonus) |

## Ejemplos con curl

Los ejemplos usan sintaxis de Linux/Mac/Git Bash. En PowerShell de Windows, usa `curl.exe` y escribe el JSON en un archivo (por ejemplo `datos.json`) con `-d "@datos.json"`.

**Listar**
```bash
curl -i http://127.0.0.1:5000/avistamientos
```

**Ver uno**
```bash
curl -i http://127.0.0.1:5000/avistamientos/1
```

**Registrar**
```bash
curl -i -X POST http://127.0.0.1:5000/avistamientos \
  -H "Content-Type: application/json" \
  -d '{"especie":"colibri","lugar":"Parque Simon Bolivar","fecha":"2026-10-12","observador":"Ana"}'
```

**Registrar con datos inválidos (responde 400)**
```bash
curl -i -X POST http://127.0.0.1:5000/avistamientos \
  -H "Content-Type: application/json" \
  -d '{"especie":"ab","lugar":"Parque Simon Bolivar","fecha":"12-10-2026","observador":"Ana"}'
```

**Actualizar**
```bash
curl -i -X PUT http://127.0.0.1:5000/avistamientos/1 \
  -H "Content-Type: application/json" \
  -d '{"especie":"colibri","lugar":"Jardin Botanico","fecha":"2026-10-13","observador":"Ana"}'
```

**Eliminar**
```bash
curl -i -X DELETE http://127.0.0.1:5000/avistamientos/1
```

**Resumen por especie (bonus)**
```bash
curl -i http://127.0.0.1:5000/avistamientos/resumen
```

## Pruebas

Para correr todas las pruebas:

```bash
python -m pytest -v
```

Son 47 pruebas:

- 21 unitarias del validador (`tests/test_validador.py`), con partición de equivalencia, valores límite y un `RelojFijo` (stub) para fijar la fecha de hoy.
- 12 de integración por HTTP (`tests/test_integracion.py`), sobre SQLite real y temporal.
- 14 de los endpoints (`tests/test_api.py`).

Todas usan una base de datos temporal y no tocan `avistamientos.db`.

## Cobertura

Para generar la cobertura (líneas y ramas) y ver qué quedó sin cubrir:

```bash
python -m pytest --cov=app --cov=validador --cov-branch --cov-report=term-missing
```

Para guardar el reporte en un archivo:

```bash
python -m pytest --cov=app --cov=validador --cov-branch --cov-report=term-missing > cobertura.txt
```

Resultado actual: 98% en total (97% en `app.py` y 100% en `validador.py`). Lo único sin cubrir es el bloque de arranque `if __name__ == "__main__"`.

## Herramientas de desarrollo

- Pruebas manuales con la extensión REST Client de Visual Studio Code (`peticiones.http`).
- pytest y pytest-cov para las pruebas y la cobertura.

## Uso de IA

Se usó **Claude (Anthropic), modelo Claude Sonnet 5.5**, como ayuda para crear el archivo de pruebas, para ayudar con la identificacion de tildes, mayusculas y minusculas y espacios en el apartado de la creacion de avistamiento y su especie, tambien aconsejo como probar con peticiones y no creando una vista compleja y tambien el uso de un archivo JSON para crear datos para la Base de Datos, tambien para verificacion de que los metodos creados estuvieran bien hechos y tambien agregar los cambios ya mencionados en cuanto a la especie.

En el taller de pruebas también ayudó a extraer la validación a `validador.py`, a elegir los casos de prueba con partición y valores límite, a escribir las pruebas unitarias y de integración, a usar la cobertura y a estructurar el documento de justificación.

## Limitaciones conocidas

- La especie no corrige errores de ortografía: "cndor" cuenta como otra especie.
- Si una especie se registró primero con tilde (o sin ella), las siguientes variantes se guardan con esa misma escritura.