# Sistema de Turismo V2 - Dirección de Turismo Esperanza

## 📋 Descripción
Sistema web para gestionar solicitudes de visitas turísticas, reemplazando el proceso manual con Google Sheets.

## 🔄 Flujo del Sistema
1. **Instituciones** → Formulario web público → Solicitud PENDIENTE
2. **Dirección Turismo** → Panel admin → Confirma visitas 
3. **Prestadores** → Panel personal → Ven sus visitas confirmadas

## 🛠️ Tecnologías
- **Backend:** Flask + SQLAlchemy + Flask-Login
- **Frontend:** Bootstrap 5 + JavaScript vanilla
- **Base de Datos:** SQLite (desarrollo) / PostgreSQL (producción)

## 🚀 Instalación

### Requisitos
- Python 3.8+
- pip

### Pasos
```bash
# 1. Clonar repositorio
git clone <url-repo>
cd SISTEMA_TURISMO_V2

# 2. Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar base de datos (próximo commit)
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 5. Ejecutar aplicación
python run.py
```

## 🌐 URLs del Sistema
- `/` - Formulario instituciones (público)
- `/admin/*` - Panel Dirección Turismo  
- `/prestador/*` - Panel prestadores

## 📊 Estado del Proyecto
🚧 **EN DESARROLLO**

### Commits Completados
- ✅ **Commit 1:** Estructura base y configuración Flask

### Próximos Commits
- 🔄 **Commit 2:** Modelos de base de datos
- ⏳ **Commit 3:** Sistema de autenticación
- ⏳ **Commit 4:** Formulario instituciones

## 👥 Contribuir
Proyecto de tesis - desarrollo individual

## 📄 Licencia
Uso académico - Dirección de Turismo Esperanza