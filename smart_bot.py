import os
import threading
import time
from datetime import datetime, timezone
import requests
from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
  return "Bot Director Pro Activo 24/7 🚀"


TELEGRAM_TOKEN = os.environ.get("8944132671:AAEZR2CcxNM1-Qj-Hh5ApEWmdkR0eB_afrs")
CHAT_ID = os.environ.get("8982812050")


def get_market_session():
  utc_hour = datetime.now(timezone.utc).hour
  if 0 <= utc_hour < 8:
    return "ASIA", "Mercado en rango, propenso a trampas."
  elif 8 <= utc_hour < 13:
    return "LONDRES", "Volumen real. La tendencia de Asia suele ser barrida."
  elif 13 <= utc_hour < 17:
    return "NUEVA YORK", "Fuego puro. Los institucionales definen la tendencia."
  else:
    return "CIERRE", "Baja liquidez. Observación y espera."


def get_imbalance(symbol):
  url = (
      f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=5"
  )
  try:
    data = requests.get(url, timeout=5).json()
    c1_high = float(data[-3][2])
    c3_low = float(data[-1][3])
    if c1_high < c3_low:
      return f"Bullish: ${c1_high:,.0f} - ${c3_low:,.0f}"
    if float(data[-3][3]) > float(data[-1][2]):
      return f"Bearish: ${data[-3][3]:,.0f} - ${data[-1][2]:,.0f}"
    return "Sin imbalances evidentes."
  except:
    return "Calculando..."


def generar_reporte_director():
  if not TELEGRAM_TOKEN or not CHAT_ID:
    print("Faltan las credenciales de Telegram.")
    return

  ahora = datetime.now().strftime("%d/%m/%Y · %H:%M hs")
  sesion, insight = get_market_session()

  try:
    data = requests.get(
        "https://api.binance.com/api/v3/ticker/price", timeout=5
    ).json()
    btc_price = float(
        next(item for item in data if item["symbol"] == "BTCUSDT")["price"]
    )
    eth_price = float(
        next(item for item in data if item["symbol"] == "ETHUSDT")["price"]
    )

    res_btc, sop_btc = round(btc_price * 1.005, -2), round(
        btc_price * 0.995, -2
    )
    res_eth, sop_eth = round(eth_price * 1.01, -2), round(eth_price * 0.99, -2)

    mensaje = (
        f"📰 **MERCADO AHORA — {ahora}**\n\n"
        f"📍 *Sesión activa:* {sesion}\n"
        f"🧠 *Análisis:* {insight}\n\n"
        f"🔍 **BTC (Bitcoin)**\n"
        f"Precio: ${btc_price:,.0f}\n"
        f"⚖️ FVG: {get_imbalance('BTCUSDT')}\n"
        f"🎯 Si no aguanta ~${sop_btc:,.0f}, buscamos liquidez abajo.\n\n"
        f"🔍 **ETH (Ethereum)**\n"
        f"Precio: ${eth_price:,.0f}\n"
        f"⚖️ FVG: {get_imbalance('ETHUSDT')}\n"
        f"🎯 Si no aguanta ~${sop_eth:,.0f}, buscamos liquidez abajo.\n\n"
        f"📊 **Niveles clave**\n"
        f"🔴 BTC Res: ${res_btc:,.0f} · ETH Res: ${res_eth:,.0f}\n"
        f"🟢 BTC Sop: ${sop_btc:,.0f} · ETH Sop: ${sop_eth:,.0f}\n\n"
        f"🤖 *Reporte generado por IA — Gestión de riesgo obligatoria*"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    respuesta = requests.post(
        url,
        json={"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"},
    )
    print("Respuesta de Telegram:", respuesta.text)
  except Exception as e:
    print(f"Error crítico en reporte: {e}")


def bot_loop():
  print("🤖 Hilo del Bot Director Activo...")
  time.sleep(60)
  while True:
    generar_reporte_director()
    time.sleep(14400)


if __name__ == "__main__":
  t = threading.Thread(target=bot_loop)
  t.daemon = True
  TELEGRAM_TOKEN = os.environ.get("8944132671:AAEZR2CcxNM1-Qj-Hh5ApEWmdkR0eB_afrs")
CHAT_ID = os.environ.get("8982812050")
  t.start()
def bot_loop():
  print("🤖 Hilo del Bot Director Activo...")
  time.sleep(60)  # Espera 1 minuto al arrancar
  while True:
    generar_reporte_director()
    time.sleep(14400)  # Espera 4 horas (14400 segundos) entre reporte y reporte

  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
