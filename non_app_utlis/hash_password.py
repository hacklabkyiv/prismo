import hashlib

salt = 'some_salt'
password = 'admin'

if __name__ == '__main__':
    final_slat = salt + str(len(password))
    hashed_pass = hashlib.sha256((password + final_slat).encode('utf-8')).hexdigest()
    print(hashed_pass)
