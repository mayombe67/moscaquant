"use strict";

const DATA =
  "data/replay-A-v1.json";

const ROLE = {
  RETINA: 1,
  RELAY: 2,
  GRADED: 4,
  DN: 8,
  RESPONDER: 16,
};

const RESPONDER_NAMES = [
  "DNp11_R",
  "DNc02_L",
  "DNc02_R",
  "DNp27_L",
  "DNc01_R",
  "DNp30_R",
  "DNp30_L",
  "DNp27_R",
  "DNc01_L",
];

const canvas =
  document.getElementById("scope");

const ctx =
  canvas.getContext(
    "2d",
    {
      alpha: false,
    }
  );

const timeline =
  document.getElementById("timeline");

const playButton =
  document.getElementById("play");

const frameLabel =
  document.getElementById("frameLabel");

const retinalSpikes =
  document.getElementById(
    "retinalSpikes"
  );

const relaySpikes =
  document.getElementById(
    "relaySpikes"
  );

const gradedActive =
  document.getElementById(
    "gradedActive"
  );

const channelsEl =
  document.getElementById(
    "dnChannels"
  );

const respondersEl =
  document.getElementById(
    "responders"
  );

const selectionEl =
  document.getElementById(
    "selection"
  );

const causalToggle =
  document.getElementById(
    "causalToggle"
  );

let replay = null;

let frame = 145;

let playing = false;

let timer = null;

let selectedLocal = null;

let positions = [];

let activeMap = new Map();

let voltageMap = new Map();

let spikeSet = new Set();


function hash32(value) {
  let x =
    Math.imul(
      value ^ 0x9e3779b9,
      0x85ebca6b
    );

  x ^= x >>> 13;

  x =
    Math.imul(
      x,
      0xc2b2ae35
    );

  return (
    (x ^ (x >>> 16))
    >>> 0
  );
}


function deterministicNoise(
  value,
  salt
) {
  return (
    hash32(
      value ^ salt
    )
    / 0xffffffff
  );
}


function resizeCanvas() {
  const dpr =
    window.devicePixelRatio || 1;

  const rect =
    canvas.getBoundingClientRect();

  canvas.width =
    Math.max(
      1,
      Math.floor(
        rect.width * dpr
      )
    );

  canvas.height =
    Math.max(
      1,
      Math.floor(
        rect.height * dpr
      )
    );

  ctx.setTransform(
    dpr,
    0,
    0,
    dpr,
    0,
    0
  );

  buildPositions();

  render();
}


function stageFor(node) {
  const roles =
    node.roles;

  if (
    roles
    & ROLE.RETINA
  ) {
    return 0;
  }

  if (
    roles
    & ROLE.RELAY
  ) {
    return 1;
  }

  if (
    roles
    & ROLE.GRADED
  ) {
    return 2;
  }

  return 3;
}


function buildPositions() {
  if (!replay) {
    return;
  }

  const rect =
    canvas.getBoundingClientRect();

  const width =
    rect.width;

  const height =
    rect.height;

  const top =
    80;

  const bottom =
    height - 70;

  const stageCenters = [
    width * 0.10,
    width * 0.36,
    width * 0.64,
    width * 0.89,
  ];

  const spreads = [
    width * 0.08,
    width * 0.10,
    width * 0.10,
    width * 0.07,
  ];

  positions =
    replay.nodes.map(
      (node) => {

        const stage =
          stageFor(node);

        const nx =
          deterministicNoise(
            node.i,
            0x1234
          );

        const ny =
          deterministicNoise(
            node.i,
            0x55aa
          );

        let x =
          stageCenters[stage]
          + (
            nx - 0.5
          )
          * spreads[stage];

        let y =
          top
          + ny
          * Math.max(
            1,
            bottom - top
          );

        //
        // Give responders a slightly
        // cleaner vertical spread.
        //
        if (
          node.roles
          & ROLE.RESPONDER
        ) {

          const responderIndex =
            replay
              .responderModelIndices
              .indexOf(
                node.i
              );

          if (
            responderIndex >= 0
          ) {
            y =
              top
              + 40
              + responderIndex
              * Math.max(
                25,
                (
                  bottom
                  - top
                  - 80
                )
                / 8
              );

            x =
              stageCenters[3];
          }
        }

        return {
          x,
          y,
        };
      }
    );
}


function baseColor(node) {
  if (
    node.roles
    & ROLE.RESPONDER
  ) {
    return "#ff3e72";
  }

  if (
    node.roles
    & ROLE.RETINA
  ) {
    return "#3ba7ff";
  }

  if (
    node.roles
    & ROLE.RELAY
  ) {
    return "#46e0da";
  }

  if (
    node.roles
    & ROLE.GRADED
  ) {
    return "#bd6cff";
  }

  if (
    node.roles
    & ROLE.DN
  ) {
    return "#ffad42";
  }

  return "#596574";
}


