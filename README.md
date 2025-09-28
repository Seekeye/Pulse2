# Pulse Trading System 🚀

Un sistema de trading automatizado con análisis de señales en tiempo real para criptomonedas.

## 🎯 Características

- **Señales en Tiempo Real**: Análisis automático del mercado de criptomonedas
- **Dashboard Interactivo**: Interfaz web moderna con React
- **API RESTful**: Backend robusto con FastAPI
- **Base de Datos**: SQLite para almacenamiento local
- **Precios en Vivo**: Integración con Coinbase API
- **Sistema de Tracking**: Seguimiento de señales reforzadas y conflictivas

## 🛠️ Tecnologías

### Backend
- **Python 3.11+**
- **FastAPI** - Framework web moderno
- **SQLAlchemy** - ORM para base de datos
- **Uvicorn** - Servidor ASGI
- **aiohttp** - Cliente HTTP asíncrono

### Frontend
- **React 18**
- **Vite** - Build tool rápido
- **Tailwind CSS** - Framework de estilos
- **Heroicons** - Iconos

## 🚀 Instalación Local

### Backend
```bash
cd /home/seekeye/Pulse
pip install -r requirements.txt
python3 -m uvicorn api_endpoints:app --host 0.0.0.0 --port 8004
```

### Frontend
```bash
cd pulse-frontend
npm install
npm run dev
```

## 🌐 URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8004
- **API Docs**: http://localhost:8004/docs

## 📊 API Endpoints

- `GET /api/dashboard-data` - Datos del dashboard
- `GET /api/test-prices` - Precios de prueba
- `POST /api/reset-database` - Resetear base de datos
- `POST /api/generate-test-signals` - Generar señales de prueba

## 🔧 Variables de Entorno

No se requieren variables de entorno para funcionamiento local.

## 📝 Licencia

MIT License
