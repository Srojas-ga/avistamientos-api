# API de Avistamientos de Aves

API REST para registrar avistamientos de aves. Taller API REST de Ingeniería de Software 2.

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

## Modelo: avistamiento

| Campo | Descripción |
|---|---|
| `id` | Lo asigna el sistema |
| `especie` | Nombre de la especie (ej. "colibri") |
| `lugar` | Dónde se observó |
| `fecha` | Texto AAAA-MM-DD; si el formato o la fecha no es válido, la API responde 400 |
| `observador` | Quién lo registró |

La `especie` se compara ignorando mayúsculas, tildes y espacios sobrantes: si ya existe una especie registrada (por ejemplo "condor"), "Cóndor" o " CONDOR " se guardan con ese mismo nombre. Un nombre distinto como "condor andino" cuenta como otra especie. Si la especie es nueva, se guarda en minúsculas y con los espacios arreglados.

## Endpoints

| Método | Ruta | Respuesta |
|---|---|---|
| GET | `/avistamientos` | 200 con la lista |
| GET | `/avistamientos/{id}` | 200, o 404 si no existe |
| POST | `/avistamientos` | 201 con el creado, o 400 si faltan datos o la fecha es inválida |
| PUT | `/avistamientos/{id}` | 200, 400 si faltan datos o la fecha es inválida, o 404 si no existe |
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
  -d '{"especie":"colibri","lugar":"Parque Simon Bolivar","fecha":"12-10-2026","observador":"Ana"}'
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

```bash
python -m pytest -v
```

Son 14 pruebas (endpoints, códigos de estado, validación de fecha y normalización de especie). se usa una base de datos temporal, no tocan `avistamientos.db`.

## Herramientas de desarrollo

- Pruebas manuales con la extensión REST Client de Visual Studio Code (`peticiones.http`).

## Uso de IA

Se usó **Claude (Anthropic), modelo Claude Sonnet 5.5**, como ayuda para Crear lo que fue el archivo de pruebas, para ayudar con la identificacion de tildes, mayusculas y minusculas y espacios en el apartado de la creacio de avistamiento y su especie, tambien aconsejo como probar con peticiones y no creando una vista compleja y tambien el uso de un archivo JSON para crear datos para la Base de Datos>

## Limitaciones conocidas

- La especie no corrige errores de ortografía: "cndor" cuenta como otra especie.
- Si una especie se registró primero con tilde (o sin ella), las siguientes variantes se guardan con esa misma escritura.