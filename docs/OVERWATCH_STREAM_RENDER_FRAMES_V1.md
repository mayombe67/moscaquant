# OVERWATCH Stream & Public Render Frames v1

## Purpose

Raw SITE-19B telemetry may eventually arrive faster than a browser should render it.

The authoritative stream and the Panopticon render stream are therefore separate.

```text
authoritative OVERWATCH telemetry
        |
        v
ordered StreamSampleV1 sequence
        |
        v
deterministic frame grouping
        |
        v
sanitized public projection
        |
        v
RenderFrameV1
        |
        v
Panopticon live/replay renderer
```

The public render stream is a projection of evidence.

It is not a replacement for the evidence.

## Authoritative ordering

Each stream sample receives a monotonically increasing integer `sequence`.

Version 1 requires contiguous sequence ranges when building render frames.

A gap is treated as an error rather than silently skipped.

The sequence number is transport/replay order, not a biological timestamp.

## Render frames

A `RenderFrameV1` contains:

- frame index;
- first source sequence;
- last source sequence;
- source event IDs;
- source event-state hashes;
- sanitized public events;
- deterministic frame hash.

This means every visible public frame can be traced back to the authoritative events that
produced it.

## Deterministic downsampling

Version 1 deliberately uses a boring deterministic rule:

> Group at most N consecutive authoritative events into each render frame.

There is no data-dependent dropping, random sampling or "interesting event" selection.

Given the same ordered source stream and the same maximum frame size, frame boundaries are
identical.

More sophisticated time-based or semantic downsampling may be introduced later, but must be
versioned and deterministic.

## Public projection

Render frames use the existing OVERWATCH public projection.

Private fields must therefore be removed before data reaches the public frame payload.

The frame retains source event IDs and state hashes so public display can still be linked back
to RECEIPTS/provenance where appropriate.

## Live versus replay

The same render-frame representation should support both:

### Live

```text
new authoritative samples
        ↓
render frame
        ↓
browser
```

### Replay

```text
stored authoritative samples
        ↓
same deterministic grouping
        ↓
same render-frame contract
        ↓
browser
```

This reduces the chance that "live MORTY" and "historical MORTY" become two subtly different
systems.

## Smooth rendering

Panopticon may interpolate between render frames for visual smoothness.

Interpolation is presentation.

It must not create new scientific telemetry or rewrite the source event sequence.

For example, a browser may interpolate a wing angle between two recorded states at 60 FPS
while the authoritative motor telemetry is sampled more slowly.

The interpolated pixels are not new evidence.

## Frame integrity

Each frame is hashed from its stable frame content.

`verify_frame_source_hashes(...)` additionally confirms that the frame's source event IDs and
state hashes still correspond to the supplied authoritative samples.

A mutated source state therefore breaks verification.

## Main-page discipline

The live Panopticon page should consume only the public render information it needs.

It does not need to display every telemetry event simultaneously.

Detailed event history, RECEIPTS, modifier history, achievements and other secondary material
belong on deeper surfaces.

## Next steps

After this contract, the remaining bridge to a live viewer is:

- transport batching/backpressure;
- render-frame streaming endpoint;
- replay/live cursor handoff;
- divergence/KILLFEED telemetry;
- minimal public debug viewer;
- production implementation inside THIS THING OF OURS.
