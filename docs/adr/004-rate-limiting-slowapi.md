# ADR-004: Rate Limiting with slowapi

**Status:** Accepted
**Date:** 2026-02-17
**Context:** AQUA COMMUNIS Sprint — Batch 4

## Context

The syllabus generation endpoints (`POST /syllabus/generate`, `GET /api/syllabus/generate`) write to the database on every call. Without rate limiting, a single client could create unbounded rows in the syllabus schema.

## Decision

Use `slowapi` (a Starlette/FastAPI wrapper around `limits`) with in-memory storage:

- `POST /syllabus/generate` — 10 requests per minute per IP
- `GET /api/syllabus/generate` — 20 requests per minute per IP
- Key function: `get_remote_address` (client IP)
- Exceeding the limit returns HTTP 429

## Consequences

**Pros:**
- Prevents abuse of write-heavy endpoints
- No external dependencies (in-memory rate tracking)
- Easy to configure per-route with decorators

**Cons:**
- In-memory storage resets on process restart
- Not shared across multiple instances (same limitation as RoomManager — see ADR-003)

**Migration path:** Switch to Redis-backed storage via `limits` library's Redis backend if horizontal scaling is needed.