function rebuildFrameMaps() {
  const state =
    replay.frames[
      frame
    ];

  activeMap =
    new Map(
      state.effective
    );

  voltageMap =
    new Map(
      state.voltage
    );

  spikeSet =
    new Set(
      state.spikes.map(
        ([index]) => index
      )
    );
}


function drawBackground(
  width,
  height
) {
  ctx.fillStyle =
    "#05080c";

  ctx.fillRect(
    0,
    0,
    width,
    height
  );

  ctx.strokeStyle =
    "#101923";

  ctx.lineWidth =
    1;

  const boundaries = [
    width * 0.23,
    width * 0.50,
    width * 0.77,
  ];

  ctx.setLineDash(
    [3, 8]
  );

  for (
    const x
    of boundaries
  ) {
    ctx.beginPath();

    ctx.moveTo(
      x,
      60
    );

    ctx.lineTo(
      x,
      height - 55
    );

    ctx.stroke();
  }

  ctx.setLineDash([]);
}



function drawCausalEdges() {
  if (
    !causalToggle.checked
    || !replay.causalEdges
  ) {
    return;
  }

  const AFTERGLOW_FRAMES = 6;

  for (
    const edge
    of replay.causalEdges
  ) {

    const pre =
      positions[
        edge.pre
      ];

    const post =
      positions[
        edge.post
      ];

    if (!pre || !post) {
      continue;
    }

    const onsetFrame =
      Math.min(
        ...edge.frames
      );

    const activeNow =
      edge.frames.includes(
        frame
      );

    const age =
      frame - onsetFrame;

    const recent =
      (
        age > 0
        && age <= AFTERGLOW_FRAMES
      );

    //
    // Future routes are invisible.
    //
    if (
      !activeNow
      && !recent
    ) {
      continue;
    }

    const dx =
      post.x - pre.x;

    const dy =
      post.y - pre.y;

    const length =
      Math.max(
        1,
        Math.sqrt(
          dx * dx
          + dy * dy
        )
      );

    const ux =
      dx / length;

    const uy =
      dy / length;

    const startX =
      pre.x + ux * 5;

    const startY =
      pre.y + uy * 5;

    const endX =
      post.x - ux * 7;

    const endY =
      post.y - uy * 7;

    ctx.save();

    //
    // ACTIVE ONSET:
    // huge outer glow.
    //
    if (activeNow) {

      ctx.beginPath();

      ctx.moveTo(
        startX,
        startY
      );

      ctx.lineTo(
        endX,
        endY
      );

      ctx.strokeStyle =
        "#ffb000";

      ctx.globalAlpha =
        0.26;

      ctx.lineWidth =
        11;

      ctx.shadowColor =
        "#ffb000";

      ctx.shadowBlur =
        24;

      ctx.stroke();

      //
      // Bright gold body.
      //
      ctx.beginPath();

      ctx.moveTo(
        startX,
        startY
      );

      ctx.lineTo(
        endX,
        endY
      );

      ctx.strokeStyle =
        "#ffd166";

      ctx.globalAlpha =
        1;

      ctx.lineWidth =
        5;

      ctx.shadowColor =
        "#ffd166";

      ctx.shadowBlur =
        14;

      ctx.stroke();

      //
      // White-hot center.
      //
      ctx.beginPath();

      ctx.moveTo(
        startX,
        startY
      );

      ctx.lineTo(
        endX,
        endY
      );

      ctx.strokeStyle =
        "#fff4c2";

      ctx.globalAlpha =
        0.95;

      ctx.lineWidth =
        1.5;

      ctx.shadowBlur =
        0;

      ctx.stroke();

      //
      // Moving signal pulse.
      //
      const phase =
        (
          (
            performance.now()
            / 650
          )
          % 1
        );

      const pulseX =
        startX
        + (
          endX - startX
        )
        * phase;

      const pulseY =
        startY
        + (
          endY - startY
        )
        * phase;

      ctx.beginPath();

      ctx.arc(
        pulseX,
        pulseY,
        5.5,
        0,
        Math.PI * 2
      );

      ctx.fillStyle =
        "#ffffff";

      ctx.shadowColor =
        "#ffd166";

      ctx.shadowBlur =
        18;

      ctx.fill();

    } else {

      //
      // Recently fired route.
      //
      const fade =
        1
        - (
          age
          / (
            AFTERGLOW_FRAMES
            + 1
          )
        );

      ctx.beginPath();

      ctx.moveTo(
        startX,
        startY
      );

      ctx.lineTo(
        endX,
        endY
      );

      ctx.strokeStyle =
        "#c77d22";

      ctx.globalAlpha =
        0.18
        + fade * 0.42;

      ctx.lineWidth =
        1.5
        + fade * 1.5;

      ctx.shadowColor =
        "#c77d22";

      ctx.shadowBlur =
        4
        + fade * 6;

      ctx.stroke();
    }

    //
    // Arrowhead.
    //
    const angle =
      Math.atan2(
        endY - startY,
        endX - startX
      );

    const arrowSize =
      activeNow
        ? 10
        : 7;

    ctx.beginPath();

    ctx.moveTo(
      endX,
      endY
    );

    ctx.lineTo(
      endX
        - Math.cos(
            angle - 0.52
          )
          * arrowSize,
      endY
        - Math.sin(
            angle - 0.52
          )
          * arrowSize
    );

    ctx.lineTo(
      endX
        - Math.cos(
            angle + 0.52
          )
          * arrowSize,
      endY
        - Math.sin(
            angle + 0.52
          )
          * arrowSize
    );

    ctx.closePath();

    ctx.fillStyle =
      activeNow
        ? "#fff4c2"
        : "#c77d22";

    ctx.globalAlpha =
      activeNow
        ? 1
        : 0.55;

    ctx.shadowColor =
      activeNow
        ? "#ffd166"
        : "#c77d22";

    ctx.shadowBlur =
      activeNow
        ? 12
        : 4;

    ctx.fill();

    //
    // Active route identifier.
    //
    if (activeNow) {

      const midX =
        (
          startX + endX
        )
        / 2;

      const midY =
        (
          startY + endY
        )
        / 2;

      const label =
        `${edge.preModel} → ${edge.postModel}`;

      ctx.shadowBlur =
        0;

      ctx.font =
        "bold 9px monospace";

      const metrics =
        ctx.measureText(
          label
        );

      const padding =
        5;

      const boxWidth =
        metrics.width
        + padding * 2;

      const boxHeight =
        17;

      ctx.globalAlpha =
        0.92;

      ctx.fillStyle =
        "#171006";

      ctx.fillRect(
        midX
          - boxWidth / 2,
        midY
          - boxHeight / 2,
        boxWidth,
        boxHeight
      );

      ctx.strokeStyle =
        "#ffd166";

      ctx.lineWidth =
        1;

      ctx.strokeRect(
        midX
          - boxWidth / 2,
        midY
          - boxHeight / 2,
        boxWidth,
        boxHeight
      );

      ctx.globalAlpha =
        1;

      ctx.fillStyle =
        "#ffe4a0";

      ctx.textAlign =
        "center";

      ctx.textBaseline =
        "middle";

      ctx.fillText(
        label,
        midX,
        midY
      );

      ctx.textAlign =
        "start";
    }

    ctx.restore();
  }
}


