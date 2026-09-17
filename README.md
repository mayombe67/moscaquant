# MoscaQuant

## Current Project State

MoscaQuant has completed MQ-6 — Deploy the Warden.

- MQ-1 through MQ-3: frozen scientific foundation and causal evidence
- MQ-4: Neuroscope COMPLETE
- MQ-5: intervention and perturbation program COMPLETE — accepted with documented limitations
- MQ-6: WARDEN-01 authority and production-containment hardening COMPLETE under tested local conditions
- MQ-7: Awaken the Oracle is the next MQ phase

WARDEN-01 is maintained separately from the public scientific implementation. The public repository contains the scientific system, experiment records, Neuroscope, sanitized architecture, and reproducibility material. Private operational components include Warden implementation, authoritative state handling, deployment internals, credentials, signing material, and future external-execution adapters.

Current financial boundary:

- Financial semantics: NOT ASSIGNED
- Broker integration: NONE
- Exchange integration: NONE
- External execution: DISABLED
- Live capital policy: NOT ASSIGNED

MQ-6 does not retroactively change any MQ-1 through MQ-5 scientific result.

Cloud migration is an infrastructure activity, not a new scientific MQ phase, and must preserve the accepted scientific and authority boundaries.
## Public Deployment

Canonical URL: **https://moscaquant.com**

MoscaQuant currently uses a low-cost AWS baseline deployment with a path to elastic compute.

The current host runs the public web surface, MQ-001 runtime, and WARDEN-01 as separate services and operating-system identities. WARDEN-01 remains local-only, exposes no public network service, and requires no broker, exchange, or wallet credentials.

Heavy scientific compute may later burst to ephemeral workers without changing scientific configuration, accepted experimental semantics, or the Warden authority boundary.

Current public surface: temporary MoscaQuant coming-soon page.

### Verified cloud baseline

The initial MoscaQuant cloud baseline has been deployed and verified.

Verified properties:

- `moscaquant.com` is served over TLS through Nginx.
- `www.moscaquant.com` redirects to the canonical apex domain.
- automated certificate renewal passes a Certbot dry-run.
- `/healthz` provides a minimal public host-health check.
- Neuroscope is deployed as a static, read-only science surface at `/neuroscope/`.
- Neuroscope exposes accepted scientific artifacts only and provides no execution or authority path.
- WARDEN-01 remains a local-only private authority service and is not exposed through Nginx or public DNS.
- WARDEN-01 automatically recovers after host reboot.
- authoritative state survives host reboot.
- the unprivileged `ubuntu` account cannot access WARDEN-01 IPC or authoritative state.

The public science deployment verified at this checkpoint corresponds to commit:

`6e24093f9013b0d0c2600d669e9bb54dce90cfd4`

Deployment state does not alter accepted scientific configuration or experiment semantics.
