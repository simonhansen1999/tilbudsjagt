/* Tilbudsjagt card – følger med integrationen. */
const TJ_VERSION = "__VERSION__"; // sættes af release-workflowet

const THEMES = {
  blue: { a: "#2f7cf6", b: "#0b2a6b", c: "#5cc8ff", hero: "linear-gradient(120deg, #0b2a6b 0%, #0d47a1 55%, #d32f2f 140%)" },
  red: { a: "#e8394a", b: "#4a0710", c: "#ff9aa4", hero: "linear-gradient(120deg, #4a0710 0%, #a3101d 55%, #e53935 120%)" },
  green: { a: "#1fb26b", b: "#0b3d1f", c: "#7ef0b6", hero: "linear-gradient(120deg, #0b3d1f 0%, #1b7a3a 60%, #9ccc65 140%)" },
  purple: { a: "#9b5cf6", b: "#2a0b4d", c: "#d4b8ff", hero: "linear-gradient(120deg, #2a0b4d 0%, #5e2ca5 60%, #ec407a 140%)" },
  orange: { a: "#f59e0b", b: "#5d2600", c: "#ffd27a", hero: "linear-gradient(120deg, #5d2600 0%, #d35400 60%, #ffb300 140%)" },
};

const UNIT_TITLE = { ltr: "Billigste literpris", kg: "Billigste kilopris", stk: "Billigste stykpris" };
const UNIT_SHORT = { ltr: "l", kg: "kg", stk: "stk" };
const PACKAGE = { ds: ["dåse", "dåser"], fl: ["flaske", "flasker"] };
const MONTHS = ["jan.", "feb.", "mar.", "apr.", "maj", "jun.", "jul.", "aug.", "sep.", "okt.", "nov.", "dec."];

const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const kr = (n) => (Number(n) || 0).toFixed(2).replace(".", ",");
const num = (n) => String(Number(n) || 0).replace(".", ",");
const isoToday = () => {
  const t = new Date();
  return `${t.getFullYear()}-${String(t.getMonth() + 1).padStart(2, "0")}-${String(t.getDate()).padStart(2, "0")}`;
};

const ICON = {
  cart: "M7 18a2 2 0 1 0 0 4 2 2 0 0 0 0-4Zm10 0a2 2 0 1 0 0 4 2 2 0 0 0 0-4ZM7.2 14h9.9a2 2 0 0 0 1.8-1.1L22 6H5.2l-.9-2H1v2h2l3.6 7.6L5.2 16c-.7 1.3.3 2 1.8 2h12v-2H7.4l.8-2Z",
  calendar: "M19 4h-1V2h-2v2H8V2H6v2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2Zm0 16H5V9h14v11Z",
  star: "M12 17.3 18.2 21l-1.6-7 5.4-4.7-7.1-.6L12 2 9.1 8.7 2 9.3 7.4 14l-1.6 7z",
  info: "M11 7h2v2h-2V7Zm0 4h2v6h-2v-6Zm1-9a10 10 0 1 0 0 20 10 10 0 0 0 0-20Z",
};
const CAN = `<svg class="can" viewBox="0 0 60 100" aria-hidden="true">
  <defs>
    <linearGradient id="tjBody" x1="0" x2="1"><stop offset="0" stop-color="#05070d"/><stop offset=".45" stop-color="#2a3246"/><stop offset="1" stop-color="#05070d"/></linearGradient>
    <linearGradient id="tjMetal" x1="0" x2="1"><stop offset="0" stop-color="#8a93a6"/><stop offset=".5" stop-color="#f1f4fa"/><stop offset="1" stop-color="#8a93a6"/></linearGradient>
  </defs>
  <path d="M8 12 L8 88 Q8 96 30 96 Q52 96 52 88 L52 12 Q52 18 30 18 Q8 18 8 12 Z" fill="url(#tjBody)"/>
  <ellipse cx="30" cy="12" rx="22" ry="5.5" fill="url(#tjMetal)"/>
  <ellipse cx="30" cy="12" rx="16" ry="3.2" fill="#cfd5e2"/>
  <path d="M8 42 Q30 50 52 42 L52 62 Q30 70 8 62 Z" fill="var(--tj-c)"/>
  <rect x="13" y="22" width="4" height="68" rx="2" fill="#fff" opacity=".13"/>
</svg>`;

