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

# Radar de Élite: Majors + Activos de alta liquidez + Proyectos de alto potencial
TRACKED_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", 
    "XRPUSDT", "ADAUSDT", "LINKUSDT", 
    "TAOUSDT", "HYPEUSDT", "BANANAUSDT"
]
last_prices = {symbol: 0.0 for symbol in TRACKED_SYMBOLS}

# Umbral de movimiento fuerte (0.8% para el Radar de Élite)
THRESHOLD = 0.008 

@app.route("/")
def home():
    return "Bot Director Pro Activo 24/7 (Radar Élite + TAO/HYPE/BANANA) 🚀"

def get_market_prices():
    try:
        # Consultamos la API de Binance
        data = requests.get("https://api.binance.com/api/v3/ticker/price", timeout=5).json()
        prices = {}
        for item in data:
            if item["symbol"] in TRACKED_SYMBOLS:
                prices[item["symbol"]] = float(item["price"])
        return prices
    except:
        return {}

def check_session_alert():
    target_hours = [0, 8, 13]
    now = datetime.now(timezone.utc)
    future = now + timedelta(minutes=20)
    
    if future.hour in target_hours and future.minute < 5:
        return True, "PRE-APERTURA"
    return False, ""

def generar_reporte(razon, prices_dict):
    ahora = datetime.now(timezone.utc).strftime("%H:%M UTC")
    
    precios_txt = ""
    for sym in TRACKED_SYMBOLS:
        val = prices_dict.get(sym, 0)
        # Solo mostramos si tenemos precio (por si algún ticker no está en Binance)
        if val > 0:
            nombre = sym.replace("USDT", "")
            precios_txt += f"• {nombre}: ${val:,.2f}\n"

    mensaje = (
        f"🚨 **ALERTA DEL DIRECTOR — {razon}**\n\n"
        f"⏰ *Hora:* {ahora}\n\n"
        f"📈 **Radar de Élite:**\n{precios_txt}\n"
        f"🤖 *¡Atentos a la acción del precio!*"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"})

def bot_loop():
    print("🤖 Hilo del Bot Centinela 'Élite' Activo...")
    
    # Inicializar precios
    initial_prices = get_market_prices()
    for sym in TRACKED_SYMBOLS:
        if sym in initial_prices:
            last_prices[sym] = initial_prices[sym]

    while True:
        try:
            current_prices = get_market_prices()
            if not current_prices:
                time.sleep(60)
                continue

            alerta_disparada = False
            razon_alerta = ""
            
            # Vigilar saltos de precio
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

            # Vigilar aperturas
            is_opening, razon = check_session_alert()
            if is_opening:
                generar_reporte(f"APERTURA DE MERCADO EN 20 MIN", current_prices)
                time.sleep(3600) # Descansar tras el aviso

            time.sleep(60)
        except Exception as e:
            print(f"Error en bucle: {e}")
            time.sleep(60)

if __name__ == "__main__":
    t = threading.Thread(target=bot_loop)
    t.daemon = True
    t.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
