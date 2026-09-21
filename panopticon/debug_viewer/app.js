(() => {
  "use strict";

  const ENDPOINT = "/api/panopticon/render-frame";
  const POLL_MS = 1000;

  const canvas = document.getElementById("scene");
  const ctx = canvas.getContext("2d");

  const els = {
    liveBadge: document.getElementById("liveBadge"),
    modifierBadge: document.getElementById("modifierBadge"),
    frameLabel: document.getElementById("frameLabel"),
    sequenceLabel: document.getElementById("sequenceLabel"),
    environmentLabel: document.getElementById("environmentLabel"),
    locomotor: document.getElementById("locomotor"),
    tension: document.getElementById("tension"),
    rootY: document.getElementById("rootY"),
    pitch: document.getElementById("pitch"),
    mode: document.getElementById("mode"),
    integrity: document.getElementById("integrity"),
    replay: document.getElementById("replay"),
    killfeed: document.getElementById("killfeed"),
  };

  let demoTick = 0;
  let lastFrame = null;

  function clamp(v, lo, hi) {
    return Math.max(lo, Math.min(hi, Number(v) || 0));
  }

  function demoFrame() {
    demoTick += 1;
    const locomotor = 0.5 + 0.45 * Math.sin(demoTick / 6);
    const rootY = Math.min(locomotor * 0.10, 0.03);
    const blocked = Math.max(0, locomotor * 0.10 - rootY);
    return {
      schema: "overwatch.render-frame.v1",
      frame_index: demoTick,
      source_sequence_start: demoTick,
      source_sequence_end: demoTick,
      public_events: [
        {
          event_type: "motor.state",
          payload: { motor: { locomotor_drive: locomotor } }
        },
        {
          event_type: "constraint.state",
          payload: {
            constraint: {
              environment_id: "CELL-67.v1",
              tether_enabled: true,
              tether_tension_n: blocked * 2.0,
              root_position: { x: 0, y: rootY, z: 0.08 }
            }
          }
        },
        {
          event_type: "physics.pose",
          payload: {
            pose: {
              root_position: { x: 0, y: rootY, z: 0.08 },
              body_pitch_deg: locomotor * 15
            }
          }
        }
      ]
    };
  }

  function eventOf(frame, type) {
    return (frame.public_events || []).find(e => e.event_type === type);
  }

  function extractState(frame) {
    const motor = eventOf(frame, "motor.state")?.payload?.motor || {};
    const constraint = eventOf(frame, "constraint.state")?.payload?.constraint || {};
    const pose = eventOf(frame, "physics.pose")?.payload?.pose || {};
    const modifier = eventOf(frame, "modifier.activated")?.payload?.modifier || null;
    const divergence = (frame.public_events || []).filter(e =>
      e.event_type === "replay.divergence" ||
      e.event_type === "stream.gap" ||
      e.event_type === "transport.backpressure"
    );

    return {
      locomotor: clamp(motor.locomotor_drive, 0, 1),
      tension: Math.max(0, Number(constraint.tether_tension_n) || 0),
      rootY: Number(pose.root_position?.y ?? constraint.root_position?.y ?? 0) || 0,
      pitch: Number(pose.body_pitch_deg) || 0,
      environment: constraint.environment_id || "CELL-67.v1",
      tethered: constraint.tether_enabled !== false,
      modifier,
      divergence,
    };
  }

  function drawScene(state) {
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    ctx.strokeStyle = "#303840";
    ctx.lineWidth = 2;
    ctx.strokeRect(80, 60, w - 160, h - 120);

    // desk
    ctx.strokeStyle = "#69727c";
    ctx.strokeRect(w * 0.56, h * 0.40, w * 0.22, h * 0.08);
    ctx.beginPath();
    ctx.moveTo(w * 0.59, h * 0.48);
    ctx.lineTo(w * 0.57, h * 0.78);
    ctx.moveTo(w * 0.75, h * 0.48);
    ctx.lineTo(w * 0.77, h * 0.78);
    ctx.stroke();

    const x = w * 0.48;
    const y = h * (0.61 - state.rootY * 1.3);
    const bodyLen = 58;
    const pitch = state.pitch * Math.PI / 180;

    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(-pitch);

    // body
    ctx.strokeStyle = "#d9ff62";
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.ellipse(0, 0, bodyLen, 25, 0, 0, Math.PI * 2);
    ctx.stroke();

    // head
    ctx.beginPath();
    ctx.arc(48, -5, 20, 0, Math.PI * 2);
    ctx.stroke();

    // wings
    const wing = 38 + state.locomotor * 28;
    ctx.beginPath();
    ctx.moveTo(-8, -14);
    ctx.lineTo(-30, -wing);
    ctx.moveTo(-8, 14);
    ctx.lineTo(-30, wing);
    ctx.stroke();

    // legs
    ctx.lineWidth = 3;
    [-30, -5, 20].forEach((lx, i) => {
      const span = 38 + state.locomotor * (i + 1) * 5;
      ctx.beginPath();
      ctx.moveTo(lx, 15);
      ctx.lineTo(lx - 18, 15 + span);
      ctx.moveTo(lx, -15);
      ctx.lineTo(lx - 18, -15 - span);
      ctx.stroke();
    });
    ctx.restore();

    // tether / chain
    if (state.tethered) {
      ctx.strokeStyle = state.tension > 0.01 ? "#ff7272" : "#737b84";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(x - 50, y + 8);
      ctx.lineTo(w * 0.36, h * 0.63);
      ctx.stroke();
    }

    // labels
    ctx.fillStyle = "#8e99a4";
    ctx.font = "18px ui-monospace, monospace";
    ctx.fillText("CELL-67.WORLD.v1", 96, 90);
    ctx.fillText("DESK", w * 0.63, h * 0.38);
    ctx.fillText("MQ-001", x - 28, y - 50);
  }

  function render(frame, sourceMode) {
    lastFrame = frame;
    const state = extractState(frame);
    drawScene(state);

    els.liveBadge.textContent = sourceMode === "live" ? "LIVE FEED" : "DEMO FEED";
    els.mode.textContent = sourceMode.toUpperCase();
    els.frameLabel.textContent = `frame ${frame.frame_index ?? 0}`;
    els.sequenceLabel.textContent =
      `seq ${frame.source_sequence_start ?? "?"}–${frame.source_sequence_end ?? "?"}`;
    els.environmentLabel.textContent = state.environment;
    els.locomotor.textContent = state.locomotor.toFixed(2);
    els.tension.textContent = `${state.tension.toFixed(3)} N`;
    els.rootY.textContent = `${state.rootY.toFixed(3)} m`;
    els.pitch.textContent = `${state.pitch.toFixed(1)}°`;

    if (state.modifier) {
      els.modifierBadge.textContent = state.modifier.display_name || "MODIFIER ACTIVE";
      els.modifierBadge.classList.remove("muted");
    } else {
      els.modifierBadge.textContent = "NO ACTIVE MODIFIER";
      els.modifierBadge.classList.add("muted");
    }

    if (state.divergence.length) {
      els.integrity.textContent = "ATTENTION";
      els.killfeed.innerHTML = "";
      state.divergence.slice(-5).forEach(event => {
        const li = document.createElement("li");
        li.textContent = `${event.event_type}: ${event.payload?.detail || event.payload?.handling || "reported"}`;
        els.killfeed.appendChild(li);
      });
    } else {
      els.integrity.textContent = "OK";
    }
  }

  async function poll() {
    try {
      const response = await fetch(ENDPOINT, {
        headers: { "Accept": "application/json" },
        cache: "no-store",
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const frame = await response.json();
      render(frame, "live");
    } catch {
      render(demoFrame(), "demo");
    }
  }

  render(demoFrame(), "demo");
  window.setInterval(poll, POLL_MS);
})();
