# Panopticon Lightsail Cutover v1

## Goal

Replace the static SITE-19B placeholder with the first real public debug viewer while keeping
the current site and WARDEN deployment intact.

## Safety rules

This cutover does not expose:

- WARDEN IPC;
- raw OVERWATCH telemetry;
- private runtime directories;
- credentials;
- brokerage/account data;
- classified modifier catalog.

Only sanitized `overwatch.render-frame.v1` JSON is served publicly.

## Files

```text
deploy/scripts/deploy_panopticon_debug_viewer.sh
deploy/scripts/publish_initial_panopticon_frame.py
```

The deployment helper intentionally does **not** rewrite the current Nginx virtual host.

It installs the public-feed snippet and prints the small location block to add manually.

## Expected public URLs

After Nginx wiring:

```text
https://moscaquant.com/panopticon/
https://moscaquant.com/api/panopticon/render-frame
```

## Initial state

The first frame is explicitly marked:

```text
feed_mode = REFERENCE
status_text = SITE-19B PUBLIC FEED INITIALIZED
```

It must not be represented as live MQ-001 activity.

Once an actual public-safe OVERWATCH producer is connected, the file may be updated through
the same atomic publisher contract.

## Cutover sequence

1. Pull current `main` on the Lightsail host.
2. Run:

```bash
cd ~/projects/moscaquant
source .venv/bin/activate
bash deploy/scripts/deploy_panopticon_debug_viewer.sh
```

3. Add the printed Nginx include and `/panopticon/` location to the existing TLS server block.
4. Run:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

5. Verify both public URLs.
6. Replace the existing placeholder section/link/embed on the main site with `/panopticon/`.

## Rollback

Because this is additive, rollback is simple:

- remove/comment the two Nginx additions;
- reload Nginx;
- restore the old placeholder markup if necessary.

No WARDEN or scientific runtime configuration needs to change.
