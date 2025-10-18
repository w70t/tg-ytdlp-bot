# استخدم صورة أساسية أحدث (Bullseye بدلاً من Buster)
FROM python:3.10-slim-bullseye AS builder

WORKDIR /app

# هذا الأمر سيعمل الآن لأن مستودعات Bullseye نشطة
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg mediainfo && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# استخدم نفس الصورة الأساسية في مرحلة الإنتاج
FROM python:3.10-slim-bullseye

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=builder /usr/bin/ffmpeg /usr/bin/ffmpeg
COPY --from=builder /usr/bin/mediainfo /usr/bin/mediainfo

COPY . .

EXPOSE 8080

CMD ["python3", "magic.py"]
