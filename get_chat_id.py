"""
Script para obtener Chat ID de Telegram
Uso: python3 get_chat_id.py TU_BOT_TOKEN
"""

import sys
import requests
import json
from datetime import datetime

def get_chat_id(bot_token):
    """Obtener Chat ID desde Telegram"""
    try:
        print("🔍 Obteniendo actualizaciones de Telegram...")
        
        # URL de la API de Telegram
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        
        # Hacer petición
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Error HTTP {response.status_code}")
            if response.status_code == 401:
                print("❌ Token inválido. Verifica tu bot token.")
            return None
        
        data = response.json()
        
        if not data.get('ok'):
            print(f"❌ Error de API: {data.get('description', 'Unknown')}")
            return None
        
        updates = data.get('result', [])
        
        if not updates:
            print("⚠️  No hay mensajes. Envía un mensaje a tu bot primero.")
            print("📱 Pasos:")
            print("   1. Busca tu bot en Telegram")
            print("   2. Envía: /start")
            print("   3. Ejecuta este script de nuevo")
            return None
        
        # Obtener Chat IDs únicos
        chat_ids = set()
        for update in updates:
            if 'message' in update:
                chat_id = update['message']['chat']['id']
                chat_ids.add(chat_id)
        
        if chat_ids:
            print("✅ Chat IDs encontrados:")
            for chat_id in chat_ids:
                print(f"   📱 Chat ID: {chat_id}")
            
            # Retornar el primer Chat ID
            return list(chat_ids)[0]
        else:
            print("❌ No se encontraron Chat IDs")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None

def test_bot_connection(bot_token):
    """Probar conexión con el bot"""
    try:
        print("🔧 Probando conexión con el bot...")
        
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                bot_name = bot_info.get('username', 'Unknown')
                print(f"✅ Bot conectado: @{bot_name}")
                return True
        
        print(f"❌ Error de conexión: HTTP {response.status_code}")
        return False
        
    except Exception as e:
        print(f"❌ Error probando bot: {e}")
        return False

def update_config_file(chat_id, bot_token):
    """Actualizar config/settings.py con los nuevos valores"""
    try:
        print("📝 Actualizando config/settings.py...")
        
        # Leer archivo actual
        with open('config/settings.py', 'r') as f:
            content = f.read()
        
        # Reemplazar valores
        content = content.replace(
            'TELEGRAM_BOT_TOKEN: str = "6123456789:AAEhBOweik6ad2r_3lJ7Z8z2qMsQ1nwTokyo"',
            f'TELEGRAM_BOT_TOKEN: str = "{bot_token}"'
        )
        content = content.replace(
            'TELEGRAM_CHAT_ID: str = "1001234567890"',
            f'TELEGRAM_CHAT_ID: str = "{chat_id}"'
        )
        content = content.replace(
            'TELEGRAM_ENABLED: bool = False',
            'TELEGRAM_ENABLED: bool = True'
        )
        
        # Escribir archivo actualizado
        with open('config/settings.py', 'w') as f:
            f.write(content)
        
        print("✅ config/settings.py actualizado correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando config: {e}")
        return False

def main():
    print("🚀 ChainPulse - Telegram Chat ID Extractor")
    print("=" * 50)
    
    if len(sys.argv) != 2:
        print("❌ Uso: python3 get_chat_id.py TU_BOT_TOKEN")
        print("\n📱 Para obtener tu bot token:")
        print("   1. Busca @BotFather en Telegram")
        print("   2. Envía: /newbot")
        print("   3. Sigue las instrucciones")
        print("   4. Copia el token que te da")
        sys.exit(1)
    
    bot_token = sys.argv[1]
    
    # Validar formato del token
    if ':' not in bot_token or len(bot_token) < 20:
        print("❌ Token inválido. Debe tener formato: 123456789:ABCdef...")
        sys.exit(1)
    
    # Probar conexión
    if not test_bot_connection(bot_token):
        sys.exit(1)
    
    # Obtener Chat ID
    chat_id = get_chat_id(bot_token)
    
    if chat_id:
        print(f"\n🎉 ¡Éxito!")
        print(f"   🤖 Bot Token: {bot_token}")
        print(f"   💬 Chat ID: {chat_id}")
        
        # Preguntar si actualizar config
        response = input("\n❓ ¿Actualizar config/settings.py automáticamente? (y/n): ")
        if response.lower() in ['y', 'yes', 's', 'si']:
            if update_config_file(chat_id, bot_token):
                print("\n🚀 ¡Listo! Ahora puedes ejecutar:")
                print("   python3 main.py")
            else:
                print("\n📝 Actualiza manualmente config/settings.py:")
                print(f'   TELEGRAM_BOT_TOKEN: str = "{bot_token}"')
                print(f'   TELEGRAM_CHAT_ID: str = "{chat_id}"')
        else:
            print("\n📝 Actualiza manualmente config/settings.py:")
            print(f'   TELEGRAM_BOT_TOKEN: str = "{bot_token}"')
            print(f'   TELEGRAM_CHAT_ID: str = "{chat_id}"')
    else:
        print("\n❌ No se pudo obtener el Chat ID")
        print("📱 Asegúrate de enviar un mensaje a tu bot primero")

if __name__ == "__main__":
    main()