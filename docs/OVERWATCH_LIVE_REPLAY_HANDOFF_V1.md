# OVERWATCH Live / Replay Handoff & Divergence v1

## Purpose

Panopticon should be able to move between:

- live observation;
- historical replay;

without changing the authoritative scientific stream.

Viewer mode is presentation state.

The underlying event order remains fixed.

## Stream cursor

`StreamCursorV1` identifies:

- run ID;
- authoritative sequence;
- mode (`live` or `replay`);
- optional render-frame index.

A mode handoff preserves the run and sequence.

It must not silently jump to a different scientific state.

## `stream.handoff`

Records a viewer-mode transition such as:

```text
live -> replay
replay -> live
```

The event documents the transition but does not modify experiment state.

## Replay divergence

If reconstruction disagrees with recorded state, emit:

`replay.divergence`

This event is surfaced through the KILLFEED.

Examples:

- state hash differs;
- expected frame missing;
- unexpected frame appears;
- event type differs;
- sample order differs.

The required handling is:

`report_only_no_silent_repair`

A divergence must not be hidden by silently substituting the recorded value or rewriting the
reconstructed stream.

## Stream gaps

If an authoritative sequence is not contiguous, emit:

`stream.gap`

Version 1 handling is:

`report_and_stop_frame_assembly`

The renderer may continue showing the last valid state, but it must not pretend the missing
authoritative samples never existed.

## Why this matters

A live viewer and a replay viewer can otherwise drift into subtly different interpretations
of the same run.

The intended model is:

```text
authoritative stream
        |
        +------> live render frames
        |
        +------> replay reconstruction
                       |
                       v
                 verification
                       |
             mismatch? -> KILLFEED
```

Both surfaces remain accountable to the same source evidence.

## Presentation boundary

Camera movement, UI layout, open panels and viewer scrub position are presentation state.

They do not become scientific telemetry merely because Panopticon records a handoff event.

## Next step

With handoff and divergence semantics frozen, the remaining public bridge to a usable viewer
is:

- bounded transport queues;
- batching/backpressure behavior;
- a minimal public debug viewer;
- production transport/rendering inside THIS THING OF OURS.
