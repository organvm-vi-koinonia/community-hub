# ADR-003: WebSocket Room Manager

**Status:** Accepted
**Date:** 2026-02-17
**Context:** AQUA COMMUNIS Sprint — Batch 5

## Context

ORGAN-VI salons need real-time participation for live sessions. Participants should see each other's messages instantly without page reloads.

## Decision

Implement an in-process `RoomManager` using a dict of `room_id → set[WebSocket]`. No external message broker (Redis Pub/Sub, RabbitMQ) for the initial deployment.

- `GET /salons/{id}/live` serves the live room HTML page
- `WS /ws/salons/{id}` handles WebSocket connections
- Client sends 30s keepalive pings to survive Render's 55s idle timeout
- Auto-reconnect on disconnect with 3s backoff

## Consequences

**Pros:**
- Zero infrastructure cost — no Redis or external broker needed
- Simple deployment — single process on Render
- Latency is minimal (in-process broadcast)

**Cons:**
- No horizontal scaling — rooms are process-local, so a second Render instance wouldn't share rooms
- If the process restarts, all connections drop (auto-reconnect mitigates this)

**Migration path:** If scaling becomes necessary, replace `RoomManager._rooms` dict with Redis Pub/Sub. The `broadcast()` API stays the same.
