# Panopticon Public Debug Viewer v1

## Purpose

The first SITE-19B viewer replaces a static placeholder image with a real, deliberately plain
visualization driven by the public render-frame contract.

This is **not** the proprietary production Panopticon experience.

It proves that the public contracts are renderable.

## Location

```text
panopticon/debug_viewer/
  index.html
  style.css
  app.js
```

The viewer is dependency-free static HTML/CSS/JavaScript.

## Data endpoint

The viewer attempts to read:

```text
GET /api/panopticon/render-frame
```

Expected response:

`overwatch.render-frame.v1`

If the endpoint is not available yet, the viewer falls back to a deterministic local demo
feed and clearly labels itself:

`DEMO FEED`

The demo must never be presented as live MQ-001 telemetry.

## Current surface

The viewer displays:

- CELL-67 debug boundary;
- trading desk;
- simplified MQ-001 body;
- wing/leg motion derived from public motor values;
- tether visualization;
- tether tension;
- root displacement;
- body pitch;
- environment ID;
- active modifier badge;
- KILLFEED operational events;
- frame/source sequence identity.

## Rendering boundary

The debug viewer may interpolate or simplify geometry.

It must not invent scientific state.

The public viewer is intentionally ugly compared with the production implementation inside
**THIS THING OF OURS**.

## Placeholder replacement

The deployed site should replace its existing placeholder-image region with this viewer or an
embed/container pointing at this viewer.

The placeholder image should not remain the primary SITE-19B visual once the debug viewer is
deployed.

## Security boundary

The browser endpoint must expose only sanitized public render frames.

The browser must not receive:

- raw private OVERWATCH telemetry;
- credentials;
- Warden IPC details;
- host/network internals;
- broker/account details;
- classified modifier catalog;
- private deployment metadata.

WARDEN remains outside the public HTTP path.

## Deployment shape

Recommended Lightsail layout:

```text
MQ-001 / private producers
        |
        v
OVERWATCH private ingest/storage
        |
        v
public projection + render-frame service
        |
        v
Nginx /api/panopticon/render-frame
        |
        v
static debug viewer
```

The first deployment may serve the viewer statically while the endpoint still returns a
public-safe reference/demo frame.

## Production boundary

The public viewer exists to prove the science and contracts.

The production Panopticon may privately add:

- high-fidelity 3D CELL-67;
- real MORTY rig;
- curated cameras + controlled orbit/pan/zoom;
- advanced lighting;
- modifier environments;
- meme monitor;
- achievements;
- sponsor treatments;
- polished live/replay UI.
