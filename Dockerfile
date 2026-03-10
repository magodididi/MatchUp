# Dockerfile
FROM python:3.12-slim

# Установка зависимостей
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Настройка
ENV FLASK_APP=app.py  
ENV FLASK_ENV=production
EXPOSE 5000

# Запуск
CMD ["flask", "run", "--host=0.0.0.0"]