function drawNode(
  node,
  localIndex
) {
  const position =
    positions[
      localIndex
    ];

  if (!position) {
    return;
  }

  const effective =
    activeMap.get(
      localIndex
    ) || 0;

  const voltage =
    voltageMap.get(
      localIndex
    ) || 0;

  const spiking =
    spikeSet.has(
      localIndex
    );

  const responder =
    Boolean(
      node.roles
      & ROLE.RESPONDER
    );

  const selected =
    localIndex
    === selectedLocal;

  let radius =
    responder
      ? 3.5
      : 1.15;

  if (effective > 0) {
    radius +=
      Math.min(
        4,
        effective * 6
      );
  }

  if (voltage > 0) {
    radius +=
      Math.min(
        2.5,
        Math.sqrt(
          voltage
        )
        * 12
      );
  }

  if (spiking) {
    radius += 2.2;
  }

  const color =
    baseColor(node);

  //
  // Glow active nodes only.
  //
  if (
    effective > 0
    || voltage > 0
    || spiking
    || responder
  ) {

    ctx.shadowColor =
      spiking
        ? "#ffffff"
        : color;

    ctx.shadowBlur =
      responder
        ? 11
        : (
          spiking
            ? 12
            : 5
        );
  } else {
    ctx.shadowBlur = 0;
  }

  ctx.globalAlpha =
    (
      effective > 0
      || voltage > 0
      || spiking
      || responder
    )
      ? 0.95
      : 0.16;

  ctx.fillStyle =
    spiking
      ? "#ffffff"
      : color;

  ctx.beginPath();

  ctx.arc(
    position.x,
    position.y,
    radius,
    0,
    Math.PI * 2
  );

  ctx.fill();

  if (selected) {
    ctx.shadowBlur = 0;
    ctx.globalAlpha = 1;

    ctx.strokeStyle =
      "#ffffff";

    ctx.lineWidth = 1.5;

    ctx.beginPath();

    ctx.arc(
      position.x,
      position.y,
      radius + 6,
      0,
      Math.PI * 2
    );

    ctx.stroke();
  }

  ctx.shadowBlur = 0;
  ctx.globalAlpha = 1;
}


