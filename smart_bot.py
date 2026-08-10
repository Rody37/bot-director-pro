def bot_loop():
    print("🤖 Hilo del Bot Centinela 'Élite' Activo...")
    
    initial_prices = get_market_prices()
    for sym in TRACKED_SYMBOLS:
        if sym in initial_prices:
            last_prices[sym] = initial_prices[sym]

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        mensaje_inicio = "🤖 **¡Bot Director Pro Activo!** Sistema actualizado con control por reloj real. 🚀"
        requests.post(url, json={"chat_id": CHAT_ID, "text": mensaje_inicio, "parse_mode": "Markdown"})
        print("Mensaje de inicio enviado a Telegram.")
    except Exception as e:
        print(f"Error enviando mensaje de inicio: {e}")

    # Control de tiempo real (3600 segundos = 1 hora)
    # *Nota: Si quieres probar que los reportes llegan rápido, puedes cambiar temporalmente 3600 por 300 (5 minutos)*
    ultimo_reporte = time.time()
    INTERVALO_REPORTE = 3600 

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

            # Verificación por tiempo real transcurrido
            if time.time() - ultimo_reporte >= INTERVALO_REPORTE:
                generar_reporte("REPORTE PERIÓDICO DE RUTINA (CADA 1 HORA)", current_prices)
                ultimo_reporte = time.time()

            time.sleep(30)
        except Exception as e:
            print(f"Error en bucle: {e}")
            time.sleep(30)

