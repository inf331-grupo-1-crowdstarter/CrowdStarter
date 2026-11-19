_Inf331-Grupo 1_
# 🚀 CrowdStarter
Plataforma web de crowdfunding donde personas y organizaciones publican
proyectos y reciben financiamiento directamente de una comunidad.

> Idea → Comunidad → Validación → Financiamiento → Proyecto

## 🎯 Propósito
Reducir las barreras para financiar nuevas ideas, con transparencia
y confianza entre creadores y aportantes.

## 🔗 Enlaces
- 📦 [Repositorio principal](https://github.com/inf331-grupo-1-crowdstarter/CrowdStarter)
- 📚 [Wiki del proyecto](https://github.com/inf331-grupo-1-crowdstarter/CrowdStarter/wiki)
- 🎥 Video Entrega 1: https://youtu.be/dKeZFzO4w8g
- 🎥 Video Entrega 2: https://www.youtube.com/watch?v=hXCo6FFA-T8

## 👥 Equipo
| Integrante | Rol |
|---|---|
| Aylin Rojas | Líder / Kanban master |
| Sebastián Castillo | Dev backend |
| Vicente Illane | Dev frontend + QA |

## 🛠️ Tecnologías
Python (Django) · Bootstrap · SQLite/PostgreSQL · PyTest · GitHub Actions · Playwright

## 🛠️ Ejecución local

### Requisitos

- Python 3.13 o superior
- Git

### 1. Clonar el repositorio

```bash
git clone https://github.com/inf331-grupo-1-crowdstarter/CrowdStarter.git
cd CrowdStarter
```

### 2. Crear y activar el entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
python -m pip install -r requirements.txt
```

### 4. Aplicar las migraciones

```bash
python manage.py migrate
```

### 5. Ejecutar la aplicación

```bash
python manage.py runserver
```

La aplicación estará disponible en:

`http://127.0.0.1:8000/`

## 🧪 Pruebas automatizadas

Con el entorno virtual activado, instala el navegador para las pruebas E2E:

```bash
python -m playwright install chromium
```

Para ejecutar toda la suite de pruebas:

```bash
pytest -v
```

Para verificar la configuración del proyecto Django:

```bash
python manage.py check
```

### Pruebas E2E y BASE_URL

```bash
python -m pytest e2e -v
```

Para elegir su dirección en Linux o Jenkins:

```bash
BASE_URL=http://127.0.0.1:8016 python -m pytest e2e -v
```


`BASE_URL` configura el servidor temporal, no una aplicación ya desplegada.
Admite HTTP, `localhost` o `127.0.0.1`, y un puerto explícito libre entre 1 y 65535. Si el puerto está ocupado, la ejecución falla.
