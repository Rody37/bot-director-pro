import os
import threading
import time
from datetime import datetime, timezone, timedelta
import requests
from flask import Flask

app = Flask(__name__)

# --- CONFIGURACIÓN ---
TELEGRAM_TOKEN = "8944132671:AAEZR2CcxNM1-Qj-Hh5ApEWmdkR0eB_afrs"
CHAT_ID = "8982812050"
TRACKED_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

@app.route("/")
def home():
    return "Bot Director Pro Activo 🚀"

def enviar_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}, timeout=10)
    except:
        pass

def get_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        res = requests.get(url, timeout=5)
        return float(res.json()["price"])
    except:
        return 0.0

def bot_loop():
    time.sleep(10)
    enviar_telegram("🤖 *Bot Director Pro: Sistema Sniper Iniciado*")
    
    while True:
        try:
            local_tz = timezone(timedelta(hours=-3))
            hora = datetime.now(local_tz).strftime("%H:%M hs")
            
            for sym in TRACKED_SYMBOLS:
                nombre = sym.replace("USDT", "")
                precio = get_price(sym)
                
                if precio > 0:
                    # Estructura calcada a tu foto
                    mensaje = (
                        f"📰 *{nombre} AHORA — {datetime.now(local_tz).strftime('%d/%m/%Y')} · {hora}*\n\n"
                        f"🔍 *Lo que está pasando ahora*\n"
                        f"El precio está en ~${precio:,.2f}, monitoreando reacción en zonas clave.\n\n"
                        f"🛡️ *Niveles a vigilar*\n"
                        f"🔵 Resistencias: ~${precio * 1.01:,.0f} · ~${precio * 1.02:,.0f}\n"
                        f"🔵 Soportes: ~${precio * 0.99:,.0f} · ~${precio * 0.98:,.0f}\n\n"
                        f"🎯 *Análisis Sniper:* Esperando confirmación institucional."
                    )
                    enviar_telegram(mensaje)
                time.sleep(5)
            
            time.sleep(3600) # Reporte cada hora
        except Exception as e:
            time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=bot_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
