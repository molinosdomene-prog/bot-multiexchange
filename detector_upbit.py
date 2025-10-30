import requests
import time
from datetime import datetime

# ==============================
# CONFIGURACIÓN DE TELEGRAM
# ==============================
TELEGRAM_TOKEN = "8275618528:AAFH01IIOhx7oeZDOnYRK6CkD9UPChGTHww"
TELEGRAM_CHAT_ID = "6241445577"

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("⚠ Error enviando Telegram:", e)

# ==============================
# CONFIGURACIÓN DEL BOT
# ==============================
CHECK_INTERVAL = 15  # segundos entre revisiones

tokens_upbit_file = "upbit_list.txt"
tokens_bithumb_file = "bithumb_list.txt"
tokens_bitget_file = "bitget_list.txt"
tokens_binance_file = "binance_list.txt"

def load_list(filename):
    try:
        with open(filename, "r") as f:
            return set(line.strip() for line in f.readlines())
    except FileNotFoundError:
        return set()

def save_list(filename, data):
    with open(filename, "w") as f:
        for item in sorted(data):
            f.write(item + "\n")

# ==============================
# APIS
# ==============================
def fetch_upbit():
    r = requests.get("https://api.upbit.com/v1/market/all")
    return {item["market"] for item in r.json()}

def fetch_bithumb():
    r = requests.get("https://api.bithumb.com/public/ticker/ALL_KRW")
    data = r.json()["data"]
    return {"KRW-" + s for s in data.keys() if s != "date"}

def fetch_bitget():
    r = requests.get("https://api.bitget.com/api/spot/v1/public/products")
    return {item["symbolName"] for item in r.json()["data"]}

def fetch_binance():
    r = requests.get("https://api.binance.com/api/v3/exchangeInfo")
    return {item["symbol"] for item in r.json()["symbols"]}

# ==============================
# DETECTAR CAMBIOS
# ==============================
def check_exchange(name, fetch_func, filename):
    print(f"\n🔍 Revisando {name}...")

    old_list = load_list(filename)
    new_list = fetch_func()

    new_pairs = new_list - old_list

    if new_pairs:
        print(f"\n🚨 NUEVO LISTADO DETECTADO EN {name} ({datetime.now()})")

        for p in new_pairs:
            print(f"✅ {name} ha añadido: {p}")
            enviar_telegram(f"🚨 Nuevo listado en {name}: {p}")

    save_list(filename, new_list)

# ==============================
# PRUEBA DE TELEGRAM
# ==============================
enviar_telegram("✅ Bot multiexchange iniciado correctamente")

# ==============================
# LOOP PRINCIPAL
# ==============================
print("✅ BOT MULTI-EXCHANGE INICIADO")
print("Revisando cada", CHECK_INTERVAL, "segundos...")

while True:
    try:
        check_exchange("Upbit", fetch_upbit, tokens_upbit_file)
        check_exchange("Bithumb", fetch_bithumb, tokens_bithumb_file)
        check_exchange("Bitget", fetch_bitget, tokens_bitget_file)
        check_exchange("Binance", fetch_binance, tokens_binance_file)

    except Exception as e:
        print("❌ Error: ", e)

    time.sleep(CHECK_INTERVAL)
