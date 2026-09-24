# MoscaQuant Cloud Deployment

## Purpose

This document describes deployment of the **public web / read-only science
surface**.

It is not the authoritative scientific-execution specification for PROJECT
RASPUTIN. That contract is documented separately in
`docs/infrastructure/PROJECT_RASPUTIN.md`.

The public cloud deployment provides a stable web runtime and a public
read-only science surface without changing accepted MoscaQuant scientific
behavior.

Cloud migration is infrastructure work, not a new experimental MQ phase.

## Deployment-plane separation

MoscaQuant has two distinct cloud concerns:

```text
PUBLIC WEB PLANE
source revision -> commit-addressed web release -> Nginx/TLS -> read-only public surface

AUTHORITATIVE SCIENCE PLANE
frozen science -> immutable execution image -> accepted RASPUTIN runtime
              -> content-addressed result + provenance
```

The two planes may share generic cloud primitives, but they do not share
scientific authority. A website deployment cannot create or reclassify a
scientific result, and a RASPUTIN worker is not a public application authority.

## Public architecture

```text
Internet
   |
   v
 Nginx + TLS
   |
   +--> MoscaQuant public surface
   |
   +--> /neuroscope/
          static read-only science artifacts
```

The public web tier is observational.

It does not expose authority, execution, intervention, trading, or WARDEN-01 control paths.

## Neuroscope

Neuroscope is deployed as static content at:

`https://moscaquant.com/neuroscope/`

Neuroscope may display accepted experimental artifacts and completed intervention replays.

It does not modify MQ-001, execute interventions, generate new causal evidence, submit authority decisions, or communicate with WARDEN-01.

## MQ-001 runtime

MQ-001 is the scientific computation layer.

It may run on the same host as other MoscaQuant components, but it is not inherently an Internet-facing service.

Public web exposure and scientific runtime execution are separate concerns.

## WARDEN-01

WARDEN-01 is maintained separately as the private authority boundary.

WARDEN-01 is local-only, exposes no public network service, is not proxied by Nginx, is not reachable from public Neuroscope, and stores authoritative state outside the public web tree.

Future external execution or broker connectivity must remain separate from the public science surface.

## Health endpoint

The production host exposes:

`/healthz`

This endpoint reports only minimal host/web availability.

It does not report WARDEN-01 state or provide authority access.

## Canonical routing

Production routing uses:

```text
http://moscaquant.com      -> https://moscaquant.com/
http://www.moscaquant.com  -> https://moscaquant.com/
https://www.moscaquant.com -> https://moscaquant.com/
```

## Release provenance

Public web releases are deployed into commit-addressed directories:

`/var/www/moscaquant/releases/<public-git-sha>/`

A stable symlink points to the active release:

`/var/www/moscaquant/current`

This preserves a direct relationship between a deployed public science surface and its source revision.

## Scientific invariant

Cloud/runtime configuration may change resource allocation, worker counts, memory limits, filesystem paths, scratch storage, and computational batching.

Cloud/runtime configuration must not change scientific behavior or accepted experiment semantics.
