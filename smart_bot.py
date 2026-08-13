import os
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
    return "Bot Director Pro Sniper - Activo y Despierto 24/7 🚀"

def enviar_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(f"Error Telegram: {e}")

def get_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        res = requests.get(url, timeout=5)
        return float(res.json()["price"])
    except:
        return 0.0

# Esta es la ruta que el despertador externo va a visitar
@app.route("/despertar")
def despertar_bot():
    try:
        local_tz = timezone(timedelta(hours=-3))
        hora = datetime.now(local_tz).strftime("%H:%M hs")
        fecha = datetime.now(local_tz).strftime("%d/%m/%Y")
        
        for sym in TRACKED_SYMBOLS:
            nombre = sym.replace("USDT", "")
            precio = get_price(sym)
            
            if precio > 0:
                mensaje = (
                    f"📰 *{nombre} AHORA — {fecha} · {hora}*\n\n"
                    f"🔍 *Lo que está pasando ahora*\n"
                    f"El precio está en ~${precio:,.2f}, monitoreando reacción en zonas clave.\n\n"
                    f"🛡️ *Niveles a vigilar*\n"
                    f"🔵 Resistencias: ~${precio * 1.01:,.0f} · ~${precio * 1.02:,.0f}\n"
                    f"🔵 Soportes: ~${precio * 0.99:,.0f} · ~${precio * 0.98:,.0f}\n\n"
                    f"🎯 *Análisis Sniper:* Reporte automático de sesión."
                )
                enviar_telegram(mensaje)
                requests.get("https://httpbin.org/delay/2") # Pequeña pausa de cortesía
                
        return "¡Reporte enviado con éxito por el despertador! 🚀"
    except Exception as e:
        return f"Error en el reporte: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
