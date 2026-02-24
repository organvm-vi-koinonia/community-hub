"""Lightweight CSRF protection via double-submit cookie pattern.

Sets a `csrf_token` cookie on every response and validates that POST
requests include a matching `csrf_token` form field or X-CSRF-Token header.
Safe methods (GET, HEAD, OPTIONS) and API paths (/api/) are exempt.
"""

from __future__ import annotations

import secrets

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

CSRF_COOKIE = "csrf_token"
CSRF_HEADER = "x-csrf-token"
CSRF_FIELD = "csrf_token"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
EXEMPT_PREFIXES = ("/api/", "/ws/", "/health")


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Read or generate token
        token = request.cookies.get(CSRF_COOKIE)  # allow-secret
        if not token:
            token = secrets.token_hex(32)  # allow-secret

        # Make token available to templates via request.state
        request.state.csrf_token = token

        # Validate on unsafe methods for non-exempt paths
        if request.method not in SAFE_METHODS:
            path = request.url.path
            if not any(path.startswith(p) for p in EXEMPT_PREFIXES):
                submitted = request.headers.get(CSRF_HEADER)
                if not submitted:
                    # Check form body
                    content_type = request.headers.get("content-type", "")
                    if "form" in content_type:
                        form = await request.form()
                        submitted = form.get(CSRF_FIELD)

                cookie_token = request.cookies.get(CSRF_COOKIE)
                if not submitted or not cookie_token or submitted != cookie_token:
                    return Response("CSRF token mismatch", status_code=403)

        response = await call_next(request)

        # Set cookie on every response so it's always fresh
        response.set_cookie(
            CSRF_COOKIE,
            token,
            httponly=False,  # JS needs access for AJAX
            samesite="strict",
            secure=request.url.scheme == "https",
            max_age=3600,
        )
        return response
