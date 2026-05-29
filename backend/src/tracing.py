"""
OpenTelemetry tracing kurulumu — Jaeger'e OTLP gRPC ile gönderir.

`settings.enable_tracing` False ise hiçbir şey yapmaz (test ortamında).
FastAPI ve SQLAlchemy auto-instrument; her HTTP request + DB sorgu trace edilir.
"""
from .config import settings


def setup_tracing(app, engine):
    """FastAPI app + SQLAlchemy engine'i Jaeger'a bağla."""
    if not settings.enable_tracing:
        return

    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

    resource = Resource.create({"service.name": settings.otel_service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(
        endpoint=settings.otel_exporter_otlp_endpoint,
        insecure=True,
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app, excluded_urls="/health,/metrics")
    SQLAlchemyInstrumentor().instrument(engine=engine)
