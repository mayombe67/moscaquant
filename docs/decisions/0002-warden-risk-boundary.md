# ADR-0002: WARDEN-01 Risk Boundary

**Status:** Accepted

MQ-001 proposes trades but never possesses execution authority.

WARDEN-01 independently validates financial actions and owns broker credentials, exposure limits, loss limits, cooldowns, watchdogs, and Sugar Cube Mode.

Communication or validation failure defaults to DENY.

The initial Warden host is a Raspberry Pi 3. Future cloud migration must preserve the logical security boundary between MQ-001 and WARDEN-01.
