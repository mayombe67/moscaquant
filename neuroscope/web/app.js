/*
 * MoscaQuant — MQ-4 Neuroscope
 * MQ-4.4 Hybrid Anatomy Viewer
 *
 * Same neurons. Deeper questions.
 *
 * Design constraints
 * ------------------
 * - Consume frozen MQ-1 -> MQ-3 telemetry.
 * - Do NOT alter experimental state/model behavior.
 * - Real soma coordinates remain real soma coordinates.
 * - Missing anatomical coordinates remain explicit topologyFallback.
 * - No invented anatomical positions.
 * - Causal overlay is derived from frozen MQ-3 intervention evidence.
 * - Runtime/machine configuration is separate from scientific semantics.
 */

(() => {
  "use strict";

  const CONFIG = {
    dataUrl:
      window.MOSCAQUANT_NEUROSCOPE_DATA ||
      "./data/replay-A-v1.json",

    runtime:
      window.MOSCAQUANT_RUNTIME ||
      document.documentElement.dataset.runtime ||
      "habitat",

    background: "#06080c",
    nodeReal: "#78a8ff",
    nodeFallback: "#69707d",
    responder: "#ffb84d",
    causalEdge: "#ff7a45",
    selected: "#ffffff",
    grid: "#17202c",
    text: "#c8d1dc",
    dimText: "#75808e",

    realRadius: 1.55,
    fallbackRadius: 1.15,
    responderRadius: 3.0,

    minZoom: 0.15,
    maxZoom: 8.0,

    pointPickRadius: 9,

    initialYaw: -0.35,
    initialPitch: 0.18,
    initialZoom: 1.0,

    fallbackSeparation: 1.2,
  };

  const state = {
    payload: null,

    nodes: [],
    edges: [],

    projected: [],

    width: 0,
    height: 0,
    dpr: Math.min(window.devicePixelRatio || 1, 2),

    yaw: CONFIG.initialYaw,
    pitch: CONFIG.initialPitch,
    zoom: CONFIG.initialZoom,

    panX: 0,
    panY: 0,

    center: [0, 0, 0],
    scale: 1,

    dragging: false,
    dragMode: "rotate",
    lastX: 0,
    lastY: 0,

    selected: null,
    hovered: null,

    showReal: true,
    showFallback: true,
    showCausal: true,
    showRespondersOnly: false,
    showRetina: true,
    showRelay: true,
    showGraded: true,
    showDN: true,
    showResponders: true,

    currentFrame: 0,
    replayPlaying: false,
    replayFps: 8,
    replayTimer: null,

    animationFrame: null,
  };

  let root;
  let canvas;
  let ctx;
  let hud;
  let info;
  let status;
  let controls;

  // ---------------------------------------------------------------------------
  // Bootstrap
  // ---------------------------------------------------------------------------

  async function init() {
    root =
      document.getElementById("neuroscope-root") ||
      document.getElementById("app") ||
      document.body;

    buildUI();

    try {
      setStatus("Loading MQ-4 Neuroscope artifact…");

      const response = await fetch(CONFIG.dataUrl, {
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error(
          `HTTP ${response.status} loading ${CONFIG.dataUrl}`
        );
      }

      const payload = await response.json();

      loadPayload(payload);
      resize();

      setStatus(
        `${state.nodes.length.toLocaleString()} neurons · ` +
          `${countReal().toLocaleString()} real soma · ` +
          `${countFallback().toLocaleString()} topology fallback · ` +
          `${state.edges.length.toLocaleString()} causal edges`
      );

      requestDraw();
    } catch (error) {
      console.error("[Neuroscope]", error);

      setStatus(`Neuroscope load failure: ${error.message}`, true);

      info.innerHTML = `
        <div class="ns-error-title">DATA LOAD FAILED</div>
        <div class="ns-error-body">${escapeHtml(error.message)}</div>
        <div class="ns-error-body">
          Expected artifact:
          <code>${escapeHtml(CONFIG.dataUrl)}</code>
        </div>
      `;
    }
  }

  // ---------------------------------------------------------------------------
  // Payload normalization
  // ---------------------------------------------------------------------------

  function loadPayload(payload) {
    state.payload = payload;

    const rawNodes =
      payload.nodes ||
      payload.neurons ||
      payload.geometry?.nodes ||
      payload.geometry?.neurons ||
      [];

    const rawEdges =
      payload.causalEdges ||
      payload.causal_edges ||
      payload.edges ||
      payload.causal?.edges ||
      [];

    if (!Array.isArray(rawNodes)) {
      throw new Error("Artifact has no valid node array.");
    }

    const responderModelIndices = new Set(
      (payload.responderModelIndices || []).map(Number)
    );

    state.nodes = rawNodes.map((raw, index) => {
      const modelIndex = Number(
        raw.i ??
        raw.modelIndex ??
        raw.model_index ??
        index
      );

      const roles = Number(raw.roles ?? 0);

      const responder =
        responderModelIndices.has(modelIndex) ||
        (roles & 16) !== 0;

      return normalizeNode(
        {
          ...raw,
          responder,
        },
        index
      );
    });
    state.edges = rawEdges.map(normalizeEdge).filter(Boolean);

    calculateSceneBounds();
    updateHud();
    updateFrameSummary();
  }

  function normalizeNode(raw, index) {
    const id =
      raw.bodyId ??
      raw.body_id ??
      raw.neuronId ??
      raw.neuron_id ??
      raw.id ??
      index;

    const source =
      raw.geometrySource ??
      raw.geometry_source ??
      raw.positionSource ??
      raw.position_source ??
      raw.source ??
      "";

    const explicitlyFallback =
      raw.topologyFallback === true ||
      raw.topology_fallback === true ||
      String(source).toLowerCase() === "topologyfallback" ||
      String(source).toLowerCase() === "topology_fallback";

    let soma = vector3(
      raw.somaLocation ??
        raw.soma_location ??
        raw.soma ??
        raw.position ??
        raw.xyz
    );

    let display = vector3(
      raw.displayPosition ??
        raw.display_position ??
        raw.viewerPosition ??
        raw.viewer_position ??
        raw.position ??
        raw.xyz
    );

    const topology = vector3(
      raw.topologyPosition ??
        raw.topology_position ??
        raw.fallbackPosition ??
        raw.fallback_position
    );

    /*
     * IMPORTANT:
     *
     * A fallback viewer position is not anatomical geometry.
     *
     * We permit it for visual topology layout, but preserve the distinction
     * permanently via topologyFallback.
     */

    let topologyFallback = explicitlyFallback;

    if (!soma && topology) {
      topologyFallback = true;
      display = topology;
    }

    if (!soma && display) {
      topologyFallback = true;
    }

    if (soma) {
      display = soma;
      topologyFallback = false;
    }

    if (!display) {
      /*
       * Last-resort deterministic viewer placement.
       *
       * This is NOT anatomical geometry. It exists only so a malformed/missing
       * fallback position does not make a neuron disappear from the viewer.
       */
      topologyFallback = true;
      display = deterministicFallback(index, rawNodesLengthHint());
    }

    return {
      index,
      id: String(id),

      type:
        raw.type ??
        raw.flywireType ??
        raw.flywire_type ??
        raw.cellType ??
        raw.cell_type ??
        "unknown",

      instance:
        raw.instance ??
        "",

      side:
        raw.side ??
        raw.somaSide ??
        raw.soma_side ??
        raw.rootSide ??
        raw.root_side ??
        "",

      position: display,
      soma,

      topologyFallback,

      responder:
        Boolean(
          raw.responder ??
            raw.causalResponder ??
            raw.causal_responder ??
            raw.isResponder ??
            raw.is_responder
        ),

      response:
        raw.response ??
        raw.responseMagnitude ??
        raw.response_magnitude ??
        null,

      latency:
        raw.latency ??
        raw.delay ??
        raw.interventionDelay ??
        raw.intervention_delay ??
        null,

      activity:
        raw.activity ??
        raw.activation ??
        null,

      raw,
    };
  }

  function normalizeEdge(raw) {
    const source =
      raw.source ??
      raw.pre ??
      raw.from ??
      raw.body_pre ??
      raw.pre_id;

    const target =
      raw.target ??
      raw.post ??
      raw.to ??
      raw.body_post ??
      raw.post_id;

    if (source == null || target == null) {
      return null;
    }

    return {
      source: String(source),
      target: String(target),
      weight:
        numberOrNull(raw.weight) ??
        numberOrNull(raw.strength) ??
        1,

      causal:
        raw.causal !== false,

      raw,
    };
  }

  function rawNodesLengthHint() {
    const p = state.payload;

    if (!p) return 12475;

    return (
      p.nodes?.length ||
      p.neurons?.length ||
      p.geometry?.nodes?.length ||
      12475
    );
  }

  // ---------------------------------------------------------------------------
  // Scene geometry
  // ---------------------------------------------------------------------------

  function calculateSceneBounds() {
    const real = state.nodes.filter((n) => !n.topologyFallback);

    const reference = real.length ? real : state.nodes;

    if (!reference.length) {
      state.center = [0, 0, 0];
      state.scale = 1;
      return;
    }

    let minX = Infinity;
    let minY = Infinity;
    let minZ = Infinity;

    let maxX = -Infinity;
    let maxY = -Infinity;
    let maxZ = -Infinity;

    for (const node of reference) {
      const [x, y, z] = node.position;

      minX = Math.min(minX, x);
      minY = Math.min(minY, y);
      minZ = Math.min(minZ, z);

      maxX = Math.max(maxX, x);
      maxY = Math.max(maxY, y);
      maxZ = Math.max(maxZ, z);
    }

    state.center = [
      (minX + maxX) / 2,
      (minY + maxY) / 2,
      (minZ + maxZ) / 2,
    ];

    const extent = Math.max(
      maxX - minX,
      maxY - minY,
      maxZ - minZ,
      1
    );

    state.scale = 1 / extent;
  }

  function deterministicFallback(index, total) {
    /*
     * Visual topology shell only.
     *
     * Deliberately separated from the real anatomical cloud and explicitly
     * tagged topologyFallback.
     */

    const n = Math.max(total, 1);
    const golden = Math.PI * (3 - Math.sqrt(5));

    const y = 1 - (index / Math.max(n - 1, 1)) * 2;
    const radius = Math.sqrt(Math.max(0, 1 - y * y));
    const theta = golden * index;

    return [
      Math.cos(theta) * radius * CONFIG.fallbackSeparation,
      y * CONFIG.fallbackSeparation,
      Math.sin(theta) * radius * CONFIG.fallbackSeparation,
    ];
  }

  // ---------------------------------------------------------------------------
  // Projection
  // ---------------------------------------------------------------------------

  function projectNode(node) {
    const p = node.position;

    let x = p[0];
    let y = p[1];
    let z = p[2];

    if (!node.topologyFallback) {
      x = (x - state.center[0]) * state.scale * 2;
      y = (y - state.center[1]) * state.scale * 2;
      z = (z - state.center[2]) * state.scale * 2;
    } else {
      /*
       * Fallback positions may already be normalized by the builder.
       * If they look like raw EM-scale coordinates, normalize them anyway.
       */
      const magnitude = Math.max(Math.abs(x), Math.abs(y), Math.abs(z));

      if (magnitude > 10) {
        x = (x - state.center[0]) * state.scale * 2;
        y = (y - state.center[1]) * state.scale * 2;
        z = (z - state.center[2]) * state.scale * 2;
      }
    }

    // Yaw — Y axis.
    const cy = Math.cos(state.yaw);
    const sy = Math.sin(state.yaw);

    const x1 = x * cy - z * sy;
    const z1 = x * sy + z * cy;

    // Pitch — X axis.
    const cp = Math.cos(state.pitch);
    const sp = Math.sin(state.pitch);

    const y2 = y * cp - z1 * sp;
    const z2 = y * sp + z1 * cp;

    const perspective = 3.5;
    const depth = Math.max(0.35, perspective + z2);

    const perspectiveScale = perspective / depth;

    const base =
      Math.min(state.width, state.height) *
      0.40 *
      state.zoom;

    return {
      node,

      x:
        state.width / 2 +
        state.panX +
        x1 * base * perspectiveScale,

      y:
        state.height / 2 +
        state.panY -
        y2 * base * perspectiveScale,

      z: z2,

      depth,

      perspectiveScale,
    };
  }

  // ---------------------------------------------------------------------------
  // Rendering
  // ---------------------------------------------------------------------------

  function draw() {
    state.animationFrame = null;

    if (!ctx) return;

    ctx.clearRect(0, 0, state.width, state.height);

    drawBackdrop();

    let visible = state.nodes;

    if (state.showRespondersOnly) {
      visible = visible.filter((n) => n.responder);
    }

    visible = visible.filter((n) => {
      if (n.topologyFallback && !state.showFallback) return false;
      if (!n.topologyFallback && !state.showReal) return false;

      const roles = Number(n.raw?.roles ?? 0);

      const roleBits =
        state.payload?.roleBits || {
          retina: 1,
          relay: 2,
          graded: 4,
          dn: 8,
          responder: 16,
        };

      if (
        (roles & Number(roleBits.retina)) !== 0 &&
        !state.showRetina
      ) return false;

      if (
        (roles & Number(roleBits.relay)) !== 0 &&
        !state.showRelay
      ) return false;

      if (
        (roles & Number(roleBits.graded)) !== 0 &&
        !state.showGraded
      ) return false;

      if (
        (roles & Number(roleBits.dn)) !== 0 &&
        !state.showDN
      ) return false;

      if (
        (roles & Number(roleBits.responder)) !== 0 &&
        !state.showResponders
      ) return false;

      return true;
    });

    state.projected = visible
      .map(projectNode)
      .filter(
        (p) =>
          Number.isFinite(p.x) &&
          Number.isFinite(p.y) &&
          Number.isFinite(p.z)
      )
      .sort((a, b) => b.z - a.z);

    if (state.showCausal) {
      drawCausalEdges();
    }

    drawNodes();
    drawOrientation();
    updateHud();
  }

  function drawBackdrop() {
    ctx.fillStyle = CONFIG.background;
    ctx.fillRect(0, 0, state.width, state.height);

    const spacing = 48;

    ctx.beginPath();
    ctx.strokeStyle = CONFIG.grid;
    ctx.globalAlpha = 0.24;
    ctx.lineWidth = 1;

    for (let x = state.width % spacing; x < state.width; x += spacing) {
      ctx.moveTo(x, 0);
      ctx.lineTo(x, state.height);
    }

    for (let y = state.height % spacing; y < state.height; y += spacing) {
      ctx.moveTo(0, y);
      ctx.lineTo(state.width, y);
    }

    ctx.stroke();
    ctx.globalAlpha = 1;
  }

  function setReplayFrame(frameIndex) {
    const total =
      state.payload?.frames?.length ?? 0;

    if (!total) return;

    state.currentFrame =
      Math.max(
        0,
        Math.min(total - 1, frameIndex)
      );

    const slider =
      document.getElementById("frame-slider");

    if (slider) {
      slider.value =
        String(state.currentFrame);
    }

    updateFrameSummary();
    requestDraw();
  }

  function startReplay() {
    const total =
      state.payload?.frames?.length ?? 0;

    if (!total || state.replayPlaying) return;

    if (state.currentFrame >= total - 1) {
      setReplayFrame(0);
    }

    state.replayPlaying = true;

    const button =
      document.getElementById("frame-play");

    if (button) {
      button.textContent = "PAUSE";
      button.classList.add("active");
    }

    state.replayTimer = window.setInterval(
      () => {
        if (state.currentFrame >= total - 1) {
          stopReplay();
          return;
        }

        setReplayFrame(
          state.currentFrame + 1
        );
      },
      1000 / Math.max(1, state.replayFps)
    );
  }

  function stopReplay() {
    state.replayPlaying = false;

    if (state.replayTimer != null) {
      window.clearInterval(
        state.replayTimer
      );

      state.replayTimer = null;
    }

    const button =
      document.getElementById("frame-play");

    if (button) {
      button.textContent = "PLAY";
      button.classList.remove("active");
    }
  }

  function sparseActivityMap(values) {
    const map = new Map();

    if (!Array.isArray(values)) {
      return map;
    }

    for (const item of values) {
      if (
        Array.isArray(item) &&
        item.length >= 2
      ) {
        map.set(
          Number(item[0]),
          Number(item[1])
        );
      } else if (
        Number.isInteger(item)
      ) {
        map.set(
          Number(item),
          1
        );
      }
    }

    return map;
  }

  function currentFrameActivity() {
    const frame =
      state.payload?.frames?.[
        state.currentFrame
      ];

    if (!frame) {
      return {
        voltage: new Map(),
        effective: new Map(),
        spikes: new Map(),
        responders: new Map(),
      };
    }

    const responderMap =
      new Map();

    const responderIndices =
      state.payload?.responderModelIndices || [];

    const responderValues =
      Array.isArray(frame.responders)
        ? frame.responders
        : [];

    for (
      let i = 0;
      i < responderIndices.length;
      i++
    ) {
      responderMap.set(
        Number(responderIndices[i]),
        Number(responderValues[i] ?? 0)
      );
    }

    return {
      voltage:
        sparseActivityMap(frame.voltage),

      effective:
        sparseActivityMap(frame.effective),

      spikes:
        sparseActivityMap(frame.spikes),

      responders:
        responderMap,
    };
  }

  function drawNodes() {
    const activity =
      currentFrameActivity();

    for (const p of state.projected) {
      const n = p.node;

      let radius = n.topologyFallback
        ? CONFIG.fallbackRadius
        : CONFIG.realRadius;

      let fill = n.topologyFallback
        ? CONFIG.nodeFallback
        : CONFIG.nodeReal;

      let alpha = n.topologyFallback ? 0.38 : 0.72;

      const modelIndex =
        Number(
          n.raw?.i ??
          n.raw?.modelIndex ??
          n.index
        );

      const localIndex =
        Number(n.index);

      const voltage =
        Number(
          activity.voltage.get(localIndex) ?? 0
        );

      const effective =
        Number(
          activity.effective.get(localIndex) ?? 0
        );

      const spike =
        Number(
          activity.spikes.get(localIndex) ?? 0
        );

      const voltageIntensity =
        clamp(
          Math.abs(voltage) / 0.08,
          0,
          1
        );

      if (voltageIntensity > 0.02) {
        alpha = Math.max(
          alpha,
          0.45 + voltageIntensity * 0.5
        );

        radius +=
          voltageIntensity * 1.4;
      }

      if (effective !== 0) {
        fill = "#64e9ff";
        alpha = 0.92;

        radius +=
          Math.min(
            2.5,
            Math.abs(effective) * 4
          );
      }

      if (spike !== 0) {
        fill = "#ffffff";
        alpha = 1;

        radius += 2.4;
      }

      if (n.responder) {
        const responderValue =
          Number(
            activity.responders.get(
              modelIndex
            ) ?? 0
          );

        radius =
          CONFIG.responderRadius +
          Math.min(
            4,
            Math.abs(responderValue) * 24
          );

        fill = CONFIG.responder;

        alpha =
          responderValue !== 0
            ? 1
            : 0.96;
      }

      if (state.hovered === n) {
        radius += 2;
        alpha = 1;
      }

      if (state.selected === n) {
        radius += 3;
        fill = CONFIG.selected;
        alpha = 1;
      }

      radius *= Math.max(
        0.65,
        Math.min(1.8, p.perspectiveScale)
      );

      ctx.beginPath();
      ctx.arc(p.x, p.y, radius, 0, Math.PI * 2);

      ctx.fillStyle = fill;
      ctx.globalAlpha = alpha;
      ctx.fill();

      if (n.responder) {
        ctx.beginPath();
        ctx.arc(
          p.x,
          p.y,
          radius + 3,
          0,
          Math.PI * 2
        );

        ctx.strokeStyle = CONFIG.responder;
        ctx.globalAlpha = 0.25;
        ctx.lineWidth = 1;
        ctx.stroke();
      }
    }

    ctx.globalAlpha = 1;
  }

  function drawCausalEdges() {
    if (!state.edges.length) return;

    const byId = new Map(
      state.projected.map((p) => [p.node.id, p])
    );

    const selectedId =
      state.selected?.id ?? null;

    for (const edge of state.edges) {
      const a = byId.get(edge.source);
      const b = byId.get(edge.target);

      if (!a || !b) continue;

      const selectedEdge =
        selectedId !== null &&
        (
          edge.source === selectedId ||
          edge.target === selectedId
        );

      ctx.strokeStyle = selectedEdge
        ? "#ffb84d"
        : CONFIG.causalEdge;

      ctx.lineWidth = selectedEdge
        ? 3.0
        : 1.4;

      ctx.globalAlpha = selectedEdge
        ? 1.0
        : 0.58;

      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.stroke();
    }

    ctx.globalAlpha = 1;
  }

  function drawOrientation() {
    const x = 54;
    const y = state.height - 52;

    ctx.save();
    ctx.font = "10px monospace";
    ctx.lineWidth = 1.5;

    ctx.strokeStyle = "#ff6868";
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x + 24, y);
    ctx.stroke();

    ctx.fillStyle = "#ff6868";
    ctx.fillText("X", x + 29, y + 3);

    ctx.strokeStyle = "#68ff9a";
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x, y - 24);
    ctx.stroke();

    ctx.fillStyle = "#68ff9a";
    ctx.fillText("Y", x - 3, y - 30);

    ctx.fillStyle = CONFIG.dimText;
    ctx.fillText(
      "drag: rotate · shift-drag: pan · wheel: zoom",
      20,
      state.height - 15
    );

    ctx.restore();
  }

  // ---------------------------------------------------------------------------
  // Interaction
  // ---------------------------------------------------------------------------

  function pointerDown(event) {
    state.dragging = true;

    state.dragMode =
      event.shiftKey ||
      event.button === 1 ||
      event.button === 2
        ? "pan"
        : "rotate";

    state.lastX = event.clientX;
    state.lastY = event.clientY;

    canvas.setPointerCapture?.(event.pointerId);
  }

  function pointerMove(event) {
    const rect = canvas.getBoundingClientRect();

    const mx = event.clientX - rect.left;
    const my = event.clientY - rect.top;

    if (state.dragging) {
      const dx = event.clientX - state.lastX;
      const dy = event.clientY - state.lastY;

      state.lastX = event.clientX;
      state.lastY = event.clientY;

      if (state.dragMode === "pan") {
        state.panX += dx;
        state.panY += dy;
      } else {
        state.yaw += dx * 0.006;
        state.pitch += dy * 0.006;

        state.pitch = clamp(
          state.pitch,
          -Math.PI / 2,
          Math.PI / 2
        );
      }

      requestDraw();
      return;
    }

    const hit = pick(mx, my);

    if (hit !== state.hovered) {
      state.hovered = hit;

      canvas.style.cursor = hit ? "pointer" : "grab";

      requestDraw();
    }
  }

  function pointerUp(event) {
    state.dragging = false;

    canvas.releasePointerCapture?.(event.pointerId);
  }

  function click(event) {
    if (state.dragging) return;

    const rect = canvas.getBoundingClientRect();

    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    state.selected = pick(x, y);

    renderSelection();
    requestDraw();
  }

  function wheel(event) {
    event.preventDefault();

    const factor = Math.exp(-event.deltaY * 0.0012);

    state.zoom = clamp(
      state.zoom * factor,
      CONFIG.minZoom,
      CONFIG.maxZoom
    );

    requestDraw();
  }

  function doubleClick() {
    resetCamera();
  }

  function pick(x, y) {
    let winner = null;
    let best = CONFIG.pointPickRadius ** 2;

    /*
     * Iterate near-to-far so visible foreground neurons win.
     */
    for (let i = state.projected.length - 1; i >= 0; i--) {
      const p = state.projected[i];

      const dx = p.x - x;
      const dy = p.y - y;

      const d2 = dx * dx + dy * dy;

      if (d2 < best) {
        best = d2;
        winner = p.node;
      }
    }

    return winner;
  }

  function resetCamera() {
    state.yaw = CONFIG.initialYaw;
    state.pitch = CONFIG.initialPitch;
    state.zoom = CONFIG.initialZoom;
    state.panX = 0;
    state.panY = 0;

    requestDraw();
  }

  // ---------------------------------------------------------------------------
  // UI
  // ---------------------------------------------------------------------------

  function buildUI() {
    injectStyles();

    root.innerHTML = `
      <div class="ns-shell">

        <header class="ns-header">
          <div>
            <div class="ns-kicker">MOSCAQUANT / MQ-4</div>
            <h1>NEUROSCOPE</h1>
            <div class="ns-subtitle">
              Same neurons. Deeper questions.
            </div>
          </div>

          <div class="ns-runtime">
            <span>RUNTIME</span>
            <strong>${escapeHtml(CONFIG.runtime)}</strong>
          </div>
        </header>

        <div class="ns-main">

          <section class="ns-stage">
            <canvas id="neuroscope-canvas"></canvas>

            <div id="neuroscope-hud" class="ns-hud"></div>

            <div class="ns-legend">
              <span>
                <i class="real"></i>
                somaLocation
              </span>

              <span>
                <i class="fallback"></i>
                topologyFallback
              </span>

              <span>
                <i class="responder"></i>
                causal responder
              </span>

              <span>
                <i class="edge"></i>
                causal path
              </span>
            </div>
          </section>

          <aside class="ns-sidebar">

            <section class="ns-panel">
              <div class="ns-panel-title">
                DISPLAY
              </div>

              <div id="neuroscope-controls"></div>
            </section>

            <section class="ns-panel">
              <div class="ns-panel-title">
                NEURON INSPECTOR
              </div>

              <div id="neuroscope-info" class="ns-info">
                Select a neuron.
              </div>
            </section>

            <section class="ns-panel ns-science">
              <div class="ns-panel-title">
                SCIENTIFIC STATUS
              </div>

              <div>
                Frozen MQ-1 → MQ-3 telemetry
              </div>

              <div>
                Financial semantics:
                <strong>NOT ASSIGNED</strong>
              </div>

              <div>
                Geometry:
                <strong>HYBRID / EXPLICIT</strong>
              </div>
            </section>

          </aside>

        </div>

        <footer class="ns-footer">
          <span id="neuroscope-status">
            Initializing…
          </span>

          <span>
            Anatomy. Evidence. Causality. Next.
          </span>
        </footer>

      </div>
    `;

    canvas = document.getElementById("neuroscope-canvas");
    ctx = canvas.getContext("2d", {
      alpha: false,
      desynchronized: true,
    });

    hud = document.getElementById("neuroscope-hud");
    info = document.getElementById("neuroscope-info");
    status = document.getElementById("neuroscope-status");
    controls = document.getElementById("neuroscope-controls");

    buildControls();

    canvas.addEventListener("pointerdown", pointerDown);
    canvas.addEventListener("pointermove", pointerMove);
    canvas.addEventListener("pointerup", pointerUp);
    canvas.addEventListener("pointercancel", pointerUp);
    canvas.addEventListener("click", click);
    canvas.addEventListener("dblclick", doubleClick);
    canvas.addEventListener("wheel", wheel, {
      passive: false,
    });

    canvas.addEventListener("contextmenu", (e) =>
      e.preventDefault()
    );

    window.addEventListener("resize", resize);
  }

  function buildControls() {
    controls.innerHTML = `
      ${toggle(
        "show-real",
        "Real soma geometry",
        state.showReal
      )}

      ${toggle(
        "show-fallback",
        "Topology fallback",
        state.showFallback
      )}

      ${toggle(
        "show-causal",
        "Causal overlay",
        state.showCausal
      )}

      ${toggle(
        "responders-only",
        "Responders only",
        state.showRespondersOnly
      )}

      <div class="ns-panel-title" style="margin-top:18px">
        ROLES
      </div>

      ${toggle("show-retina", "Retina", state.showRetina)}
      ${toggle("show-relay", "Relay", state.showRelay)}
      ${toggle("show-graded", "Graded", state.showGraded)}
      ${toggle("show-dn", "Descending neurons", state.showDN)}
      ${toggle("show-responders", "Responders", state.showResponders)}

      <div class="ns-panel-title" style="margin-top:18px">
        REPLAY
      </div>

      <div class="ns-replay">
        <div class="ns-replay-row">
          <span>Frame</span>
          <strong id="frame-label">0 / 191</strong>
        </div>

        <input
          id="frame-slider"
          class="ns-frame-slider"
          type="range"
          min="0"
          max="191"
          step="1"
          value="0"
        >

        <div class="ns-replay-buttons">
          <button
            id="frame-prev"
            class="ns-replay-button"
            type="button"
          >
            ◀
          </button>

          <button
            id="frame-play"
            class="ns-replay-button ns-replay-play"
            type="button"
          >
            PLAY
          </button>

          <button
            id="frame-next"
            class="ns-replay-button"
            type="button"
          >
            ▶
          </button>

          <select
            id="replay-speed"
            class="ns-replay-speed"
            aria-label="Replay speed"
          >
            <option value="2">2 fps</option>
            <option value="4">4 fps</option>
            <option value="8" selected>8 fps</option>
            <option value="12">12 fps</option>
            <option value="24">24 fps</option>
          </select>
        </div>

        <div id="frame-summary" class="ns-frame-summary"></div>
      </div>

      <button id="reset-camera" class="ns-button">
        RESET CAMERA
      </button>
    `;

    bindToggle("show-real", (checked) => {
      state.showReal = checked;
    });

    bindToggle("show-fallback", (checked) => {
      state.showFallback = checked;
    });

    bindToggle("show-causal", (checked) => {
      state.showCausal = checked;
    });

    bindToggle("responders-only", (checked) => {
      state.showRespondersOnly = checked;
    });

    bindToggle("show-retina", (checked) => {
      state.showRetina = checked;
    });

    bindToggle("show-relay", (checked) => {
      state.showRelay = checked;
    });

    bindToggle("show-graded", (checked) => {
      state.showGraded = checked;
    });

    bindToggle("show-dn", (checked) => {
      state.showDN = checked;
    });

    bindToggle("show-responders", (checked) => {
      state.showResponders = checked;
    });

    const frameSlider =
      document.getElementById("frame-slider");

    const framePrev =
      document.getElementById("frame-prev");

    const framePlay =
      document.getElementById("frame-play");

    const frameNext =
      document.getElementById("frame-next");

    const replaySpeed =
      document.getElementById("replay-speed");

    frameSlider.max = String(
      Math.max(
        0,
        Number(state.payload?.frameCount ?? 192) - 1
      )
    );

    frameSlider.addEventListener("input", (event) => {
      stopReplay();

      setReplayFrame(
        Number(event.target.value)
      );
    });

    framePrev.addEventListener("click", () => {
      stopReplay();

      setReplayFrame(
        state.currentFrame - 1
      );
    });

    frameNext.addEventListener("click", () => {
      stopReplay();

      setReplayFrame(
        state.currentFrame + 1
      );
    });

    framePlay.addEventListener("click", () => {
      if (state.replayPlaying) {
        stopReplay();
      } else {
        startReplay();
      }
    });

    replaySpeed.addEventListener("change", (event) => {
      state.replayFps =
        Number(event.target.value) || 8;

      if (state.replayPlaying) {
        stopReplay();
        startReplay();
      }
    });

    document
      .getElementById("reset-camera")
      .addEventListener("click", resetCamera);
  }

  function bindToggle(id, setter) {
    document
      .getElementById(id)
      .addEventListener("change", (event) => {
        setter(event.target.checked);
        requestDraw();
      });
  }

  function toggle(id, label, checked) {
    return `
      <label class="ns-toggle">
        <input
          type="checkbox"
          id="${id}"
          ${checked ? "checked" : ""}
        >
        <span>${label}</span>
      </label>
    `;
  }

  function updateFrameSummary() {
    if (!state.payload?.frames?.length) return;

    const frame =
      state.payload.frames[state.currentFrame];

    if (!frame) return;

    const frameLabel =
      document.getElementById("frame-label");

    const summary =
      document.getElementById("frame-summary");

    if (frameLabel) {
      frameLabel.textContent =
        `${state.currentFrame} / ${
          state.payload.frames.length - 1
        }`;
    }

    if (!summary) return;

    const dnMean =
      Array.isArray(frame.dnMean)
        ? frame.dnMean
        : [];

    const dnMax =
      Array.isArray(frame.dnMax)
        ? frame.dnMax
        : [];

    const dnSpikes =
      Array.isArray(frame.dnSpikes)
        ? frame.dnSpikes
        : [];

    const responders =
      Array.isArray(frame.responders)
        ? frame.responders
        : [];

    const maxResponder =
      responders.length
        ? Math.max(...responders.map(Number))
        : 0;

    summary.innerHTML = `
      <dl class="ns-frame-dl">

        <dt>Retinal spikes</dt>
        <dd>${escapeHtml(
          String(frame.retinalSpikes ?? 0)
        )}</dd>

        <dt>Relay spikes</dt>
        <dd>${escapeHtml(
          String(frame.relaySpikes ?? 0)
        )}</dd>

        <dt>Graded active</dt>
        <dd>${escapeHtml(
          String(frame.gradedActive ?? 0)
        )}</dd>

        <dt>DN mean</dt>
        <dd>${escapeHtml(
          dnMean
            .map((v) => Number(v).toExponential(2))
            .join(" · ") || "—"
        )}</dd>

        <dt>DN max</dt>
        <dd>${escapeHtml(
          dnMax
            .map((v) => Number(v).toExponential(2))
            .join(" · ") || "—"
        )}</dd>

        <dt>DN spikes</dt>
        <dd>${escapeHtml(
          dnSpikes.join(" · ") || "—"
        )}</dd>

        <dt>Max responder</dt>
        <dd>${escapeHtml(
          Number(maxResponder).toExponential(3)
        )}</dd>

      </dl>
    `;
  }

  function updateHud() {
    if (!hud || !state.nodes.length) return;

    const responders = state.nodes.filter(
      (n) => n.responder
    ).length;

    hud.innerHTML = `
      <div>
        <span>NEURONS</span>
        <strong>${state.nodes.length.toLocaleString()}</strong>
      </div>

      <div>
        <span>REAL SOMA</span>
        <strong>${countReal().toLocaleString()}</strong>
      </div>

      <div>
        <span>FALLBACK</span>
        <strong>${countFallback().toLocaleString()}</strong>
      </div>

      <div>
        <span>CAUSAL EDGES</span>
        <strong>${state.edges.length.toLocaleString()}</strong>
      </div>

      <div>
        <span>RESPONDERS</span>
        <strong>${responders}</strong>
      </div>
    `;
  }

  function renderSelection() {
    const n = state.selected;

    if (!n) {
      info.innerHTML = "Select a neuron.";
      return;
    }

    const raw = n.raw || {};

    const modelIndex =
      raw.i ??
      raw.modelIndex ??
      raw.model_index ??
      "—";

    const bodyId =
      raw.body ??
      raw.bodyId ??
      raw.body_id ??
      n.id ??
      "—";

    const rolesValue = Number(raw.roles ?? 0);

    const roleBits =
      state.payload?.roleBits || {
        retina: 1,
        relay: 2,
        graded: 4,
        dn: 8,
        responder: 16,
      };

    const roles = Object.entries(roleBits)
      .filter(([, bit]) => (rolesValue & Number(bit)) !== 0)
      .map(([name]) => name.toUpperCase());

    const geometryLabel =
      raw.positionSource ||
      (n.topologyFallback
        ? "topologyFallback"
        : "somaLocation");

    const gradedType =
      raw.gradedType ??
      "—";

    const dnCluster =
      raw.dnCluster ??
      "—";

    const somaSide =
      raw.somaSide ??
      n.side ??
      "—";

    const somaNeuromere =
      raw.somaNeuromere ??
      "—";

    const causalNode =
      raw.causalNode === true;

    const causalEdges = state.edges.filter(
      (edge) =>
        edge.source === n.id ||
        edge.target === n.id
    );

    const causalEdgeHtml = causalEdges.length
      ? causalEdges.map((edge) => {
          const outgoing = edge.source === n.id;

          const peerModelIndex =
            outgoing
              ? edge.raw?.postModel
              : edge.raw?.preModel;

          const frames =
            edge.raw?.frames ??
            edge.raw?.observed_frames ??
            [];

          const weight =
            Number(edge.weight);

          const weightLabel =
            Number.isFinite(weight)
              ? weight.toExponential(4)
              : "—";

          return `
            <div class="ns-causal-edge">
              <div>
                <strong>${outgoing ? "OUT" : "IN"}</strong>
                · model ${escapeHtml(
                  String(peerModelIndex ?? "—")
                )}
              </div>

              <div>
                weight ${escapeHtml(weightLabel)}
              </div>

              <div>
                frame${
                  frames.length === 1 ? "" : "s"
                } ${
                  frames.length
                    ? escapeHtml(frames.join(", "))
                    : "—"
                }
              </div>
            </div>
          `;
        }).join("")
      : "";

    info.innerHTML = `
      <dl class="ns-dl">

        <dt>Model index</dt>
        <dd>${escapeHtml(String(modelIndex))}</dd>

        <dt>Body ID</dt>
        <dd>${escapeHtml(String(bodyId))}</dd>

        <dt>Roles</dt>
        <dd>${escapeHtml(
          roles.length ? roles.join(" · ") : "—"
        )}</dd>

        <dt>Graded type</dt>
        <dd>${escapeHtml(String(gradedType))}</dd>

        <dt>DN cluster</dt>
        <dd>${escapeHtml(String(dnCluster))}</dd>

        <dt>Soma side</dt>
        <dd>${escapeHtml(String(somaSide))}</dd>

        <dt>Neuromere</dt>
        <dd>${escapeHtml(String(somaNeuromere))}</dd>

        <dt>Geometry</dt>
        <dd class="${
          n.topologyFallback ? "warn" : "good"
        }">
          ${escapeHtml(String(geometryLabel))}
        </dd>

        <dt>Causal node</dt>
        <dd class="${causalNode ? "good" : ""}">
          ${causalNode ? "YES" : "NO"}
        </dd>

        <dt>Responder</dt>
        <dd class="${n.responder ? "good" : ""}">
          ${n.responder ? "YES" : "NO"}
        </dd>

        <dt>Causal edges</dt>
        <dd>${causalEdges.length}</dd>

      </dl>

      ${
        causalEdges.length
          ? `
            <div class="ns-causal-block">
              <div class="ns-causal-title">
                CAUSAL CONNECTIONS
              </div>
              ${causalEdgeHtml}
            </div>
          `
          : ""
      }

      ${
        n.topologyFallback
          ? `
            <div class="ns-warning">
              Viewer topology only. This position is
              <strong>not</strong> an anatomical coordinate.
            </div>
          `
          : `
            <div class="ns-valid">
              Position originates from MaleCNS
              <code>somaLocation</code>.
            </div>
          `
      }
    `;
  }
  // ---------------------------------------------------------------------------
  // Resize / redraw
  // ---------------------------------------------------------------------------

  function resize() {
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();

    state.width = Math.max(1, rect.width);
    state.height = Math.max(1, rect.height);

    canvas.width =
      Math.round(state.width * state.dpr);

    canvas.height =
      Math.round(state.height * state.dpr);

    ctx.setTransform(
      state.dpr,
      0,
      0,
      state.dpr,
      0,
      0
    );

    requestDraw();
  }

  function requestDraw() {
    if (state.animationFrame != null) return;

    state.animationFrame =
      requestAnimationFrame(draw);
  }

  // ---------------------------------------------------------------------------
  // Metrics
  // ---------------------------------------------------------------------------

  function countReal() {
    return state.nodes.reduce(
      (sum, node) =>
        sum + (node.topologyFallback ? 0 : 1),
      0
    );
  }

  function countFallback() {
    return state.nodes.reduce(
      (sum, node) =>
        sum + (node.topologyFallback ? 1 : 0),
      0
    );
  }

  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------

  function vector3(value) {
    if (!value) return null;

    if (
      Array.isArray(value) &&
      value.length >= 3
    ) {
      const result = [
        Number(value[0]),
        Number(value[1]),
        Number(value[2]),
      ];

      return result.every(Number.isFinite)
        ? result
        : null;
    }

    if (
      typeof value === "object" &&
      value !== null
    ) {
      const result = [
        Number(value.x ?? value[0]),
        Number(value.y ?? value[1]),
        Number(value.z ?? value[2]),
      ];

      return result.every(Number.isFinite)
        ? result
        : null;
    }

    return null;
  }

  function numberOrNull(value) {
    if (value == null) return null;

    const n = Number(value);

    return Number.isFinite(n) ? n : null;
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function setStatus(message, error = false) {
    if (!status) return;

    status.textContent = message;
    status.classList.toggle("error", error);
  }

  // ---------------------------------------------------------------------------
  // CSS
  // ---------------------------------------------------------------------------

  function injectStyles() {
    const style = document.createElement("style");

    style.textContent = `
      :root {
        color-scheme: dark;
      }

      * {
        box-sizing: border-box;
      }

      html,
      body {
        margin: 0;
        width: 100%;
        height: 100%;
        background: #06080c;
        color: #c8d1dc;
        font-family:
          Inter,
          ui-sans-serif,
          system-ui,
          -apple-system,
          BlinkMacSystemFont,
          "Segoe UI",
          sans-serif;
      }

      #neuroscope-root,
      #app {
        width: 100%;
        height: 100%;
      }

      .ns-shell {
        height: 100vh;
        min-height: 600px;
        display: flex;
        flex-direction: column;
        background: #06080c;
      }

      .ns-header {
        min-height: 92px;
        padding: 18px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
        border-bottom: 1px solid #1b2430;
        background: #090c12;
      }

      .ns-kicker,
      .ns-panel-title {
        color: #8b5cf6;
        font-family: monospace;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .15em;
      }

      .ns-header h1 {
        margin: 2px 0 0;
        font-size: 30px;
        line-height: 1;
        letter-spacing: .08em;
      }

      .ns-subtitle {
        margin-top: 5px;
        color: #75808e;
        font-size: 12px;
      }

      .ns-runtime {
        text-align: right;
        font-family: monospace;
      }

      .ns-runtime span {
        display: block;
        color: #626d7b;
        font-size: 9px;
        letter-spacing: .14em;
      }

      .ns-runtime strong {
        color: #9c7cff;
        font-size: 12px;
      }

      .ns-main {
        flex: 1;
        min-height: 0;
        display: grid;
        grid-template-columns:
          minmax(0, 1fr)
          285px;
      }

      .ns-stage {
        position: relative;
        min-width: 0;
        min-height: 0;
        overflow: hidden;
      }

      #neuroscope-canvas {
        display: block;
        width: 100%;
        height: 100%;
        cursor: grab;
        touch-action: none;
      }

      #neuroscope-canvas:active {
        cursor: grabbing;
      }

      .ns-sidebar {
        overflow-y: auto;
        border-left: 1px solid #1b2430;
        background: #090c12;
      }

      .ns-panel {
        padding: 18px;
        border-bottom: 1px solid #1b2430;
      }

      .ns-panel-title {
        margin-bottom: 14px;
      }

      .ns-toggle {
        display: flex;
        gap: 9px;
        align-items: center;
        margin: 10px 0;
        font-size: 12px;
        cursor: pointer;
      }

      .ns-toggle input {
        accent-color: #8b5cf6;
      }

      .ns-replay {
        margin: 8px 0 14px;
      }

      .ns-replay-buttons {
        display: grid;
        grid-template-columns:
          34px
          1fr
          34px
          70px;
        gap: 5px;
        margin-top: 8px;
      }

      .ns-replay-button,
      .ns-replay-speed {
        min-height: 28px;
        border: 1px solid #303b4a;
        background: #111722;
        color: #aeb9c6;
        font-family: monospace;
        font-size: 9px;
      }

      .ns-replay-button {
        cursor: pointer;
      }

      .ns-replay-button:hover {
        border-color: #8b5cf6;
      }

      .ns-replay-play.active {
        border-color: #8b5cf6;
        color: #cbbaff;
        background: #181226;
      }

      .ns-replay-speed {
        padding: 0 4px;
      }

      .ns-replay-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
        color: #778291;
        font-family: monospace;
        font-size: 10px;
      }

      .ns-replay-row strong {
        color: #b69cff;
      }

      .ns-frame-slider {
        width: 100%;
        accent-color: #8b5cf6;
      }

      .ns-frame-summary {
        margin-top: 10px;
      }

      .ns-frame-dl {
        display: grid;
        grid-template-columns: 105px 1fr;
        gap: 5px 8px;
        margin: 0;
        font-family: monospace;
        font-size: 9px;
      }

      .ns-frame-dl dt {
        color: #626d7b;
      }

      .ns-frame-dl dd {
        margin: 0;
        color: #b5bfcc;
        overflow-wrap: anywhere;
      }

      .ns-button {
        width: 100%;
        margin-top: 12px;
        padding: 9px 12px;
        border: 1px solid #303b4a;
        background: #111722;
        color: #c8d1dc;
        font-family: monospace;
        font-size: 10px;
        letter-spacing: .08em;
        cursor: pointer;
      }

      .ns-button:hover {
        border-color: #8b5cf6;
      }

      .ns-info {
        color: #8893a2;
        font-size: 12px;
      }

      .ns-dl {
        display: grid;
        grid-template-columns: 92px 1fr;
        gap: 7px 10px;
        margin: 0;
        font-family: monospace;
        font-size: 11px;
      }

      .ns-dl dt {
        color: #657080;
      }

      .ns-dl dd {
        margin: 0;
        overflow-wrap: anywhere;
        color: #d4dae2;
      }

      .ns-dl .good {
        color: #73e6a2;
      }

      .ns-dl .warn {
        color: #f5bb65;
      }

      .ns-causal-block {
        margin-top: 15px;
        padding-top: 12px;
        border-top: 1px solid #27303d;
      }

      .ns-causal-title {
        margin-bottom: 8px;
        color: #ff9a55;
        font-family: monospace;
        font-size: 9px;
        font-weight: 700;
        letter-spacing: .12em;
      }

      .ns-causal-edge {
        margin: 6px 0;
        padding: 7px 8px;
        border-left: 2px solid #ff7a45;
        background: #111016;
        color: #8994a3;
        font-family: monospace;
        font-size: 9px;
        line-height: 1.45;
      }

      .ns-causal-edge strong {
        color: #ffb84d;
      }

      .ns-warning,
      .ns-valid {
        margin-top: 15px;
        padding: 10px;
        line-height: 1.5;
        border: 1px solid #49371f;
        background: #17130d;
        color: #cda668;
        font-size: 10px;
      }

      .ns-valid {
        border-color: #204233;
        background: #0d1713;
        color: #79cfa1;
      }

      .ns-science {
        color: #778291;
        font-size: 10px;
        line-height: 1.8;
        font-family: monospace;
      }

      .ns-science strong {
        color: #aab4c2;
      }

      .ns-hud {
        position: absolute;
        top: 18px;
        left: 18px;
        display: flex;
        gap: 7px;
        pointer-events: none;
      }

      .ns-hud > div {
        min-width: 74px;
        padding: 7px 9px;
        border: 1px solid rgba(83, 97, 116, .36);
        background: rgba(8, 12, 18, .78);
        backdrop-filter: blur(5px);
      }

      .ns-hud span {
        display: block;
        color: #606b79;
        font-family: monospace;
        font-size: 8px;
        letter-spacing: .08em;
      }

      .ns-hud strong {
        display: block;
        margin-top: 2px;
        color: #d6dde6;
        font-family: monospace;
        font-size: 12px;
      }

      .ns-legend {
        position: absolute;
        top: 18px;
        right: 18px;
        display: flex;
        flex-direction: column;
        gap: 6px;
        padding: 8px 10px;
        border: 1px solid rgba(83, 97, 116, .3);
        background: rgba(8, 12, 18, .76);
        color: #75808e;
        font-family: monospace;
        font-size: 9px;
        pointer-events: none;
      }

      .ns-legend span {
        display: flex;
        align-items: center;
        gap: 7px;
      }

      .ns-legend i {
        width: 7px;
        height: 7px;
        display: inline-block;
        border-radius: 50%;
      }

      .ns-legend .real {
        background: #78a8ff;
      }

      .ns-legend .fallback {
        background: #69707d;
      }

      .ns-legend .responder {
        background: #ffb84d;
      }

      .ns-legend .edge {
        width: 14px;
        height: 2px;
        border-radius: 0;
        background: #ff7a45;
      }

      .ns-footer {
        min-height: 34px;
        padding: 8px 18px;
        display: flex;
        justify-content: space-between;
        gap: 20px;
        border-top: 1px solid #1b2430;
        background: #090c12;
        color: #626d7b;
        font-family: monospace;
        font-size: 9px;
      }

      .ns-footer .error {
        color: #ff6d76;
      }

      .ns-error-title {
        margin-bottom: 9px;
        color: #ff6d76;
        font-weight: 700;
      }

      .ns-error-body {
        margin: 5px 0;
        line-height: 1.5;
      }

      code {
        color: #b69cff;
      }

      @media (max-width: 900px) {
        .ns-main {
          grid-template-columns: 1fr;
          grid-template-rows:
            minmax(420px, 1fr)
            auto;
        }

        .ns-sidebar {
          border-left: 0;
          border-top: 1px solid #1b2430;
        }

        .ns-hud {
          flex-wrap: wrap;
          right: 18px;
        }

        .ns-legend {
          top: auto;
          right: 12px;
          bottom: 34px;
        }
      }
    `;

    document.head.appendChild(style);
  }

  document.addEventListener("DOMContentLoaded", init);
})();
