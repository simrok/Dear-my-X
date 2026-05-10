FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 시스템 패키지 (asyncpg, cryptography 빌드 등에 필요)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# 의존성 먼저 설치 (캐시 효율)
COPY requirements.txt ./
RUN pip install -r requirements.txt

# 실제 앱 코드는 docker-compose 의 볼륨 마운트로 들어옵니다.
# 운영용 이미지를 만들 때는 아래 주석을 활성화하세요.
# COPY ./app ./app
# COPY ./alembic ./alembic
# COPY ./alembic.ini ./

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