function drawResponderLabels() {
  ctx.font =
    "10px monospace";

  ctx.textBaseline =
    "middle";

  replay
    .responderModelIndices
    .forEach(
      (
        modelIndex,
        responderIndex
      ) => {

        const local =
          replay.nodes.findIndex(
            (node) =>
              node.i === modelIndex
          );

        if (local < 0) {
          return;
        }

        const p =
          positions[
            local
          ];

        const voltage =
          voltageMap.get(
            local
          ) || 0;

        ctx.fillStyle =
          voltage > 0
            ? "#ff8dab"
            : "#77505d";

        ctx.fillText(
          RESPONDER_NAMES[
            responderIndex
          ],
          p.x + 10,
          p.y
        );
      }
    );
}


function render() {
  if (!replay) {
    return;
  }

  rebuildFrameMaps();

  const rect =
    canvas.getBoundingClientRect();

  drawBackground(
    rect.width,
    rect.height
  );

  //
  // Draw quiet neurons first.
  //
  for (
    let i = 0;
    i < replay.nodes.length;
    i += 1
  ) {
    const active =
      activeMap.has(i)
      || voltageMap.has(i)
      || spikeSet.has(i)
      || (
        replay.nodes[i].roles
        & ROLE.RESPONDER
      );

    if (!active) {
      drawNode(
        replay.nodes[i],
        i
      );
    }
  }

  //
  // Active neurons on top.
  //
  for (
    let i = 0;
    i < replay.nodes.length;
    i += 1
  ) {
    const active =
      activeMap.has(i)
      || voltageMap.has(i)
      || spikeSet.has(i)
      || (
        replay.nodes[i].roles
        & ROLE.RESPONDER
      );

    if (active) {
      drawNode(
        replay.nodes[i],
        i
      );
    }
  }

  //
  // Evidence overlay sits above the neural field.
  //
  drawCausalEdges();

  drawResponderLabels();

  updateUI();
}


function updateUI() {
  const state =
    replay.frames[
      frame
    ];

  frameLabel.textContent =
    `FRAME ${frame} / ${replay.frameCount - 1}`;

  timeline.value =
    String(frame);

  retinalSpikes.textContent =
    state.retinalSpikes;

  relaySpikes.textContent =
    state.relaySpikes;

  gradedActive.textContent =
    state.gradedActive;

  renderChannels(
    state
  );

  renderResponders(
    state
  );

  renderSelection();
}


function renderChannels(
  state
) {
  const labels = [
    "DN-C0",
    "DN-C1",
    "DN-C2",
  ];

  const maxValue =
    Math.max(
      ...state.dnMax,
      1e-12
    );

  channelsEl.innerHTML =
    labels.map(
      (
        label,
        index
      ) => {

        const value =
          state.dnMean[
            index
          ];

        const max =
          state.dnMax[
            index
          ];

        const width =
          Math.min(
            100,
            (
              max
              / maxValue
            )
            * 100
          );

        return `
          <div class="channel">
            <div class="channel-head">
              <span>${label}</span>
              <span class="channel-value">
                ${value.toExponential(3)}
              </span>
            </div>

            <div class="bar">
              <div
                style="width:${width}%"
              ></div>
            </div>
          </div>
        `;
      }
    )
    .join("");
}


function renderResponders(
  state
) {
  const max =
    Math.max(
      ...state.responders.map(
        (x) =>
          Math.max(
            0,
            x
          )
      ),
      1e-12
    );

  respondersEl.innerHTML =
    state.responders.map(
      (
        value,
        index
      ) => {

        const positive =
          Math.max(
            0,
            value
          );

        const width =
          (
            positive
            / max
          )
          * 100;

        return `
          <div class="responder-row">
            <span class="responder-name">
              ${RESPONDER_NAMES[index]}
            </span>

            <span class="responder-bar">
              <div
                style="width:${width}%"
              ></div>
            </span>

            <span class="responder-value">
              ${value.toExponential(2)}
            </span>
          </div>
        `;
      }
    )
    .join("");
}


