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

TRACKED_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", 
    "XRPUSDT", "ADAUSDT", "LINKUSDT", 
    "TAOUSDT", "HYPEUSDT", "BANANAUSDT"
]
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
    return "Bot Director Pro Activo 24/7 🚀"

@app.route("/test")
def test_alert():
    try:
        prices = get_market_prices()
        generar_reporte("TEST MANUAL DE CONECTIVIDAD", prices)
        return "¡Mensaje de test enviado con éxito a Telegram! 🚀"
    except Exception as e:
        return f"Error al enviar test: {e}"

def get_market_prices():
    try:
        res = requests.get("https://api.binance.com/api/v3/ticker/price", timeout=5)
        data = res.json()
        prices = {}
        for item in data:
            if item["symbol"] in TRACKED_SYMBOLS:
                prices[item["symbol"]] = float(item["price"])
        return prices
    except Exception as e:
        print(f"Error obteniendo precios: {e}")
        return {}

def check_session_alert():
    try:
        target_hours = [0, 8, 13]
        now = datetime.now(timezone.utc)
        future = now + timedelta(minutes=20)
        if future.hour in target_hours and future.minute < 5:
            return True, "PRE-APERTURA"
    except Exception:
        pass
    return False, ""

def generar_reporte(razon, prices_dict):
    try:
        ahora = datetime.now(timezone.utc).strftime("%H:%M UTC")
        vibe_secreto = random.choice(SECRET_VIBES)
        
        precios_txt = ""
        for sym in TRACKED_SYMBOLS:
            val = prices_dict.get(sym, 0)
            if val > 0:
                nombre = sym.replace("USDT", "")
                precios_txt += f"• {nombre}: ${val:,.2f}\n"

        mensaje = (
            f"🚨 **ALERTA DEL DIRECTOR — {razon}**\n\n"
            f"⏰ *Hora:* {ahora}\n\n"
            f"📈 **Radar de Élite:**\n{precios_txt}\n"
            f"{vibe_secreto}\n\n"
            f"🤖 *¡Atentos a la acción del precio!*"
        )

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}, timeout=5)
    except Exception as e:
        print(f"Error enviando reporte a Telegram: {e}")

def bot_loop():
    print("🤖 Hilo del Bot Centinela 'Élite' Activo...")
    try:
        initial_prices = get_market_prices()
        for sym in TRACKED_SYMBOLS:
            if sym in initial_prices:
                last_prices[sym] = initial_prices[sym]

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        mensaje_inicio = "🤖 **¡Bot Director Pro Activo!** Sistema blindado y operando con reloj real. 🚀"
        requests.post(url, json={"chat_id": CHAT_ID, "text": mensaje_inicio, "parse_mode": "Markdown"}, timeout=5)
        print("Mensaje de inicio enviado a Telegram.")
    except Exception as e:
        print(f"Error en inicio del hilo: {e}")

    ultimo_reporte = time.time()
    INTERVALO_REPORTE = 300 

    while True:
        try:
            current_prices = get_market_prices()
            if not current_prices:
                time.sleep(30)
                continue

            alerta_disparada = False
            razon_alerta = ""
            
            for sym, price in current_prices.items():
                old_price = last_prices.get(sym, price)
                if old_price > 0:
                    diff = abs((price - old_price) / old_price)
                    if diff > THRESHOLD:
                        alerta_disparada = True
                        nombre_moneda = sym.replace("USDT", "")
                        razon_alerta = f"¡MOVIMIENTO FUERTE EN {nombre_moneda}!"
                        break

            if alerta_disparada:
                generar_reporte(razon_alerta, current_prices)
                for sym in TRACKED_SYMBOLS:
                    if sym in current_prices:
                        last_prices[sym] = current_prices[sym]
                ultimo_reporte = time.time()

            is_opening, razon = check_session_alert()
            if is_opening:
                generar_reporte(f"APERTURA DE MERCADO EN 20 MIN", current_prices)
                ultimo_reporte = time.time()

            if time.time() - ultimo_reporte >= INTERVALO_REPORTE:
                generar_reporte("REPORTE PERIÓDICO DE RUTINA (CADA 1 HORA)", current_prices)
                ultimo_reporte = time.time()

            time.sleep(30)
        except Exception as e:
            print(f"Error en bucle del bot: {e}")
            time.sleep(30)

if __name__ == "__main__":
    try:
        t = threading.Thread(target=bot_loop)
        t.daemon = True
        t.start()

        port = int(os.environ.get("PORT", 10000))
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        print(f"Error fatal al arrancar la app web: {e}")
