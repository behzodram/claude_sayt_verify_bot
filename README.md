# 🔐 Telegram Verification Bot + Web System

Bu loyiha Telegram bot orqali foydalanuvchilarni tasdiqlash va web sahifaga kirish huquqini berish tizimini amalga oshiradi.

## 📋 Xususiyatlar

- ✅ Telegram bot orqali 4 raqamli tasdiqlash kodi generatsiyasi
- ⏱️ 1 daqiqalik expire time bilan kod amal qiladi
- 🔒 Flask web ilovasi orqali tasdiqlash
- 🔥 Firebase Realtime Database ga foydalanuvchilarni saqlash
- 🎨 Zamonaviy va responsive UI dizayni
- 🔐 Session bilan xavfsiz autentifikatsiya

## 🚀 O'rnatish

### 1. Kerakli kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 2. Telegram Bot yaratish

1. [@BotFather](https://t.me/botfather) ga o'ting
2. `/newbot` buyrug'ini yuboring
3. Bot nomi va username kiriting
4. Bot tokenni saqlang

### 3. Firebase sozlash

1. [Firebase Console](https://console.firebase.google.com/) ga kiring
2. Yangi loyiha yarating
3. Realtime Database ni yoqing
4. Service Account key yuklab oling
5. Key ma'lumotlarini `config.py` ga kiriting

### 4. Config.py ni sozlash

`config.py` faylida quyidagilarni o'zgartiring:

```python
BOT_TOKEN = 'sizning_bot_tokeningiz'
SECRET_KEY = 'xavfsiz_secret_key'

FIREBASE_CONFIG = {
    'project_id': 'sizning-project-id',
    'private_key': 'sizning-private-key',
    'client_email': 'sizning-email',
    'databaseURL': 'https://sizning-project.firebaseio.com'
}
```

### 5. Environment Variables (ixtiyoriy)

`.env` fayl yaratib quyidagilarni qo'shing:

```env
BOT_TOKEN=your_bot_token_here
SECRET_KEY=your_secret_key_here
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your@email.com
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com
```

## 🎯 Ishga tushirish

### Botni ishga tushirish

Yangi terminal oynasida:

```bash
python bot.py
```

### Web ilovani ishga tushirish

Boshqa terminal oynasida:

```bash
python main.py
```

Yoki Windows uchun:

```bash
run.bat
```

## 📖 Foydalanish

### Foydalanuvchi uchun:

1. Web sahifaga kiring: `http://localhost:5000`
2. Telegram botga o'ting va `/start` buyrug'ini yuboring
3. Bot sizga 4 raqamli kod va Telegram ID yuboradi
4. Web sahifada Telegram ID va kodni kiriting
5. Tasdiqlangandan keyin dashboardga yo'naltrilasiz

### Bot buyruqlari:

- `/start` - Yangi tasdiqlash kodi olish
- `/verify` - Tasdiqlash kodi olish (start bilan bir xil)

## 🏗️ Loyiha strukturasi

```
CLAUDE_SAYT_VERIFY_BOT/
├── app/
│   ├── bot.py              # Telegram bot
│   ├── main.py             # Flask web ilovasi
│   └── config.py           # Konfiguratsiya
├── templates/
│   ├── index.html          # Tasdiqlash sahifasi
│   └── dashboard.html      # Asosiy dashboard
├── verification_data.json  # Kodlar saqlash (auto-yaratiladi)
├── requirements.txt        # Python kutubxonalar
├── run.bat                # Windows uchun ishga tushirish
└── README.md              # Dokumentatsiya
```

## 🔧 Texnologiyalar

- **Backend:** Python Flask
- **Bot:** python-telegram-bot
- **Database:** Firebase Realtime Database
- **Frontend:** HTML, CSS, JavaScript (Vanilla)
- **Storage:** JSON file (local verification codes)

## 🔒 Xavfsizlik

- ✅ 4 raqamli tasdiqlash kodi
- ✅ 1 daqiqalik expire time
- ✅ Session-based authentication
- ✅ Firebase Realtime Database himoyasi
- ✅ Ishlatilgan kodlar avtomatik o'chiriladi
- ✅ CSRF himoyasi (Flask session)

## 📝 Muhim eslatmalar

1. **Production uchun:**
   - `SECRET_KEY` ni xavfsiz qiymatga o'zgartiring
   - HTTPS yoqing (`SESSION_COOKIE_SECURE = True`)
   - Firebase xavfsizlik qoidalarini sozlang
   - Environment variables ishlatish tavsiya etiladi

2. **Kod saqlash:**
   - Hozirda `verification_data.json` faylida saqlanadi
   - Production uchun Redis yoki database ishlatish yaxshiroq
   - Har safar restart bo'lganda kodlar tiklanadi

3. **Bot username:**
   - `index.html` da bot username ni o'zgartiring:
   ```html
   <a href="https://t.me/YOUR_BOT_USERNAME" ...>
   ```

## 🐛 Muammolarni hal qilish

### Bot ishlamayapti:
- Bot tokenni tekshiring
- Internetga ulanishni tekshiring
- `python-telegram-bot` versiyasini tekshiring

### Web sahifa ochilmayapti:
- 5000-port bandmi tekshiring
- Flask o'rnatilganligini tekshiring
- Log xabarlarni o'qing

### Firebase xatolik:
- Firebase kredentiallarni tekshiring
- Database URL to'g'riligini tasdiqlang
- Realtime Database yoqilganligini tekshiring

## 📞 Yordam

Savollar bo'lsa:
1. README.md ni diqqat bilan o'qing
2. Log fayllarni tekshiring
3. Error xabarlarni o'qing

## 📜 Litsenziya

Bu loyiha MIT litsenziyasi ostida tarqatiladi.

## 🎉 Qo'shimcha funksiyalar (kelajakda)

- [ ] Email tasdiqlash
- [ ] 2FA (Two-Factor Authentication)
- [ ] Foydalanuvchi profil sahifasi
- [ ] Admin panel
- [ ] Statistika va analytics
- [ ] Multi-language support
- [ ] Redis integration
- [ ] Docker support

---

**Muallif:** Claude AI yordamida yaratildi  
**Sana:** 2026-01-30