FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# إنشاء مجلد لتخزين الخلايا
RUN mkdir -p cells

# تعريض المنفذ 8000
EXPOSE 8000

# تشغيل الخادم
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
