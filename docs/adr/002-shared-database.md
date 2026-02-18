# ADR 002: Shared Database via koinonia-db Package

## Status
Accepted

## Context
ORGAN-VI has four repos (salon-archive, reading-group-curriculum, adaptive-personal-syllabus, community-hub) that all need database access. They share common models (taxonomy, sessions, curricula) and a single Neon PostgreSQL instance.

## Decision
Create a shared `koinonia-db` Python package with SQLAlchemy models, Alembic migrations, and seed data. All ORGAN-VI repos depend on this package.

## Rationale
- **Single source of truth:** One set of models, one migration history, one schema definition
- **Consistency:** All repos see the same table structures and relationships
- **Reusability:** Seed data (taxonomy, curricula, reading lists) defined once, used everywhere
- **Independence:** Each repo adds its own repository layer and business logic on top

## Alternatives Considered
- **Duplicated models:** Each repo defines its own models — leads to drift and inconsistency
- **Microservices with API:** Each repo exposes an API — adds complexity for a single-user system
- **Shared database without shared code:** Raw SQL in each repo — error-prone, no type safety

## Consequences
- All repos must install koinonia-db as a dependency
- Schema changes require updating koinonia-db first, then running migrations
- The koinonia-db package must remain stable and backward-compatible
- Tests can use SQLite for fast local testing via ATTACH DATABASE for schema simulation
