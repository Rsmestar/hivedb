FROM python:3.9-slim

WORKDIR /app

# تثبيت الحزم الأساسية
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات وتثبيتها
COPY server/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir uvicorn gunicorn

# إنشاء مجلد التخزين
RUN mkdir -p cells

# نسخ ملفات الخادم
COPY server/ .

# تعريف متغير البيئة للمنفذ
ENV PORT=8000

# تعريض المنفذ
EXPOSE 8000

# أمر بدء التشغيل
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:$PORT"]
