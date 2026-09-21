# OVERWATCH Transport Queue & Backpressure v1

## Purpose

Panopticon transport must remain bounded under load.

A burst of telemetry must not cause:

- unbounded memory growth;
- silent scientific-event loss;
- reordering;
- invisible client drift.

Version 1 therefore introduces a small deterministic FIFO queue contract.

## Bounded queue

`BoundedTransportQueueV1` has a fixed capacity.

When space exists:

```text
put(item) -> True
```

When full:

```text
put(item) -> False
```

The queue does **not** silently evict:

- oldest samples;
- newest samples;
- "boring" samples;
- scientifically inconvenient samples.

The caller must react explicitly.

## Backpressure behavior

Version 1 policy:

`caller_must_retry_or_stop_no_silent_drop`

A producer or transport adapter may:

- retry later;
- pause frame production;
- disconnect a slow client;
- spill to an appropriate authoritative storage layer;
- stop the public stream temporarily.

It may not pretend that rejected data entered the queue.

## `transport.backpressure`

When a relevant queue reaches capacity and rejects work, OVERWATCH can emit:

`transport.backpressure`

The event records:

- queue name;
- capacity;
- queued count;
- cumulative rejection count;
- explicit handling rule.

It surfaces through the KILLFEED.

Backpressure is an operational condition, not a biological event.

## Batching

`drain(max_items)` preserves FIFO order.

Transport adapters may batch consecutive public render frames/events for efficiency.

`transport.batch` can record:

- queue name;
- batch size;
- first authoritative sequence;
- last authoritative sequence.

Batch boundaries must not redefine authoritative order.

## Slow viewers

A slow public viewer is not allowed to dictate scientific retention.

The intended architecture is:

```text
authoritative OVERWATCH storage
        |
        v
public projection / render frames
        |
        v
bounded transport queue
        |
        v
browser
```

If the browser falls behind, the product layer may choose to reconnect or resume from a known
cursor.

The authoritative record remains intact.

## Live/replay recovery

Because render frames retain source sequence/hash identity, a disconnected viewer can
eventually resume by:

1. remembering its last valid cursor;
2. requesting replay from that cursor;
3. verifying state;
4. handing back to live mode.

The viewer should never fill a transport gap by inventing intermediate scientific state.

## Public/private boundary

The queue contract is public because it defines reliability semantics.

Production details may remain inside **THIS THING OF OURS**, including:

- WebSocket/SSE implementation;
- load balancers;
- queue technology;
- autoscaling;
- connection fan-out;
- CDN behavior;
- cloud metrics.

The contract remains:

> bounded, ordered, explicit backpressure, no silent scientific-event loss.

## Next step

With storage, replay, render frames, handoff and transport semantics in place, the public repo
is ready for a deliberately minimal Panopticon debug viewer.

That viewer should prove:

- live/render-frame consumption;
- 2D status representation;
- CELL-67 debug pose rendering;
- replay cursor movement;
- active modifier badge;
- divergence/KILLFEED visibility;

without reproducing the proprietary production experience.
