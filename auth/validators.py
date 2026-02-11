import re

def is_valid_password(password: str) -> bool:
    """Пароль: 6–72 символа, минимум одна буква и одна цифра"""
    if not (6 <= len(password) <= 72):
        return False
    if not re.search(r"[A-Za-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True
