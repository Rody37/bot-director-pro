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

# Lista simplificada
TRACKED_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BANANAUSDT"]

@app.route("/")
def home():
    return "Bot Director Pro Activo 24/7 🚀"

def get_market_data(symbol):
    try:
        # Petición a Binance
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=5"
        res = requests.get(url, timeout=10)
        data = res.json()
        
        current_price = float(data[-1][4])
        
        # OB y FVG simplificados
        p_open, p_high, p_low, p_close = float(data[-2][1]), float(data[-2][2]), float(data[-2][3]), float(data[-2][4])
        ob = f"🟢 OB: ${p_low:,.2f}" if p_close > p_open else f"🔴 OB: ${p_high:,.2f}"
        
        cp_high, cp_low = float(data[-3][2]), float(data[-3][3])
        fvg = "⚡ FVG: Activo" if (p_low > cp_high or p_high < cp_low) else "⚡ FVG: Neutral"
        
        return current_price, ob, fvg
    except Exception:
        return 0.0, "OB: Error", "FVG: Error"

def enviar_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}, timeout=15)
    except Exception as e:
        print(f"Error enviando Telegram: {e}")

def bot_loop():
    time.sleep(10) # Espera inicial
    
    while True:
        try:
            local_tz = timezone(timedelta(hours=-3))
            ahora = datetime.now(local_tz).strftime("%d/%m/%Y - %H:%M (Py)")
            
            reporte = f"🎯 *Reporte Francotirador: Rodrigo Sniper*\n⏰ {ahora}\n\n"
            
            for sym in TRACKED_SYMBOLS:
                nombre = sym.replace("USDT", "")
                precio, ob, fvg = get_market_data(sym)
                reporte += f"📊 {nombre}: ${precio:,.2f}\n  {ob} | {fvg}\n\n"
                time.sleep(0.5) 
            
            reporte += "🛡️ *Gestión:* Caza los imbalances como un francotirador."
            
            enviar_telegram(reporte)
            
            # Repetir cada 1 hora
            time.sleep(3600) 
        except Exception as e:
            print(f"Error en bucle: {e}")
            time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=bot_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