function rolesText(
  node
) {
  const roles = [];

  if (
    node.roles
    & ROLE.RETINA
  ) {
    roles.push("retina");
  }

  if (
    node.roles
    & ROLE.RELAY
  ) {
    roles.push("relay");
  }

  if (
    node.roles
    & ROLE.GRADED
  ) {
    roles.push(
      node.gradedType
      || "graded"
    );
  }

  if (
    node.roles
    & ROLE.DN
  ) {
    roles.push(
      `DN-C${node.dnCluster}`
    );
  }

  if (
    node.roles
    & ROLE.RESPONDER
  ) {
    roles.push(
      "MQ-3 responder"
    );
  }

  return roles.join(", ");
}


function renderSelection() {
  if (
    selectedLocal === null
  ) {
    selectionEl.innerHTML =
      "Click a neuron.";

    return;
  }

  const node =
    replay.nodes[
      selectedLocal
    ];

  const effective =
    activeMap.get(
      selectedLocal
    ) || 0;

  const voltage =
    voltageMap.get(
      selectedLocal
    ) || 0;

  const spike =
    spikeSet.has(
      selectedLocal
    );

  selectionEl.innerHTML = `
    <div>
      <span class="selection-key">
        model index
      </span>
      ${node.i}
    </div>

    <div>
      <span class="selection-key">
        bodyId
      </span>
      ${node.body}
    </div>

    <div>
      <span class="selection-key">
        role
      </span>
      ${rolesText(node)}
    </div>

    <div>
      <span class="selection-key">
        effective
      </span>
      ${effective.toExponential(4)}
    </div>

    <div>
      <span class="selection-key">
        +voltage
      </span>
      ${voltage.toExponential(4)}
    </div>

    <div>
      <span class="selection-key">
        spike
      </span>
      ${spike ? "YES" : "NO"}
    </div>
  `;
}


function nearestNode(
  x,
  y
) {
  let best = null;
  let bestDistance = 12;

  for (
    let i = 0;
    i < positions.length;
    i += 1
  ) {

    const p =
      positions[i];

    const dx =
      p.x - x;

    const dy =
      p.y - y;

    const distance =
      Math.sqrt(
        dx * dx
        + dy * dy
      );

    if (
      distance
      < bestDistance
    ) {
      bestDistance =
        distance;

      best = i;
    }
  }

  return best;
}


canvas.addEventListener(
  "click",
  (event) => {

    const rect =
      canvas
        .getBoundingClientRect();

    selectedLocal =
      nearestNode(
        event.clientX
          - rect.left,
        event.clientY
          - rect.top
      );

    render();
  }
);


timeline.addEventListener(
  "input",
  () => {

    frame =
      Number(
        timeline.value
      );

    render();
  }
);


document
  .getElementById("back")
  .addEventListener(
    "click",
    () => {

      frame =
        Math.max(
          0,
          frame - 1
        );

      render();
    }
  );


document
  .getElementById("forward")
  .addEventListener(
    "click",
    () => {

      frame =
        Math.min(
          replay.frameCount - 1,
          frame + 1
        );

      render();
    }
  );


playButton.addEventListener(
  "click",
  () => {

    playing =
      !playing;

    playButton.textContent =
      playing
        ? "PAUSE"
        : "PLAY";

    if (timer) {
      clearInterval(
        timer
      );

      timer = null;
    }

    if (playing) {

      timer =
        setInterval(
          () => {

            frame += 1;

            if (
              frame
              >= replay.frameCount
            ) {
              frame = 0;
            }

            render();
          },
          120
        );
    }
  }
);



causalToggle.addEventListener(
  "change",
  render
);


window.addEventListener(
  "resize",
  resizeCanvas
);


function animateEvidence() {
  if (
    replay
    && causalToggle.checked
    && replay.causalEdges.some(
      (edge) =>
        edge.frames.includes(
          frame
        )
    )
  ) {
    render();
  }

  requestAnimationFrame(
    animateEvidence
  );
}


async function init() {
  const response =
    await fetch(DATA);

  if (!response.ok) {
    throw new Error(
      `Replay load failed: ${response.status}`
    );
  }

  replay =
    await response.json();

  timeline.max =
    String(
      replay.frameCount - 1
    );

  frame =
    Math.min(
      145,
      replay.frameCount - 1
    );

  resizeCanvas();

  requestAnimationFrame(
    animateEvidence
  );

  console.log(
    "Neuroscope loaded",
    {
      schema:
        replay.schema,
      frames:
        replay.frameCount,
      nodes:
        replay.populationCount,
    }
  );
}


init().catch(
  (error) => {

    console.error(
      error
    );

    selectionEl.textContent =
      `LOAD ERROR: ${error.message}`;
  }
);