const svg = (name) => `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${ICON[name]}"/></svg>`;

function sizeText(o) {
  const n = Number(o.size) || 0;
  if (o.unit === "ltr") return n < 1 ? `${Math.round(n * 100)} cl` : `${num(n)} l`;
  if (o.unit === "kg") return n < 1 ? `${Math.round(n * 1000)} g` : `${num(n)} kg`;
  return `${num(n)} stk.`;
}

function packWords(o) {
  return PACKAGE[o.package] || ["stk.", "stk."];
}

function packText(o) {
  const [one, many] = packWords(o);
  return o.units > 1 ? `${o.units} ${many} à ${sizeText(o)}` : `1 ${one} à ${sizeText(o)}`;
}

function dateRange(start, end) {
  if (!start || !end) return "";
  const [, sm, sd] = start.split("-").map(Number);
  const [, em, ed] = end.split("-").map(Number);
  return sm === em ? `${sd}.–${ed}. ${MONTHS[em - 1]}` : `${sd}. ${MONTHS[sm - 1]} – ${ed}. ${MONTHS[em - 1]}`;
}

function initials(chain) {
  return String(chain)
    .replace(/[^A-Za-zÆØÅæøå0-9 ]/g, "")
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join("");
}

const STYLE = `
  :host { display: block; }
  ha-card { overflow: hidden; border-radius: 22px; font-family: var(--ha-font-family-body, inherit); }

  /* Topbanner */
  .hero {
    position: relative; overflow: hidden; color: #fff; margin: 10px 10px 4px; padding: 16px 20px;
    border-radius: 16px; background: var(--tj-hero);
    box-shadow: 0 4px 18px color-mix(in srgb, var(--tj-a) 45%, transparent);
  }
  .hero-grid { position: relative; z-index: 1; display: grid; grid-template-columns: 1fr auto; gap: 16px; align-items: center; }
  .kicker { font-size: 11px; font-weight: 600; letter-spacing: .28em; text-transform: uppercase; opacity: .8; }
  .title { font-size: 28px; font-weight: 800; line-height: 1.1; margin-top: 4px; letter-spacing: .02em; text-transform: uppercase; }
  .sub { font-size: 12.5px; opacity: .85; margin-top: 3px; }
  .art { width: 64px; display: flex; justify-content: center; }
  .can { width: 50px; height: 84px; transform: rotate(10deg); filter: drop-shadow(0 4px 6px rgba(0,0,0,.55)); }
  .art img { max-width: 70px; max-height: 84px; object-fit: contain; filter: drop-shadow(0 4px 6px rgba(0,0,0,.55)); }

  /* Liste */
  .list { padding: 10px; display: flex; flex-direction: column; }
  .row {
    position: relative; display: grid; grid-template-columns: 52px 1fr auto; gap: 14px; align-items: center;
    padding: 14px 12px; border-radius: 16px; cursor: pointer; transition: background .15s ease, transform .15s ease;
  }
  .row + .row::before {
    content: ""; position: absolute; left: 78px; right: 12px; top: 0; height: 1px; background: var(--divider-color, rgba(127,127,127,.18));
  }
  .row.top + .row::before { display: none; }
  .row:hover { background: rgba(127,127,127,.07); }
  .row.top {
    margin-bottom: 6px;
    background:
      linear-gradient(var(--tj-surface), var(--tj-surface)) padding-box,
      linear-gradient(135deg, var(--tj-a), var(--tj-c)) border-box;
    border: 1.5px solid transparent;
    box-shadow: 0 8px 24px -12px color-mix(in srgb, var(--tj-a) 70%, transparent);
  }
  .row.top:hover { transform: translateY(-1px); }

  .logo {
    position: relative; width: 52px; height: 52px; border-radius: 15px; background: #fff;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 2px 6px rgba(0,0,0,.14), inset 0 0 0 1px rgba(0,0,0,.06);
  }
  .logo span { position: absolute; color: #3c4043; font-weight: 800; font-size: 15px; }
  .logo img { position: relative; width: 100%; height: 100%; object-fit: contain; padding: 6px; box-sizing: border-box; border-radius: 15px; background: #fff; }
  .rank {
    position: absolute; right: -7px; bottom: -7px; min-width: 22px; height: 22px; padding: 0 5px; box-sizing: border-box;
    border-radius: 11px; font-size: 11px; font-weight: 800; display: flex; align-items: center; justify-content: center;
    background: var(--secondary-background-color, #e8eaed); color: var(--primary-text-color);
    box-shadow: 0 0 0 2.5px var(--tj-surface);
  }
  .top .rank { background: linear-gradient(135deg, #ffd76a, #f5a623); color: #3a2500; }

  .main { min-width: 0; }
  .head { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  .chain { font-size: 16px; font-weight: 700; color: var(--primary-text-color); letter-spacing: -.005em; }
  .badge {
    display: inline-flex; align-items: center; gap: 4px; padding: 3px 9px 3px 7px; border-radius: 999px;
    font-size: 10.5px; font-weight: 800; letter-spacing: .04em; text-transform: uppercase; color: #fff;
    background: linear-gradient(135deg, var(--tj-a), color-mix(in srgb, var(--tj-a) 60%, var(--tj-b)));
    box-shadow: 0 2px 8px -2px color-mix(in srgb, var(--tj-a) 80%, transparent);
  }
  .badge svg { width: 12px; height: 12px; fill: #ffd76a; }
  .pack { font-size: 14px; font-weight: 600; color: var(--primary-text-color); margin-top: 4px; }
  .pack .dot { opacity: .4; margin: 0 4px; }
  .pack .total { font-weight: 800; }
  .pack .pant { font-weight: 500; color: var(--secondary-text-color); font-size: 12px; }
  .each { font-size: 12px; color: var(--secondary-text-color); margin-top: 2px; }
  .chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
  .chip {
    display: inline-flex; align-items: center; gap: 5px; padding: 3px 9px; border-radius: 999px;
    font-size: 11px; font-weight: 600; color: var(--secondary-text-color); background: rgba(127,127,127,.11);
  }
  .chip svg { width: 12px; height: 12px; fill: currentColor; opacity: .8; }
  .chip.limit { color: #7a4300; background: linear-gradient(135deg, #ffe9b8, #ffd98a); box-shadow: inset 0 0 0 1px rgba(160,100,0,.18); }
  .chip.soon { color: #0b4f8a; background: #d9ecff; }
  .chip.last { color: #8a1c1c; background: #ffdede; }

  .price { text-align: right; white-space: nowrap; }
  .unit-price { font-size: 25px; font-weight: 800; line-height: 1; color: var(--primary-text-color); font-variant-numeric: tabular-nums; letter-spacing: -.02em; }
  .unit-price small { font-size: 12px; font-weight: 600; color: var(--secondary-text-color); margin-left: 3px; letter-spacing: 0; }
  .top .unit-price { color: var(--tj-a); font-size: 28px; }
  .meter { margin: 8px 0 0 auto; width: 72px; height: 4px; border-radius: 2px; background: rgba(127,127,127,.18); overflow: hidden; }
  .meter i { display: block; height: 100%; border-radius: 2px; background: rgba(127,127,127,.55); }
  .top .meter i { background: linear-gradient(90deg, var(--tj-a), var(--tj-c)); }
  .diff { font-size: 11.5px; font-weight: 700; color: var(--secondary-text-color); margin-top: 5px; font-variant-numeric: tabular-nums; }

  .empty { padding: 28px; text-align: center; color: var(--secondary-text-color); }
  .foot { padding: 2px 22px 14px; font-size: 11px; color: var(--secondary-text-color); opacity: .8; }

  @media (max-width: 420px) {
    .hero { padding: 14px 16px; }
    .title { font-size: 24px; }
    .can { width: 44px; height: 74px; }
    .art { width: 54px; }
    .row { grid-template-columns: 44px 1fr auto; gap: 11px; padding: 12px 10px; }
    .row + .row::before { left: 65px; }
    .logo { width: 44px; height: 44px; border-radius: 13px; }
    .unit-price { font-size: 21px; }
    .top .unit-price { font-size: 23px; }
  }
`;

class TilbudsjagtCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
  }

  setConfig(config) {
    if (!config.entity) throw new Error("Vælg en Tilbudsjagt-sensor (entity)");
    this._config = { theme: "blue", max_rows: 5, show_header: true, show_updated: true, ...config };
    this._sig = null;
    if (this._hass) this._render();
  }

  set hass(hass) {
    this._hass = hass;
    const st = hass.states[this._config.entity];
    const sig = st ? `${st.last_updated}|${isoToday()}` : "missing";
    if (sig === this._sig) return;
    this._sig = sig;
    this._render();
  }

  getCardSize() {
    return 3 + (this._config?.max_rows ?? 5) * 2;
  }

  getGridOptions() {
    return { columns: 12, min_columns: 6, rows: "auto" };
  }

  static getConfigElement() {
    return document.createElement("tilbudsjagt-card-editor");
  }

  static getStubConfig(hass) {
    const entity = Object.keys(hass.states).find(
      (id) => id.startsWith("sensor.") && Array.isArray(hass.states[id].attributes.offers)
    );
    return { entity: entity || "" };
  }

  _row(o, i, best, short, today) {
    const top = i === 0;
    const [one] = packWords(o);
    const each = o.units > 1 ? `${kr(o.price / o.units)} kr pr. ${one}${o.deposit_included ? " inkl. pant" : ""}` : "";
    const pant = o.deposit && !o.deposit_included ? `<span class="pant"> + pant</span>` : "";
    const diff = Number(o.unit_price) - best;
    const pct = Math.max(10, Math.min(100, Math.round((best / Number(o.unit_price)) * 100)));

    const chips = [`<span class="chip">${svg("calendar")}${esc(dateRange(o.start, o.end))}</span>`];
    if (o.start > today) chips.push(`<span class="chip soon">Starter snart</span>`);
    else if (o.end === today) chips.push(`<span class="chip last">Sidste dag</span>`);
    if (o.deposit_included) chips.push(`<span class="chip">Inkl. ${kr(o.deposit)} kr pant</span>`);
    if (o.limit) chips.push(`<span class="chip limit">${svg("cart")}Maks. ${esc(o.limit)} pr. kunde</span>`);
    for (const note of o.notes || []) chips.push(`<span class="chip">${svg("info")}${esc(note)}</span>`);

    return `<div class="row ${top ? "top" : ""}" data-url="${esc(o.url)}">
      <div class="logo">
        <span>${esc(initials(o.chain))}</span>
        <img src="${esc(o.logo)}" referrerpolicy="no-referrer" alt="">
        <div class="rank">${i + 1}</div>
      </div>
      <div class="main">
        <div class="head">
          <span class="chain">${esc(o.chain)}</span>
          ${top ? `<span class="badge">${svg("star")}Bedste pris</span>` : ""}
        </div>
        <div class="pack">${esc(packText(o))}<span class="dot">•</span><span class="total">${kr(o.price)} kr</span>${pant}</div>
        ${each ? `<div class="each">${esc(each)}</div>` : ""}
        <div class="chips">${chips.join("")}</div>
      </div>
      <div class="price">
        <div class="unit-price">${kr(o.unit_price)}<small>${short}</small></div>
        <div class="meter"><i style="width:${pct}%"></i></div>
        ${top ? "" : `<div class="diff">${diff > 0.004 ? `+${kr(diff)} ${short}` : "Samme pris"}</div>`}
      </div>
    </div>`;
  }

  _render() {
    const c = this._config;
    const theme = THEMES[c.theme] || THEMES.blue;
    const st = this._hass.states[c.entity];
    const a = st?.attributes || {};
    const offers = (a.offers || []).slice(0, c.max_rows);
    const unit = a.unit || "ltr";
    const short = UNIT_SHORT[unit] ? `kr/${UNIT_SHORT[unit]}` : "kr";
    const today = isoToday();
    const best = offers.length ? Number(offers[0].unit_price) : 0;

    const sub = c.subtitle ?? `${UNIT_TITLE[unit] || "Billigste pris"}${a.include_deposit ? " · inkl. pant" : ""}`;
    const header = c.show_header
      ? `<div class="hero"><div class="hero-grid">
          <div>
            <div class="kicker">${esc(c.kicker ?? "Tilbudsjagt")}</div>
            <div class="title">${esc(c.title || a.friendly_name || "Tilbud")}</div>
            <div class="sub">${esc(sub)}</div>
          </div>
          <div class="art">${c.image ? `<img src="${esc(c.image)}" alt="">` : CAN}</div>
        </div></div>`
      : "";

    const body = offers.length
      ? `<div class="list">${offers.map((o, i) => this._row(o, i, best, short, today)).join("")}</div>`
      : `<div class="empty">${st ? "Ingen tilbud lige nu" : `Entiteten ${esc(c.entity)} findes ikke`}</div>`;

    let foot = "";
    if (c.show_updated && a.last_fetch) {
      const d = new Date(a.last_fetch);
      foot = `<div class="foot">Opdateret ${d.toLocaleDateString("da-DK")} kl. ${d.toLocaleTimeString("da-DK", { hour: "2-digit", minute: "2-digit" })}</div>`;
    }

    this.shadowRoot.innerHTML = `<style>${STYLE}</style>
      <ha-card style="--tj-a:${theme.a};--tj-b:${theme.b};--tj-c:${theme.c};--tj-hero:${theme.hero};--tj-surface:var(--ha-card-background, var(--card-background-color, #fff))">${header}${body}${foot}</ha-card>`;

    this.shadowRoot.querySelectorAll(".logo img").forEach((img) => img.addEventListener("error", () => img.remove()));
    this.shadowRoot.querySelectorAll(".row").forEach((row) =>
      row.addEventListener("click", () => window.open(row.dataset.url, "_blank", "noopener"))
    );
  }
}

