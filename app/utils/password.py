import hashlib

from app.config import get_slat


def hash_password(password: str):
    final_slat = get_slat() + str(len(password))
    hashed_pass = hashlib.sha256((password + final_slat).encode('utf-8')).hexdigest()
    return hashed_pass
