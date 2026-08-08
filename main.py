import requests
import datetime
import os

# ---------------------------------------------------------
# 1. KONFIGURASI
# ---------------------------------------------------------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8766604439:AAFan6okia5TG_WEr1YFUeidnT9MgLqxKh8")
CHAT_ID = os.environ.get("CHAT_ID", "@notifperingatandini")

LOKASI_NAMA = "Kabupaten Kudus (DAS Sungai Wulan)"
LAT, LON = -6.8321, 110.8423

# ---------------------------------------------------------
# 2. AMBIL DATA CURAH HUJAN REAL-TIME
# ---------------------------------------------------------
url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&daily=precipitation_sum&timezone=auto"
response = requests.get(url).json()

today = datetime.date.today()
rain_val = response['daily']['precipitation_sum'][0]  # Total hujan hari ini (mm)
rain_val_rounded = round(rain_val, 2)

# ---------------------------------------------------------
# 3. EVALUASI STATUS & BUAT PESAN
# ---------------------------------------------------------
if rain_val_rounded >= 150.0:
    status_code, emoji, saran = "🚨 AWAS", "🔴", "Potensi banjir tinggi! Segera tingkatkan kesiapsiagaan di area cekungan/bantaran sungai."
elif rain_val_rounded >= 100.0:
    status_code, emoji, saran = "⚠️ SIAGA", "🟡", "Waspada luapan debit air sungai dalam 24 jam ke depan."
else:
    status_code, emoji, saran = "✅ AMAN", "🟢", "Kondisi hidrometeorologi relatif normal."

pesan_telegram = f"""
{emoji} *SISTEM PERINGATAN DINI BANJIR (EWS)* {emoji}
---------------------------------------------
📍 *Lokasi Monitor:* {LOKASI_NAMA}
📅 *Tanggal Analisis:* {today.strftime('%d %B %Y')}
🌧️ *Curah Hujan Hari Ini:* {rain_val_rounded} mm
📊 *Status:* *{status_code}*

💡 *Rekomendasi:*
{saran}
---------------------------------------------
_Generated automatically via Open-Meteo API & Python_
"""

# ---------------------------------------------------------
# 4. KIRIM NOTIFIKASI KE TELEGRAM
# ---------------------------------------------------------
url_tele = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
res = requests.post(url_tele, json={"chat_id": CHAT_ID, "text": pesan_telegram, "parse_mode": "Markdown"}).json()

if res.get("ok"):
    print("🚀 Notifikasi Peringatan Dini BERHASIL terkirim ke Telegram!")
else:
    print("❌ Gagal mengirim pesan:", res)
