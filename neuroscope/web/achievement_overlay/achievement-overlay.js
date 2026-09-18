(() => {
  const FEED_URL = "/public_data/achievements_v1.json";
  const SEEN_KEY = "moscaquant-achievements-seen-v3";
  const DEMO_KEY = "moscaquant-achievement-demo-v3";
  const DISPLAY_MS = 5200;

  const state = {
    queue: [],
    active: false,
    byId: new Map(),
    seen: new Set(),
    audioContext: null,
    audioUnlocked: false,
  };

  const CATEGORY_PRIORITY = {
    SECRET_ODDITY: 0,
    SCIENCE: 1,
    CONTAINMENT: 2,
    ORACLE: 3,
    BEHAVIOR: 4,
    ANOMALOUS_OBSERVANCE: 5,
    LORE: 6,
  };

  const EVIDENCE_PRIORITY = {
    E4: 0,
    E3: 1,
    E2: 2,
    E1: 3,
    E0: 4,
  };

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function signature(item) {
    return `${item.achievement_id}:${item.stack_count}`;
  }

  function seenSet() {
    try {
      return new Set(JSON.parse(localStorage.getItem(SEEN_KEY) || "[]"));
    } catch {
      return new Set();
    }
  }

  function saveSeen() {
    localStorage.setItem(SEEN_KEY, JSON.stringify([...state.seen].sort()));
  }

  function getAudioContext() {
    if (!state.audioContext) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return null;
      state.audioContext = new AudioCtx();
    }
    return state.audioContext;
  }

  async function unlockAudio() {
    const ctx = getAudioContext();
    if (!ctx) return;
    if (ctx.state === "suspended") {
      try { await ctx.resume(); } catch {}
    }
    state.audioUnlocked = ctx.state === "running";
  }

  ["pointerdown", "keydown", "touchstart"].forEach(eventName => {
    window.addEventListener(eventName, unlockAudio, { once: true, passive: true });
  });

  function pulse(ctx, destination, {
    start,
    frequency,
    duration,
    gain,
    type = "sine",
    detune = 0,
  }) {
    const osc = ctx.createOscillator();
    const amp = ctx.createGain();

    osc.type = type;
    osc.frequency.setValueAtTime(frequency, start);
    osc.detune.setValueAtTime(detune, start);

    amp.gain.setValueAtTime(0.0001, start);
    amp.gain.exponentialRampToValueAtTime(gain, start + 0.012);
    amp.gain.exponentialRampToValueAtTime(0.0001, start + duration);

    osc.connect(amp);
    amp.connect(destination);

    osc.start(start);
    osc.stop(start + duration + 0.02);
  }

  function playSting(item) {
    const ctx = getAudioContext();
    if (!ctx || ctx.state !== "running") return;

    const master = ctx.createGain();
    master.gain.value = 0.22;
    master.connect(ctx.destination);

    const now = ctx.currentTime + 0.01;

    // Original MoscaQuant reward shape:
    // short mechanical confirmation followed by a bright digital blip.
    pulse(ctx, master, {
      start: now,
      frequency: 92,
      duration: 0.105,
      gain: 0.42,
      type: "triangle",
    });

    const evidence = item.evidence_level || "E0";

    const profiles = {
      E0: [560],
      E1: [610],
      E2: [660, 880],
      E3: [690, 920],
      E4: [720, 960, 1200],
    };

    const notes = profiles[evidence] || profiles.E0;

    notes.forEach((frequency, index) => {
      pulse(ctx, master, {
        start: now + 0.082 + index * 0.045,
        frequency,
        duration: 0.18 + index * 0.025,
        gain: 0.16 - index * 0.025,
        type: "sine",
      });
    });

    if (item.category === "SECRET_ODDITY") {
      pulse(ctx, master, {
        start: now + 0.095,
        frequency: 777,
        duration: 0.23,
        gain: 0.07,
        type: "sawtooth",
        detune: -31,
      });
    }

    setTimeout(() => {
      try { master.disconnect(); } catch {}
    }, 800);
  }

  function host() {
    let node = document.getElementById("mq-achievement-host");
    if (node) return node;

    node = document.createElement("div");
    node.id = "mq-achievement-host";
    node.setAttribute("aria-live", "polite");
    document.body.appendChild(node);
    return node;
  }

  function dossierNode() {
    let node = document.getElementById("mq-achievement-dossier");
    if (node) return node;

    node = document.createElement("section");
    node.id = "mq-achievement-dossier";
    node.className = "mq-achievement-dossier";
    node.hidden = true;
    document.body.appendChild(node);

    document.addEventListener("keydown", event => {
      if (event.key === "Escape" && !node.hidden) node.hidden = true;
    });

    return node;
  }

  function showDossier(item) {
    const node = dossierNode();

    const evidence = (item.public_evidence_refs || [])
      .map(ref => `<code>${escapeHtml(ref)}</code>`)
      .join("<br>");

    const tags = (item.tags || [])
      .map(tag => `<span class="mq-dossier-tag">${escapeHtml(tag)}</span>`)
      .join("");

    const related = (item.related_achievement_ids || [])
      .map(id => {
        const relatedItem = state.byId.get(id);
        const label = relatedItem
          ? `${id} · ${relatedItem.title}`
          : id;

        return `
          <button
            type="button"
            class="mq-related-achievement"
            data-achievement-id="${escapeHtml(id)}"
          >
            ${escapeHtml(label)}
          </button>
        `;
      })
      .join("");

    const boundary = item.claim_boundary
      ? `
        <section class="mq-dossier-section mq-dossier-boundary">
          <div class="mq-dossier-section-label">Claim boundary</div>
          <p>${escapeHtml(item.claim_boundary)}</p>
        </section>
      `
      : "";

    const socialBadge = item.social_eligible
      ? `<span class="mq-dossier-badge mq-dossier-badge-social">SOCIAL ELIGIBLE</span>`
      : `<span class="mq-dossier-badge">PANOPTICON ONLY</span>`;

    node.dataset.priority = item.dossier_priority || "NORMAL";
    node.dataset.syndication = item.syndication_class || "NOISE";

    node.innerHTML = `
      <button class="mq-achievement-close" aria-label="Close">&times;</button>

      <div class="mq-dossier-header">
        <div class="mq-dossier-eyebrow">
          ${escapeHtml(item.achievement_id)}
        </div>

        <h2>${escapeHtml(item.title)}</h2>
        <p class="mq-dossier-public-text">${escapeHtml(item.public_text)}</p>

        <div class="mq-dossier-badges">
          <span class="mq-dossier-badge mq-dossier-badge-evidence">
            ${escapeHtml(item.evidence_level)}
          </span>
          <span class="mq-dossier-badge">
            ${escapeHtml(item.category)}
          </span>
          <span class="mq-dossier-badge">
            ${escapeHtml(item.family || "UNCLASSIFIED")}
          </span>
          <span class="mq-dossier-badge">
            ${escapeHtml(item.provenance_class || "UNKNOWN")}
          </span>
          <span class="mq-dossier-badge">
            ${escapeHtml(item.dossier_priority || "NORMAL")} PRIORITY
          </span>
          <span class="mq-dossier-badge mq-dossier-badge-broadcast">
            ${escapeHtml(item.syndication_class || "NOISE")}
          </span>
          ${socialBadge}
        </div>
      </div>

      <section class="mq-dossier-section">
        <div class="mq-dossier-section-label">Scientific interpretation</div>
        <p>${escapeHtml(item.science_text)}</p>
      </section>

      ${boundary}

      <section class="mq-dossier-grid">
        <div class="mq-dossier-stat">
          <span>Occurrences</span>
          <strong>${escapeHtml(item.stack_count)}</strong>
        </div>
        <div class="mq-dossier-stat">
          <span>First recorded</span>
          <strong>${escapeHtml(item.first_recorded_date || "n/a")}</strong>
        </div>
        <div class="mq-dossier-stat">
          <span>Latest recorded</span>
          <strong>${escapeHtml(item.latest_recorded_date || "n/a")}</strong>
        </div>
        <div class="mq-dossier-stat">
          <span>Historical replay</span>
          <strong>${item.historical_replay ? "YES" : "NO"}</strong>
        </div>
      </section>

      <section class="mq-dossier-section">
        <div class="mq-dossier-section-label">Tags</div>
        <div class="mq-dossier-tags">
          ${tags || '<span class="mq-dossier-empty">No tags</span>'}
        </div>
      </section>

      <section class="mq-dossier-section">
        <div class="mq-dossier-section-label">Related achievements</div>
        <div class="mq-related-achievements">
          ${related || '<span class="mq-dossier-empty">No related achievements</span>'}
        </div>
      </section>

      <section class="mq-dossier-section">
        <div class="mq-dossier-section-label">Public evidence</div>
        <div class="mq-dossier-evidence">
          ${evidence || '<span class="mq-dossier-empty">No public evidence references</span>'}
        </div>
      </section>
    `;

    node.hidden = false;

    node.querySelector(".mq-achievement-close").onclick = () => {
      node.hidden = true;
    };

    node.querySelectorAll(".mq-related-achievement").forEach(button => {
      button.onclick = () => {
        const relatedItem = state.byId.get(button.dataset.achievementId);
        if (relatedItem) showDossier(relatedItem);
      };
    });
  }

  function sortQueue() {
    state.queue.sort((a, b) => {
      const categoryDelta =
        (CATEGORY_PRIORITY[a.category] ?? 99) -
        (CATEGORY_PRIORITY[b.category] ?? 99);

      if (categoryDelta !== 0) return categoryDelta;

      const evidenceDelta =
        (EVIDENCE_PRIORITY[a.evidence_level] ?? 99) -
        (EVIDENCE_PRIORITY[b.evidence_level] ?? 99);

      if (evidenceDelta !== 0) return evidenceDelta;

      return a.achievement_id.localeCompare(b.achievement_id);
    });
  }

  async function drain() {
    if (state.active || state.queue.length === 0) return;

    state.active = true;
    sortQueue();

    const item = state.queue.shift();
    const node = document.createElement("button");
    node.type = "button";
    node.className = "mq-achievement-toast";
    node.dataset.evidence = item.evidence_level || "E0";
    node.dataset.category = item.category || "UNKNOWN";

    node.innerHTML = `
      <span class="mq-achievement-sheen" aria-hidden="true"></span>
      <span class="mq-achievement-badge" aria-hidden="true">
        <span class="mq-achievement-badge-core">MQ</span>
      </span>
      <span class="mq-achievement-body">
        <span class="mq-achievement-kicker">
          ACHIEVEMENT UNLOCKED
          <span class="mq-achievement-stack">×${escapeHtml(item.stack_count)}</span>
        </span>
        <span class="mq-achievement-title">${escapeHtml(item.title)}</span>
        <span class="mq-achievement-copy">${escapeHtml(item.public_text)}</span>
        <span class="mq-achievement-meta">${escapeHtml(item.evidence_level)} · ${escapeHtml(item.category)}</span>
      </span>
    `;

    node.onclick = async () => {
      await unlockAudio();
      showDossier(item);
    };

    host().appendChild(node);

    requestAnimationFrame(() => {
      node.dataset.open = "true";
      state.seen.add(signature(item));
      saveSeen();
      playSting(item);
    });

    await new Promise(resolve => setTimeout(resolve, DISPLAY_MS));

    node.dataset.open = "false";
    await new Promise(resolve => setTimeout(resolve, 420));
    node.remove();

    state.active = false;
    drain();
  }

  function enqueue(item) {
    const sig = signature(item);
    if (state.queue.some(queued => signature(queued) === sig)) return;

    state.queue.push(item);
    sortQueue();
    drain();
  }

  async function init() {
    const response = await fetch(FEED_URL, { cache: "no-store" });
    if (!response.ok) throw new Error(`achievement feed HTTP ${response.status}`);

    const data = await response.json();
    state.seen = seenSet();

    for (const item of data.achievements || []) {
      state.byId.set(item.achievement_id, item);

      if (!item.historical_replay && !state.seen.has(signature(item))) {
        enqueue(item);
      }
    }

    if (!localStorage.getItem(DEMO_KEY)) {
      const demo = state.byId.get("ACH-003");
      if (demo) {
        setTimeout(() => enqueue(demo), 650);
        localStorage.setItem(DEMO_KEY, "shown");
      }
    }
  }

  window.MoscaQuantAchievements = {
    enqueueById(id) {
      const item = state.byId.get(id);
      if (item) enqueue(item);
    },

    showDossierById(id) {
      const item = state.byId.get(id);
      if (item) showDossier(item);
    },

    async replayDemo() {
      await unlockAudio();
      const item = state.byId.get("ACH-003");
      if (item) enqueue(item);
    },

    async soundTest(evidenceLevel = "E3") {
      await unlockAudio();
      playSting({
        evidence_level: evidenceLevel,
        category: "SCIENCE",
      });
    },
  };

  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      () => init().catch(console.error)
    );
  } else {
    init().catch(console.error);
  }
})();
