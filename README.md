# 🚀 Pulse - Intelligent Trading Analysis System

Un sistema completo de análisis técnico inteligente para criptomonedas con interfaz web moderna.

## ✨ Características

- 📊 **Análisis técnico en tiempo real** de criptomonedas
- 🎯 **Generación de señales de trading** con IA
- 📱 **Notificaciones por Telegram**
- 🌐 **API REST** completa
- 💻 **Dashboard web** moderno con React
- 🔄 **Múltiples fuentes de datos** (Coinbase, CoinGecko, Binance, etc.)

## 🏗️ Arquitectura

### Backend (Python)
- **FastAPI** - API REST moderna y rápida
- **SQLAlchemy** - ORM para base de datos
- **SQLite** - Base de datos local
- **aiohttp** - Cliente HTTP asíncrono
- **Múltiples collectors** - Coinbase, CoinGecko, Binance, CoinCap, CryptoCompare

### Frontend (React)
- **React 18** - Biblioteca de UI moderna
- **Vite** - Build tool rápido
- **Tailwind CSS** - Framework de estilos
- **Recharts** - Gráficos y visualizaciones
- **Framer Motion** - Animaciones

## 🚀 Despliegue

### Backend (Render)
- **URL:** https://pulse-xxfq.onrender.com
- **Estado:** ✅ Funcionando 24/7

### Frontend (Netlify/Vercel)
- **Configuración:** Lista para desplegar
- **Build command:** `npm run build`
- **Publish directory:** `dist`

## 📡 API Endpoints

- `GET /api/health` - Health check
- `GET /api/dashboard-data` - Datos del dashboard
- `GET /api/test-prices` - Precios en tiempo real
- `GET /api/signals` - Señales de trading
- `POST /api/generate-test-signals` - Generar señales de prueba

## 🛠️ Desarrollo Local

### Backend
```bash
pip install -r requirements.txt
python3 -m uvicorn api_endpoints:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
npm install
npm run dev
```

## 📊 Monitoreo

- **Símbolos:** BTC-USD, ETH-USD, ADA-USD, MATIC-USD, SOL-USD, LINK-USD
- **Intervalo de análisis:** 5 minutos
- **Indicadores técnicos:** RSI, MACD, Bollinger Bands, SMA, EMA
- **Notificaciones:** Telegram automáticas

## 🔧 Configuración

### Variables de entorno
```env
VITE_API_URL=https://pulse-xxfq.onrender.com
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

## 📈 Características Técnicas

- **Análisis multi-timeframe**
- **Gestión de riesgo automática**
- **Tracking de señales en tiempo real**
- **Contexto de mercado inteligente**
- **Sistema de fallback entre fuentes de datos**

---

**Desarrollado con ❤️ para el análisis inteligente de mercados cripto**