"""
Merkezi konfigürasyon — tek `.env` dosyasından okunur.

Ortam değişkenleri (root .env veya docker-compose env_file ile gelir):
    DATABASE_URL                  → Postgres bağlantı string'i
    SECRET_KEY                    → JWT imzalama anahtarı
    ACCESS_TOKEN_EXPIRE_MINUTES   → Token TTL (dakika)
    AWS_ENDPOINT_URL              → LocalStack S3 endpoint
    AWS_REGION / KEY / SECRET     → boto3 credentials
    S3_BUCKET                     → Habit fotoğrafları için bucket
    ENABLE_TRACING                → OpenTelemetry aç/kapa (test'lerde kapalı)
    OTEL_EXPORTER_OTLP_ENDPOINT   → Jaeger OTLP gRPC adresi
    OTEL_SERVICE_NAME             → Trace'de görünen servis adı
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── DB ───────────────────────────────────────────
    database_url: str = "postgresql://habituser:habitpass@localhost:5432/habits"

    # ── Auth ─────────────────────────────────────────
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60

    # ── S3 (LocalStack) ──────────────────────────────
    aws_endpoint_url: str = "http://localhost:4566"
    aws_region: str = "us-east-1"
    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"
    s3_bucket: str = "habit-photos"

    # ── Tracing (Jaeger) ────────────────────────────
    enable_tracing: bool = False
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    otel_service_name: str = "habit-tracker-backend"


settings = Settings()
