import hashlib

from app.config import get_setting, slat_key


def hash_password(password: str):
    final_slat = get_setting(slat_key) + str(len(password))
    hashed_pass = hashlib.sha256((password + final_slat).encode('utf-8')).hexdigest()
    return hashed_pass
