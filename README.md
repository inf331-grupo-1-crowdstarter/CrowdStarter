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
- 🎥 Video Entrega 1: _(pendiente)_

## 👥 Equipo
| Integrante | Rol |
|---|---|
| Aylin Rojas | Líder / Kanban master |
| Nombre 2 | Dev backend |
| Nombre 3 | Dev frontend + QA |

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

### 5. Crear categorías iniciales

```bash
python manage.py shell -c "from campaigns.models import Category; [Category.objects.get_or_create(name=n) for n in ['Tecnología', 'Arte', 'Comunidad']]"
```

### 6. Ejecutar la aplicación

```bash
python manage.py runserver
```

La aplicación estará disponible en:

`http://127.0.0.1:8000/`

## 🧪 Pruebas automatizadas

Para ejecutar toda la suite de pruebas:

```bash
pytest -v
```

Para verificar la configuración del proyecto Django:

```bash
python manage.py check
```