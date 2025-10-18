# استخدم صورة أساسية حديثة (Bullseye) لضمان توافق الحزم
FROM python:3.10-slim-bullseye

# تعيين مجلد العمل
WORKDIR /app

# تحديث الحزم وتثبيت ffmpeg و mediainfo في خطوة واحدة
# هذا يضمن وجودها في المسار الصحيح
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg mediainfo && \
    rm -rf /var/lib/apt/lists/*

# نسخ ملف الاعتماديات وتثبيت حزم بايثون
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ كود التطبيق بالكامل
COPY . .

# تحديد المنفذ
EXPOSE 8000

# تشغيل البوت
CMD ["python3", "magic.py"]
