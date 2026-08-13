import os
import threading
import time
import random
from datetime import datetime, timezone, timedelta
import requests
from flask import Flask

app = Flask(__name__)

# --- CONFIGURACIÓN ---
TELEGRAM_TOKEN = "8944132671:AAEZR2CcxNM1-Qj-Hh5ApEWmdkR0eB_afrs"
CHAT_ID = "8982812050"

TRACKED_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BANANAUSDT", "HYPEUSDT", "TAOUSDT"]
last_prices = {symbol: 0.0 for symbol in TRACKED_SYMBOLS}
THRESHOLD = 0.008 

SECRET_VIBES = [
    "🧠 Mentalidad: El dinero se hace en la paciencia, no en la pantalla.",
    "🎯 Regla de oro: Respeta tu plan, el mercado no tiene sentimientos.",
    "⚡ Psicología: Las grandes ganancias van para el que sabe esperar el retroceso.",
    "🛡️ Gestión: Un buen trader sobrevive para operar el día de mañana.",
    "🔥 Filosofía: Caza los imbalances como un francotirador."
]

@app.route("/")
def home():
    return "Bot Director Pro Smart Money Activo 24/7 🚀"

def get_market_data(symbol):
    """Obtiene el precio actual y calcula OB / FVG de las últimas velas de 15m"""
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=10"
        res = requests.get(url, timeout=5)
        data = res.json()
        
        if not data or len(data) < 5:
            return None, "N/A", "N/A", 0.0

        current_price = float(data[-1][4])
        
        prev_candle = data[-2]
        p_open = float(prev_candle[1])
        p_high = float(prev_candle[2])
        p_low = float(prev_candle[3])
        p_close = float(prev_candle[4])

        if p_close > p_open:
            ob_zone = f"🟢 OB Alcista: ${p_low:,.2f} - ${p_open:,.2f}"
        else:
            ob_zone = f"🔴 OB Bajista: ${p_open:,.2f} - ${p_high:,.2f}"

        c_prev = data[-3]
        cp_high = float(c_prev[2])
        cp_low = float(c_prev[3])
        
        fvg_zone = "⚡ FVG: Sin desequilibrio activo"
        if p_low > cp_high:
            fvg_zone = f"⚡ FVG Alcista: ${cp_high:,.2f} - ${p_low:,.2f}"
        elif p_high < cp_low:
            fvg_zone = f"⚡ FVG Bajista: ${p_high:,.2f} - ${cp_low:,.2f}"

        return current_price, ob_zone, fvg_zone, current_price
    except Exception:
        return None, "Error OB", "Error FVG", 0.0

def generar_reporte_smc(razon):
    try:
        # Hora local de Paraguay (UTC-4)
        local_tz = timezone(timedelta(hours=-4))
        ahora = datetime.now(local_tz).strftime("%d/%m/%Y - %H:%M (Py)")
        vibe_secreto = random.choice(SECRET_VIBES)
        
        reporte_detallado = ""
        current_prices_dict = {}

        for sym in TRACKED_SYMBOLS:
            nombre = sym.replace("USDT", "")
            precio, ob, fvg, val = get_market_data(sym)
            if precio:
                current_prices_dict[sym] = val
                reporte_detallado += f"📊 **{nombre}** (15m):\n  • Precio: ${precio:,.2f}\n  • {ob}\n  • {fvg}\n\n"
            time.sleep(0.2)

        # Si por alguna razón el reporte detallado fallara en llenarse, evitamos mensaje vacío
        if not reporte_detallado:
            reporte_detallado = "⚠️ Sincronizando datos de mercado de Binance...\n\n"

        mensaje = (
            f"🎯 **¡Reporte de Francotirador, Rodrigo Sniper!**\n"
            f"🚨 **ESTADO SMC — {razon}**\n\n"
            f"⏰ *Hora:* {ahora}\n\n"
            f"{reporte_detallado}"
            f"💡 *Gestión:* {vibe_secreto}\n\n"
            f"🤖 *¡Ajusta tus rectángulos en TradingView!*"
        )
        
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
            json={"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}, 
            timeout=10
        )
        return current_prices_dict
    except Exception as e:
        print(f"Error generando reporte: {e}")
        return {}

def bot_loop():
    time.sleep(5)
    print("🤖 Lanzando escaneo inicial de Smart Money para Rodrigo Sniper...")
    global last_prices
    initial_prices = generar_reporte_smc("ESCANEO INICIAL DE MERCADO")
    if initial_prices:
        last_prices.update(initial_prices)

    while True:
        try:
            time.sleep(60)
            now = datetime.now(timezone(timedelta(hours=-4)))
            # Alerta de Apertura o momentos clave
            if now.hour in [0, 8, 13] and now.minute < 5:
                generar_reporte_smc("REPORTE DE SESIÓN")
                time.sleep(600)
        except Exception:
            time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=bot_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
