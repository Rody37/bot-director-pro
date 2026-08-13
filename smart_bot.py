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

def get_smc_data(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=5"
        res = requests.get(url, timeout=10)
        data = res.json()
        p_open, p_high, p_low, p_close = float(data[-2][1]), float(data[-2][2]), float(data[-2][3]), float(data[-2][4])
        ob = f"🟢 OB Alcista: ${p_low:,.0f}" if p_close > p_open else f"🔴 OB Bajista: ${p_high:,.0f}"
        cp_high, cp_low = float(data[-3][2]), float(data[-3][3])
        fvg = "⚡ FVG: Activo" if (p_low > cp_high or p_high < cp_low) else "⚡ FVG: Sin imbalance"
        return float(data[-1][4]), ob, fvg
    except:
        return 0.0, "OB: No disponible", "FVG: No disponible"

def bot_loop():
    # DISPARO INICIAL
    enviar_telegram("🤖 *Bot Director Pro: Sistema Sniper Iniciado y Blindado*")
    time.sleep(5)
    
    while True:
        try:
            local_tz = timezone(timedelta(hours=-3))
            hora_actual = datetime.now(local_tz).strftime("%H:%M hs")
            
            for sym in TRACKED_SYMBOLS:
                nombre = sym.replace("USDT", "")
                precio, ob, fvg = get_smc_data(sym)
                
                if precio > 0:
                    mensaje = (
                        f"📰 *{nombre} AHORA — {hora_actual}*\n\n"
                        f"🔍 *Lo que está pasando ahora*\n"
                        f"Precio actual: ${precio:,.2f}\n"
                        f"{ob}\n"
                        f"{fvg}\n\n"
                        f"🛡️ *Niveles a vigilar*\n"
                        f"🔵 Resistencias: ${precio * 1.015:,.0f} · ${precio * 1.025:,.0f}\n"
                        f"🔵 Soportes: ${precio * 0.985:,.0f} · ${precio * 0.975:,.0f}\n\n"
                        f"🎯 *Análisis Sniper: Esperando confirmación institucional.*"
                    )
                    enviar_telegram(mensaje)
                time.sleep(5) 
            
            time.sleep(3600)
        except Exception as e:
            print(f"Error en bucle: {e}")
            time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=bot_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
