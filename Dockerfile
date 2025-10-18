# =========================================================================
# المرحلة الأولى: مرحلة البناء (Builder Stage)
#
# هذه المرحلة تقوم بتثبيت الاعتماديات وإنشاء بيئة التشغيل.
# سيتم نسخ الملفات الضرورية فقط إلى المرحلة النهائية.
# =========================================================================
FROM python:3.10-slim-buster AS builder

# تعيين مجلد العمل
WORKDIR /app

# تحديث مدير الحزم وتثبيت الاعتماديات اللازمة للنظام (بما في ذلك ffmpeg)
# --no-install-recommends يقلل من حجم التثبيت
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    mediainfo \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف الاعتماديات أولاً للاستفادة من التخزين المؤقت (caching) لـ Docker
COPY requirements.txt .

# تثبيت حزم بايثون
# --no-cache-dir يقلل من حجم الصورة
RUN pip install --no-cache-dir -r requirements.txt

# =========================================================================
# المرحلة الثانية: مرحلة الإنتاج (Production Stage)
#
# هذه هي الصورة النهائية خفيفة الوزن التي سيتم تشغيل التطبيق فيها.
# إنها ترث فقط الملفات الضرورية من مرحلة البناء.
# =========================================================================
FROM python:3.10-slim-buster

# تعيين مجلد العمل
WORKDIR /app

# نسخ الاعتماديات المثبتة من مرحلة البناء
COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=builder /usr/bin/ffmpeg /usr/bin/ffmpeg
COPY --from=builder /usr/bin/mediainfo /usr/bin/mediainfo

# نسخ كود التطبيق
COPY . .

# تحديد المنفذ الذي سيعمل عليه التطبيق (سيتم تعيين متغير البيئة PORT بواسطة Koyeb)
EXPOSE 8080

# الأمر الافتراضي لتشغيل التطبيق
CMD ["python3", "magic.py"]
