import ee
import requests
import datetime
import os

# ---------------------------------------------------------
# 1. INISIALISASI EARTH ENGINE
# ---------------------------------------------------------
project_id = 'cogent-treat-504315-g3'
ee_key = os.environ.get("GCP_SA_KEY")

if ee_key:
    # Berjalan di GitHub Actions menggunakan Service Account
    credentials = ee.ServiceAccountCredentials(None, key_data=ee_key)
    ee.Initialize(credentials, project=project_id)
else:
    # Berjalan di komputer lokal / Google Colab
    ee.Initialize(project=project_id)

# ---------------------------------------------------------
# 2. KONFIGURASI BOT TELEGRAM & LOKASI
# ---------------------------------------------------------
TELEGRAM_TOKEN = "8766604439:AAFan6okia5TG_WEr1YFUeidnT9MgLqxKh8"
CHAT_ID = "@notifperingatandini"

LOKASI_NAMA = "Kabupaten Kudus (DAS Sungai Wulan)"
LAT, LON = -6.8321, 110.8423
roi = ee.Geometry.Point([LON, LAT])

THRESHOLD_SIAGA = 100.0
THRESHOLD_AWAS = 150.0

# Ambil tanggal hari ini secara otomatis
today = datetime.date.today()
three_days_ago = today - datetime.timedelta(days=3)

# ---------------------------------------------------------
# 3. AMBIL DATA CHIRPS DARI GEE
# ---------------------------------------------------------
collection = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
    .filterDate(three_days_ago.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')) \
    .select('precipitation')

if collection.size().getInfo() == 0:
    print("Tidak ada data CHIRPS yang tersedia untuk rentang tanggal ini.")
    rain_val = None
else:
    chirps_3d = collection.sum().rename('accumulated_precipitation')

    stats = chirps_3d.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=roi,
        scale=5500,
        bestEffort=True,
        tileScale=16
    )

    stats_dict = stats.getInfo()

    if stats_dict and 'accumulated_precipitation' in stats_dict:
        rain_val = stats_dict['accumulated_precipitation']
    else:
        print(f"Gagal menemukan kunci 'accumulated_precipitation' dalam hasil reduksi.")
        print(f"Kunci yang tersedia: {list(stats_dict.keys()) if stats_dict else 'Tidak ada kunci'}")
        rain_val = None

# ---------------------------------------------------------
# 4. FUNGSI KIRIM TELEGRAM
# ---------------------------------------------------------
def send_telegram_alert(message, token, chat_id):
    """Fungsi untuk mengirim notifikasi pesan ke Telegram"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()

# ---------------------------------------------------------
# 5. EVALUASI DAN KIRIM NOTIFIKASI
# ---------------------------------------------------------
if rain_val is not None:
    rain_val_rounded = round(rain_val, 2)

    if rain_val_rounded >= THRESHOLD_AWAS:
        status_code = "🚨 AWAS"
        emoji = "🔴"
        saran = "Potensi banjir tinggi! Segera tingkatkan kesiapsiagaan di area cekungan/bantaran sungai."
    elif rain_val_rounded >= THRESHOLD_SIAGA:
        status_code = "⚠️ SIAGA"
        emoji = "🟡"
        saran = "Waspada luapan debit air sungai dalam 24 jam ke depan."
    else:
        status_code = "✅ AMAN"
        emoji = "🟢"
        saran = "Kondisi hidrometeorologi relatif normal."

    pesan_telegram = f"""
{emoji} *SISTEM PERINGATAN DINI BANJIR (EWS)* {emoji}
---------------------------------------------
📍 *Lokasi Monitor:* {LOKASI_NAMA}
📅 *Tanggal Analisis:* {today.strftime('%d %B %Y')}
🌧️ *Akumulasi Hujan (3-Hari):* {rain_val_rounded} mm
📊 *Status:* *{status_code}*

💡 *Rekomendasi:*
{saran}
---------------------------------------------
_Generated automatically via Google Earth Engine & Python_
"""

    print(f"Hasil Analisis Curah Hujan: {rain_val_rounded} mm")
    print(f"Status: {status_code}")

# Selalu kirim notifikasi ke Telegram (Termasuk status AMAN/SIAGA/AWAS)
    res = send_telegram_alert(pesan_telegram, TELEGRAM_TOKEN, CHAT_ID)
    if res.get("ok"):
        print("🚀 Notifikasi Peringatan Dini BERHASIL terkirim ke Telegram!")
    else:
        print("❌ Gagal mengirim pesan:", res)

else:
    print("Gagal mengambil data curah hujan dari GEE.")
