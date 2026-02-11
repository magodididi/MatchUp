import hashlib
import os

def hash_password(password: str) -> str:
    salt = os.urandom(16).hex()  # случайная соль
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${hashed}"

def verify_password(password: str, hashed: str) -> bool:
    salt, stored_hash = hashed.split("$")
    return hashlib.sha256((salt + password).encode()).hexdigest() == stored_hash
