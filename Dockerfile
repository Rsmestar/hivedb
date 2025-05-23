FROM python:3.9-slim

# تثبيت الحزم الأساسية
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# إنشاء مستخدم غير root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# إنشاء دليل التطبيق ومجلد التخزين
RUN mkdir -p /app /app/cells \
    && chown -R appuser:appuser /app

WORKDIR /app

# نسخ ملف المتطلبات
COPY server/requirements.txt /app/

# إنشاء بيئة افتراضية وتثبيت المتطلبات
RUN python -m venv /app/venv \
    && /app/venv/bin/pip install --upgrade pip \
    && /app/venv/bin/pip install --no-cache-dir -r requirements.txt \
    && /app/venv/bin/pip install --no-cache-dir uvicorn gunicorn

# نسخ ملفات الخادم
COPY server/ /app/
RUN chown -R appuser:appuser /app

# التبديل إلى المستخدم غير root
USER appuser

# تعريف متغير البيئة للمنفذ
ENV PATH="/app/venv/bin:$PATH"
ENV PORT=8000

# تعريض المنفذ
EXPOSE 8000

# أمر بدء التشغيل
CMD ["/app/venv/bin/gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:${PORT}"]
