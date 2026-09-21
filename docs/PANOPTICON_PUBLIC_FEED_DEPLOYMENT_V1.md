# Panopticon Public Render-Frame Feed Deployment v1

## Purpose

The first live SITE-19B browser endpoint should be as small as possible.

Rather than exposing a new application server directly to the internet, the initial deployment
publishes the latest sanitized `overwatch.render-frame.v1` atomically to disk and lets Nginx
serve that file at:

```text
GET /api/panopticon/render-frame
```

This matches the endpoint already consumed by the public debug viewer.

## Data path

```text
MQ-001 / reference producer
        |
        v
OVERWATCH authoritative events
        |
        v
public projection
        |
        v
RenderFrameV1
        |
        v
atomic latest-frame publisher
        |
        v
/var/lib/moscaquant/panopticon/latest-render-frame.json
        |
        v
Nginx
        |
        v
/api/panopticon/render-frame
        |
        v
Panopticon debug viewer
```

## Why atomic file replacement

The browser must never read a half-written JSON document.

`write_latest_render_frame(...)` therefore:

1. validates the public render-frame contract;
2. writes to a temporary file in the destination directory;
3. flushes and fsyncs the file;
4. atomically replaces the previous latest frame.

Nginx either sees the old complete frame or the new complete frame.

It should not see a partial frame.

## Security boundary

The publisher accepts only the public render-frame schema.

This does not replace the existing sanitizer. The correct pipeline remains:

```text
raw/private telemetry
        ↓
public projection
        ↓
render frame
        ↓
public-feed publisher
```

Never point Nginx at raw OVERWATCH storage.

Never expose:

- WARDEN IPC;
- raw experiment directories;
- credentials;
- private host state;
- brokerage/account data;
- private modifier catalog;
- operational Warden internals.

## Recommended filesystem

Initial Lightsail target:

```text
/var/lib/moscaquant/panopticon/
    latest-render-frame.json
```

The process publishing the file needs write permission.

Nginx needs read permission.

They do not need to share broader runtime permissions.

## Nginx

An example location block is provided at:

```text
deploy/nginx/panopticon-public-feed.conf.example
```

It deliberately uses:

- `no-store` cache control;
- explicit JSON content type;
- `nosniff`;
- same-site CORS origin.

Merge it into the existing TLS server configuration rather than replacing the working site
configuration wholesale.

## Initial producer

The first producer may publish reference/demo render frames while the real MQ-001 stream is
being connected.

The website must clearly identify reference/demo data as non-live.

Once actual MQ-001 public-safe render frames are available, the same file/endpoint contract can
be retained.

## Failure behavior

If publishing stops:

- the last complete JSON frame remains on disk;
- the UI should display stale/offline state once freshness metadata is added;
- the producer should report transport/runtime failure through OVERWATCH.

A future version should add explicit freshness timestamps/heartbeat metadata.

## Next deployment step

After this lands:

1. deploy the debug viewer static assets;
2. configure the Nginx endpoint;
3. publish an initial public-safe reference frame;
4. verify the endpoint from outside the host;
5. replace the site's placeholder visual with the debug viewer;
6. then connect a real OVERWATCH render-frame producer.

This keeps the first SITE-19B launch small and reversible.
