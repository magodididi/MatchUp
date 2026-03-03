# tests/test_utils.py
from auth.routes import calculate_zodiac  # теперь импортируем из routes (там функция)

def test_calculate_zodiac():
    assert calculate_zodiac(23, 7) == "Лев"
    assert calculate_zodiac(22, 12) == "Козерог"
    assert calculate_zodiac(1, 1) == "Козерог"
    assert calculate_zodiac(31, 12) == "Козерог"
    assert calculate_zodiac(20, 2) == "Рыбы"