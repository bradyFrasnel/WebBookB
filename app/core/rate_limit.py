from collections import defaultdict, deque
import math
import threading
import time

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.audit_logger import log_security_event

# Taille maximale autorisée pour le corps d'une requête HTTP (64 Ko)
MAX_REQUEST_BODY_BYTES = 65_536

# Paramètres de verrouillage anti-force brute sur la connexion
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 300  # 5 minutes


def format_wait_fr(seconds: int) -> str:
    mins, secs = divmod(max(1, seconds), 60)
    if mins > 0 and secs > 0:
        return f"{mins} min {secs:02d} s"
    if mins > 0:
        return f"{mins} minute{'s' if mins > 1 else ''}"
    return f"{secs} seconde{'s' if secs > 1 else ''}"


class LoginAttemptTracker:
    """Verrouille l'authentification pendant 5 minutes après 5 tentatives échouées."""

    def __init__(self) -> None:
        self._failures: dict[str, deque[float]] = defaultdict(deque)
        self._locked_until: dict[str, float] = {}
        self._lock = threading.Lock()

    def check_locked(self, key: str) -> tuple[bool, int]:
        now = time.monotonic()
        with self._lock:
            until = self._locked_until.get(key, 0.0)
            if until > now:
                return True, max(1, math.ceil(until - now))
            if key in self._locked_until:
                del self._locked_until[key]
                self._failures.pop(key, None)
            return False, 0

    def record_failure(self, key: str) -> tuple[bool, int, int]:
        now = time.monotonic()
        cutoff = now - LOGIN_LOCKOUT_SECONDS
        with self._lock:
            until = self._locked_until.get(key, 0.0)
            if until > now:
                return True, max(1, math.ceil(until - now)), 0

            bucket = self._failures[key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()

            bucket.append(now)
            if len(bucket) >= MAX_LOGIN_ATTEMPTS:
                self._locked_until[key] = now + LOGIN_LOCKOUT_SECONDS
                bucket.clear()
                return True, LOGIN_LOCKOUT_SECONDS, 0

            remaining = MAX_LOGIN_ATTEMPTS - len(bucket)
            return False, 0, remaining

    def record_success(self, key: str) -> None:
        with self._lock:
            self._failures.pop(key, None)
            self._locked_until.pop(key, None)

    def reset(self) -> None:
        with self._lock:
            self._failures.clear()
            self._locked_until.clear()


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


login_tracker = LoginAttemptTracker()
rate_limiter = SlidingWindowRateLimiter()


def get_client_ip(request: Request) -> str:
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()
    true_ip = request.headers.get("true-client-ip")
    if true_ip:
        return true_ip.strip()
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


async def rate_limit_and_size_middleware(request: Request, call_next):
    # 1. Plafonnement de la taille des requêtes entrantes (64 Ko)
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
                status_code=413,
                content={
                    "detail": "La taille de la requête dépasse la limite autorisée (64 Ko)."
                },
            )

    # 2. Contrôle de verrouillage et plafonnement de débit
    if request.method != "OPTIONS":
        client_ip = get_client_ip(request)
        path = request.url.path

        # Verrouillage strict de 5 minutes après 5 échecs sur /api/auth/login
        if path == "/api/auth/login":
            locked, retry_after = login_tracker.check_locked(client_ip)
            if locked:
                log_security_event(
                    "LOGIN_LOCKED_BLOCKED",
                    ip=client_ip,
                    retry_after=retry_after,
                )
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    headers={"Retry-After": str(retry_after)},
                    content={
                        "detail": f"Trop de tentatives (5/5). Connexion bloquée pendant encore {format_wait_fr(retry_after)}.",
                        "retry_after": retry_after,
                    },
                )

        if path in {
            "/api/auth/mot-de-passe-oublie",
            "/api/auth/register",
            "/api/auth/reinitialiser-mot-de-passe",
        }:
            allowed, retry_after = rate_limiter.check(
                f"strict:{path}:{client_ip}", max_requests=5, window_seconds=300
            )
        elif path == "/api/auth/login":
            # Plafond global de sécurité même en cas d'identifiants valides répétés
            allowed, retry_after = rate_limiter.check(
                f"login_burst:{client_ip}", max_requests=15, window_seconds=300
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
                    "detail": f"Trop de tentatives. Veuillez patienter {format_wait_fr(retry_after)} avant de réessayer.",
                    "retry_after": retry_after,
                },
            )

    return await call_next(request)
