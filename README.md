# MCP Student Server

Un servidor MCP (Model Context Protocol) para gestionar información de cursos y tareas de estudiantes. Proporciona herramientas para consultar cursos, filtrar por semana o código de curso, y generar archivos ICS para integración con calendarios.

## 🚀 Características

- **Recursos MCP**: Acceso a información de cursos por estudiante
- **Herramientas MCP**:
  - `get_filtered_courses`: Consulta y filtra cursos por código y/o semana
  - `build_ics_file`: Genera archivos ICS para importar tareas al calendario
- **API REST**: Endpoints FastAPI para integración web
- **Inspector MCP**: Compatible con herramientas de inspección MCP

## 📋 Requisitos

- Python 3.8 o superior
- Conda (recomendado para gestión de entornos)

## 🛠️ Instalación

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd mcp-student-server
```

### 2. Crear y activar entorno Conda

```bash
conda create -n mcp-student python=3.11
conda activate mcp-student
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno (opcional)

```bash
cp .env.example .env
# Editar .env según necesidades
```

## 🚀 Uso

### Modo STDIO (MCP Inspector)

Para ejecutar el servidor en modo STDIO y probarlo con el MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python src/main.py
```

Esto abrirá una interfaz web en tu navegador donde podrás:
- Ver los recursos disponibles
- Probar las herramientas MCP
- Inspeccionar las respuestas del servidor

### Modo Servidor Web (FastAPI)

Para ejecutar como servidor web:

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en:
- API: http://localhost:8000
- SSE Endpoint: http://localhost:8000/sse
- Messages Endpoint: http://localhost:8000/messages

### Modo CLI (Python directo)

```bash
python src/main.py
```

## 📁 Estructura del Proyecto

```
mcp-student-server/
├── src/
│   ├── main.py                  # Entry point principal
│   ├── config.py                # Configuración
│   ├── models/                  # Modelos de datos Pydantic
│   │   ├── course.py
│   │   └── student.py
│   ├── services/                # Lógica de negocio
│   │   ├── course_service.py
│   │   └── calendar_service.py
│   ├── mcp/                     # Componentes MCP
│   │   ├── server.py
│   │   ├── resources.py
│   │   └── tools.py
│   ├── routes/                  # Rutas FastAPI
│   │   └── mcp_routes.py
│   ├── utils/                   # Utilidades
│   │   └── date_utils.py
│   └── data/                    # Datos de ejemplo
│       └── example_data.json
├── api/                         # Entry point para Vercel
│   └── index.py
├── requirements.txt
├── .env.example
└── README.md
```

## 🔧 Herramientas MCP Disponibles

### get_filtered_courses

Recupera y filtra cursos para un estudiante específico.

**Parámetros:**
- `student_id` (requerido): ID del estudiante
- `course_code` (opcional): Código del curso para filtrar (ej: 'CSE270')
- `week` (opcional): Número de semana para filtrar (ej: '1', '2')

**Ejemplo de uso:**
```json
{
  "student_id": "12345",
  "course_code": "CSE270",
  "week": "2"
}
```

### build_ics_file

Genera un archivo ICS con las tareas de los cursos.

**Parámetros:**
- `student_id` (requerido): ID del estudiante
- `course_code` (opcional): Código del curso para filtrar
- `week` (opcional): Número de semana para filtrar

**Ejemplo de uso:**
```json
{
  "student_id": "12345",
  "course_code": "CSE270"
}
```

## 🌐 Recursos MCP

### students://{student_id}/courses

URI dinámica para acceder a los cursos de un estudiante específico.

**Ejemplo:**
- `students://12345/courses`
- `students://example/courses`

## 📦 Dependencias

- `fastapi`: Framework web
- `uvicorn`: Servidor ASGI
- `mcp`: Model Context Protocol SDK
- `icalendar`: Generación de archivos ICS
- `pytz`: Manejo de zonas horarias
- `sse-starlette`: Server-Sent Events
- `pydantic`: Validación de datos

## 🚢 Deployment

### Vercel

El proyecto está configurado para deployment en Vercel mediante `vercel.json`:

```bash
# Deploy a Vercel
vercel --prod
```

El archivo `vercel.json` configura el deployment para usar `src/main.py` directamente.

## 🧪 Testing (Próximamente)

```bash
pytest tests/
```

## 📝 Notas

- Se recomienda usar Conda para gestión del entorno
- Los datos de ejemplo están en `src/data/example_data.json`
- Para desarrollo, usa el modo `--reload` con uvicorn
- El servidor soporta tanto modo STDIO como HTTP/SSE

## 📄 Licencia

[Especificar licencia]

## 👥 Contribución

[Instrucciones de contribución]
