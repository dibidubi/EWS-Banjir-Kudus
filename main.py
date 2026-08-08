import requests
import datetime
import os

# ---------------------------------------------------------
# 1. KONFIGURASI BOT TELEGRAM & LOKASI
# ---------------------------------------------------------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8766604439:AAFan6okia5TG_WEr1YFUeidnT9MgLqxKh8")
CHAT_ID = os.environ.get("CHAT_ID", "@notifperingatandini")

LOKASI_NAMA = "Kabupaten Kudus (DAS Sungai Wulan)"
LAT, LON = -6.8321, 110.8423

# Threshold Akumulasi Hujan 3 Hari (mm)
THRESHOLD_SIAGA = 100.0
THRESHOLD_AWAS = 150.0

# ---------------------------------------------------------
# 2. AMBIL DATA CURAH HUJAN (AKUMULASI 3 HARI: H-2 s.d. H-0)
# ---------------------------------------------------------
# past_days=2 mengambil data 2 hari ke belakang + 1 hari ini = Total 3 Hari
url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&daily=precipitation_sum&past_days=2&timezone=auto"
response = requests.get(url).json()

today = datetime.date.today()

# Ambil list curah hujan 3 hari [2 hari lalu, kemarin, hari ini]
daily_rain_list = response['daily']['precipitation_sum'][:3]
rain_3days_total = sum(daily_rain_list)
rain_val_rounded = round(rain_3days_total, 2)

# Detail per hari untuk informasi di pesan
hujan_2_hari_lalu = round(daily_rain_list[0], 1)
hujan_kemarin = round(daily_rain_list[1], 1)
hujan_hari_ini = round(daily_rain_list[2], 1)

# ---------------------------------------------------------
# 3. EVALUASI STATUS & REKOMENDASI
# ---------------------------------------------------------
if rain_val_rounded >= THRESHOLD_AWAS:
    status_code = "🚨 AWAS"
    emoji = "🔴"
    saran = "Potensi banjir tinggi! Akumulasi hujan 3 hari sangat tinggi. Segera tingkatkan kesiapsiagaan di area cekungan/bantaran sungai."
elif rain_val_rounded >= THRESHOLD_SIAGA:
    status_code = "⚠️ SIAGA"
    emoji = "🟡"
    saran = "Waspada luapan debit air sungai dalam 24 jam ke depan akibat akumulasi hujan beberapa hari."
else:
    status_code = "✅ AMAN"
    emoji = "🟢"
    saran = "Kondisi hidrometeorologi relatif normal."

# ---------------------------------------------------------
# 4. BUAT FORMAT PESAN TELEGRAM
# ---------------------------------------------------------
pesan_telegram = f"""
{emoji} *SISTEM PERINGATAN DINI BANJIR (EWS)* {emoji}
---------------------------------------------
📍 *Lokasi Monitor:* {LOKASI_NAMA}
📅 *Tanggal Analisis:* {today.strftime('%d %B %Y')}
🌧️ *Akumulasi Hujan (3-Hari):* {rain_val_rounded} mm
📊 *Status:* *{status_code}*

🔍 *Rincian Curah Hujan 3 Hari:*
• 2 Hari Lalu: {hujan_2_hari_lalu} mm
• Kemarin: {hujan_kemarin} mm
• Hari Ini: {hujan_hari_ini} mm

💡 *Rekomendasi:*
{saran}
---------------------------------------------
_Generated automatically via Open-Meteo API & Python_
"""

# ---------------------------------------------------------
# 5. KIRIM NOTIFIKASI KE TELEGRAM
# ---------------------------------------------------------
url_tele = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
res = requests.post(url_tele, json={"chat_id": CHAT_ID, "text": pesan_telegram, "parse_mode": "Markdown"}).json()

if res.get("ok"):
    print(f"🚀 Notifikasi Akumulasi 3 Hari ({rain_val_rounded} mm) BERHASIL terkirim ke Telegram!")
else:
    print("❌ Gagal mengirim pesan:", res)
