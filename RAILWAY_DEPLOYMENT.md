# 🚀 Guía de Deployment en Railway

## 📁 Archivos Necesarios

### ✅ Archivos que YA tienes:
- `requirements.txt` - Dependencias de Python
- `Procfile` - Comando de inicio
- `railway.json` - Configuración de Railway
- `runtime.txt` - Versión de Python
- `api_endpoints.py` - API principal
- `data/` - Módulos de base de datos
- `signals/` - Módulos de señales
- `models/` - Modelos de datos

### 📝 Archivos que creamos:
- `.gitignore` - Archivos a ignorar
- `README.md` - Documentación del proyecto

## 🔧 Pasos para Subir a Railway

### 1. **Crear Repositorio en GitHub**
```bash
# Inicializar git (si no está inicializado)
git init

# Agregar todos los archivos
git add .

# Hacer commit inicial
git commit -m "Initial commit: Pulse Trading System"

# Crear repositorio en GitHub (desde la web)
# Luego conectar:
git remote add origin https://github.com/TU_USUARIO/pulse-trading.git
git branch -M main
git push -u origin main
```

### 2. **Configurar Railway**
1. Ve a https://railway.app
2. Crea cuenta o inicia sesión
3. Click en "New Project"
4. Selecciona "Deploy from GitHub repo"
5. Conecta tu cuenta de GitHub
6. Selecciona el repositorio `pulse-trading`

### 3. **Configuración Automática**
Railway detectará automáticamente:
- ✅ Python (por `requirements.txt`)
- ✅ Puerto (por `Procfile`)
- ✅ Comando de inicio (por `railway.json`)

### 4. **Variables de Entorno (Opcional)**
En Railway Dashboard → Variables:
```
PORT=8000  # Railway lo asigna automáticamente
```

### 5. **Deploy**
- Railway construirá automáticamente tu proyecto
- Tomará 2-3 minutos
- Te dará una URL como: `https://pulse-trading-production.up.railway.app`

## 🌐 URLs de tu Aplicación

### Backend (Railway):
- **API**: `https://tu-proyecto.railway.app`
- **Docs**: `https://tu-proyecto.railway.app/docs`
- **Health Check**: `https://tu-proyecto.railway.app/api/test-prices`

### Frontend (Vercel/Netlify):
- **App**: `https://tu-frontend.vercel.app`

## 🔄 Actualizar Código

```bash
# Hacer cambios en tu código
git add .
git commit -m "Update: descripción del cambio"
git push origin main

# Railway se actualiza automáticamente
```

## 📊 Monitoreo

### Railway Dashboard:
- **Logs**: Ve logs en tiempo real
- **Métricas**: CPU, memoria, tráfico
- **Variables**: Gestiona variables de entorno
- **Dominio**: Configura dominio personalizado

### Health Check:
```bash
curl https://tu-proyecto.railway.app/api/test-prices
```

## 🚨 Solución de Problemas

### Error: "Module not found"
- Verifica que `requirements.txt` tenga todas las dependencias
- Revisa los imports en `api_endpoints.py`

### Error: "Port already in use"
- Railway asigna el puerto automáticamente
- Usa `$PORT` en lugar de puerto fijo

### Error: "Database connection failed"
- Railway no tiene SQLite persistente
- Considera usar PostgreSQL de Railway

## 💰 Costos

### Railway:
- **Hobby Plan**: $5/mes (1GB RAM, 1GB storage)
- **Pro Plan**: $20/mes (8GB RAM, 100GB storage)

### Alternativas Gratuitas:
- **Render**: 750 horas/mes gratis
- **Fly.io**: 3 apps gratis
- **Heroku**: $7/mes (mínimo)

## 🎯 Próximos Pasos

1. **Subir a GitHub** ✅
2. **Deploy en Railway** ✅
3. **Deploy Frontend en Vercel**
4. **Configurar dominio personalizado**
5. **Configurar base de datos PostgreSQL**
6. **Configurar CI/CD**

## 📞 Soporte

- **Railway Docs**: https://docs.railway.app
- **Discord**: Railway Community
- **GitHub Issues**: Para bugs del proyecto
