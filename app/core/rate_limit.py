from collections import defaultdict, deque
import math
import threading
import time

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.audit_logger import log_security_event

# Taille maximale autorisée pour le corps d'une requête HTTP (64 Ko)
MAX_REQUEST_BODY_BYTES = 65_536


class SlidingWindowRateLimiter:
    """Limiteur de débit mémoire thread-safe par fenêtre glissante."""

    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()
        self._last_cleanup = time.monotonic()

    def check(self, key: str, max_requests: int, window_seconds: int) -> tuple[bool, int]:
        now = time.monotonic()
        cutoff = now - window_seconds

        with self._lock:
            # Nettoyage périodique des clés expirées pour éviter toute fuite mémoire
            if now - self._last_cleanup > 300:
                expired_keys = [
                    k for k, q in self._hits.items() if not q or q[-1] < now - 600
                ]
                for k in expired_keys:
                    del self._hits[k]
                self._last_cleanup = now

            bucket = self._hits[key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()

            if len(bucket) >= max_requests:
                retry_after = max(1, math.ceil(window_seconds - (now - bucket[0])))
                return False, retry_after

            bucket.append(now)
            return True, 0

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


rate_limiter = SlidingWindowRateLimiter()


def get_client_ip(request: Request) -> str:
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


async def rate_limit_and_size_middleware(request: Request, call_next):
    # 1. Plafonnement de la taille des requêtes entrantes (protection anti-DoS mémoire)
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > MAX_REQUEST_BODY_BYTES:
                client_ip = get_client_ip(request)
                log_security_event(
                    "PAYLOAD_TOO_LARGE",
                    ip=client_ip,
                    path=request.url.path,
                    bytes=content_length,
                )
                return JSONResponse(
                    status_code=413,
                    content={
                        "detail": "La taille de la requête dépasse la limite autorisée (64 Ko)."
                    },
                )
        except ValueError:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "En-tête Content-Length invalide."},
            )

    if request.method in {"POST", "PUT", "PATCH"}:
        body_bytes = await request.body()
        if len(body_bytes) > MAX_REQUEST_BODY_BYTES:
            client_ip = get_client_ip(request)
            log_security_event(
                "PAYLOAD_TOO_LARGE",
                ip=client_ip,
                path=request.url.path,
                bytes=len(body_bytes),
            )
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={
                    "detail": "La taille de la requête dépasse la limite autorisée (64 Ko)."
                },
            )

    # 2. Plafonnement du nombre de requêtes (Rate Limiting par IP et par sensibilité de route)
    if request.method != "OPTIONS":
        client_ip = get_client_ip(request)
        path = request.url.path

        if path in {"/api/auth/mot-de-passe-oublie", "/api/auth/register"}:
            allowed, retry_after = rate_limiter.check(
                f"strict:{path}:{client_ip}", max_requests=5, window_seconds=300
            )
        elif path in {"/api/auth/login", "/api/auth/reinitialiser-mot-de-passe"}:
            allowed, retry_after = rate_limiter.check(
                f"auth:{path}:{client_ip}", max_requests=10, window_seconds=60
            )
        else:
            allowed, retry_after = rate_limiter.check(
                f"api:{client_ip}", max_requests=120, window_seconds=60
            )

        if not allowed:
            log_security_event(
                "RATE_LIMIT_BLOCKED",
                ip=client_ip,
                path=path,
                retry_after=retry_after,
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={"Retry-After": str(retry_after)},
                content={
                    "detail": f"Trop de tentatives. Veuillez patienter {retry_after} secondes avant de réessayer."
                },
            )

    return await call_next(request)