const EDITOR_SCHEMA = [
  { name: "entity", required: true, selector: { entity: { domain: "sensor", integration: "tilbudsjagt" } } },
  { name: "title", selector: { text: {} } },
  { name: "subtitle", selector: { text: {} } },
  {
    name: "theme",
    selector: {
      select: {
        mode: "dropdown",
        options: [
          { value: "blue", label: "Blå" },
          { value: "red", label: "Rød" },
          { value: "green", label: "Grøn" },
          { value: "purple", label: "Lilla" },
          { value: "orange", label: "Orange" },
        ],
      },
    },
  },
  { name: "image", selector: { text: { type: "url" } } },
  { name: "max_rows", selector: { number: { min: 1, max: 20, mode: "box" } } },
  { name: "show_header", selector: { boolean: {} } },
  { name: "show_updated", selector: { boolean: {} } },
];

const EDITOR_LABELS = {
  entity: "Sensor",
  title: "Titel",
  subtitle: "Undertitel",
  theme: "Farvetema",
  image: "Billede-URL (valgfri, erstatter dåsen)",
  max_rows: "Antal rækker",
  show_header: "Vis topbanner",
  show_updated: "Vis 'opdateret'",
};

class TilbudsjagtCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = { theme: "blue", max_rows: 5, show_header: true, show_updated: true, ...config };
    this._update();
  }

  set hass(hass) {
    this._hass = hass;
    this._update();
  }

  _update() {
    if (!this._hass || !this._config) return;
    if (!this._form) {
      this._form = document.createElement("ha-form");
      this._form.schema = EDITOR_SCHEMA;
      this._form.computeLabel = (s) => EDITOR_LABELS[s.name] || s.name;
      this._form.addEventListener("value-changed", (ev) => {
        this._config = ev.detail.value;
        this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: this._config }, bubbles: true, composed: true }));
      });
      this.appendChild(this._form);
    }
    this._form.hass = this._hass;
    this._form.data = this._config;
  }
}

if (!customElements.get("tilbudsjagt-card")) customElements.define("tilbudsjagt-card", TilbudsjagtCard);
if (!customElements.get("tilbudsjagt-card-editor")) customElements.define("tilbudsjagt-card-editor", TilbudsjagtCardEditor);

window.customCards = window.customCards || [];
if (!window.customCards.some((c) => c.type === "tilbudsjagt-card")) {
  window.customCards.push({
    type: "tilbudsjagt-card",
    name: "Tilbudsjagt",
    description: "Billigste tilbud fra tilbudsugen.dk",
    preview: true,
  });
}

console.info(`%c TILBUDSJAGT-CARD %c v${TJ_VERSION} `, "background:#2f7cf6;color:#fff;font-weight:700", "background:#222;color:#fff");
