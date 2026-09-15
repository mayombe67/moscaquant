# ADR-0004: Cloud Portability

**Status:** Accepted

Habitat v1 is the local development environment, not a permanent deployment dependency.

MoscaQuant will support incremental migration from local development to hybrid operation and eventually predominantly cloud-resident infrastructure.

Components must avoid unnecessary machine-specific assumptions. Initial deployment favors containers and Docker Compose over premature orchestration complexity.

WARDEN-01 remains logically isolated regardless of physical hosting.
