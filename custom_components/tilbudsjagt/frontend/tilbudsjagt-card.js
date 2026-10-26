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
  paper: "M20 3H4a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h16a1 1 0 0 0 1-1V4a1 1 0 0 0-1-1Zm-9 14H6v-2h5v2Zm0-4H6v-2h5v2Zm0-4H6V7h5v2Zm7 8h-5V7h5v10Z",
  search: "M15.5 14h-.8l-.3-.3A6.5 6.5 0 1 0 14 15.5l.3.3v.8l5 5 1.5-1.5-5-5Zm-6 0a4.5 4.5 0 1 1 0-9 4.5 4.5 0 0 1 0 9Z",
  close: "M19 6.4 17.6 5 12 10.6 6.4 5 5 6.4 10.6 12 5 17.6 6.4 19 12 13.4 17.6 19 19 17.6 13.4 12z",
  leaf: "M17 8C8 10 5.9 16.2 3.8 21.3l1.9.7 1-2.3c.5.2 1 .3 1.3.3C19 20 22 3 22 3c-1 2-8 2.2-13 3.2S2 11.5 2 13.5 3.8 17.3 3.8 17.3C7 8 17 8 17 8Z",
  check: "M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z",
  open: "M14 3v2h3.6l-9.8 9.8 1.4 1.4L19 6.4V10h2V3h-7ZM19 19H5V5h7V3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7h-2v7Z",
};
const svg = (name) => `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${ICON[name]}"/></svg>`;

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

const TAG = `<svg class="tag" viewBox="0 0 64 64" aria-hidden="true">
  <path d="M6 30V10a4 4 0 0 1 4-4h20l28 28-24 24z" fill="rgba(255,255,255,.95)"/>
  <circle cx="17" cy="17" r="4.5" fill="var(--tj-b)"/>
  <text x="36" y="42" text-anchor="middle" font-size="16" font-weight="900" fill="var(--tj-a)" font-family="Arial, sans-serif" transform="rotate(45 36 36)">%</text>
</svg>`;

function sizeText(o) {
  const n = Number(o.size) || 0;
  if (o.unit === "ltr") return n < 1 ? `${Math.round(n * 100)} cl` : `${num(n)} l`;
  if (o.unit === "kg") return n < 1 ? `${Math.round(n * 1000)} g` : `${num(n)} kg`;
  return `${num(n)} stk.`;
}

const packWords = (o) => PACKAGE[o.package] || ["stk.", "stk."];

function packText(o) {
  const [one, many] = packWords(o);
  if (!PACKAGE[o.package]) return o.units > 1 ? `${o.units} × ${sizeText(o)}` : sizeText(o);
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
  ha-card { overflow: hidden; border-radius: 22px; }

  /* Topbanner */
  .hero {
    position: relative; overflow: hidden; color: #fff; margin: 10px 10px 4px; padding: 16px 20px;
    border-radius: 16px; background: var(--tj-hero);
    box-shadow: 0 4px 18px color-mix(in srgb, var(--tj-a) 45%, transparent);
  }
  .hero-grid { position: relative; z-index: 1; display: grid; grid-template-columns: 1fr auto; gap: 16px; align-items: center; }
  .kicker { font-size: 11px; font-weight: 600; letter-spacing: .28em; text-transform: uppercase; opacity: .8; }
  .title { font-size: 28px; font-weight: 800; line-height: 1.1; margin-top: 4px; letter-spacing: .02em; text-transform: uppercase; overflow-wrap: anywhere; }
  .sub { font-size: 12.5px; opacity: .85; margin-top: 3px; }
  .art { width: 64px; display: flex; justify-content: center; }
  .can { width: 50px; height: 84px; transform: rotate(10deg); filter: drop-shadow(0 4px 6px rgba(0,0,0,.55)); }
  .tag { width: 58px; height: 58px; transform: rotate(-8deg); filter: drop-shadow(0 4px 6px rgba(0,0,0,.45)); }
  .art img { max-width: 70px; max-height: 84px; object-fit: contain; filter: drop-shadow(0 4px 6px rgba(0,0,0,.55)); }

  /* Søgning */
  .search {
    position: relative; z-index: 1; display: flex; align-items: center; gap: 8px; margin-top: 14px;
    padding: 0 6px 0 12px; height: 44px; border-radius: 12px;
    background: rgba(255,255,255,.16); box-shadow: inset 0 0 0 1px rgba(255,255,255,.22);
  }
  .search:focus-within { background: rgba(255,255,255,.24); box-shadow: inset 0 0 0 1.5px rgba(255,255,255,.6); }
  .search svg { width: 20px; height: 20px; fill: #fff; opacity: .85; flex: none; }
  .search input {
    flex: 1; min-width: 0; height: 100%; border: 0; outline: 0; background: none; color: #fff;
    font: inherit; font-size: 15px; font-weight: 600; -webkit-appearance: none; appearance: none;
  }
  .search input::-webkit-search-cancel-button { display: none; }
  .search input::placeholder { color: rgba(255,255,255,.65); font-weight: 500; }
  .search button { display: none; border: 0; background: none; padding: 6px; cursor: pointer; border-radius: 8px; }
  .search.has-text button { display: flex; }
  .search button:hover { background: rgba(255,255,255,.15); }
  .spinner {
    display: none; width: 16px; height: 16px; border-radius: 50%; flex: none;
    border: 2px solid rgba(255,255,255,.35); border-top-color: #fff; animation: spin .8s linear infinite;
  }
  .search.busy .spinner { display: block; }
  @keyframes spin { to { transform: rotate(360deg); } }

  .cats { display: flex; gap: 6px; overflow-x: auto; padding: 8px 12px 2px; scrollbar-width: none; }
  .tools { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; padding: 8px 12px 0; }
  .tools:empty { display: none; }
  .labels { display: flex; gap: 6px; flex-wrap: wrap; flex: 1; min-width: 0; }
  .lbl {
    display: inline-flex; align-items: center; gap: 6px; padding: 5px 10px 5px 7px; border-radius: 10px; cursor: pointer;
    font: inherit; font-size: 12.5px; font-weight: 600; color: var(--primary-text-color);
    background: rgba(127,127,127,.1); border: 1px solid rgba(127,127,127,.22);
  }
  .lbl .box {
    width: 15px; height: 15px; border-radius: 4px; box-sizing: border-box; flex: none;
    border: 1.5px solid var(--secondary-text-color); display: flex; align-items: center; justify-content: center;
  }
  .lbl .box svg { width: 13px; height: 13px; fill: #fff; display: none; }
  .lbl b { font-size: 11px; font-weight: 700; color: var(--secondary-text-color); }
  .lbl.on { border-color: var(--tj-a); background: color-mix(in srgb, var(--tj-a) 12%, transparent); }
  .lbl.on .box { background: var(--tj-a); border-color: var(--tj-a); }
  .lbl.on .box svg { display: block; }
  .count { display: inline-flex; margin-left: auto; padding: 3px; border-radius: 10px; background: rgba(127,127,127,.12); }
  .count button {
    border: 0; background: none; cursor: pointer; padding: 4px 10px; border-radius: 7px;
    font: inherit; font-size: 12px; font-weight: 700; color: var(--secondary-text-color);
  }
  .count button.on { color: var(--primary-text-color); background: var(--tj-surface); box-shadow: 0 1px 3px rgba(0,0,0,.2); }
  .count span { align-self: center; padding: 0 6px 0 8px; font-size: 11px; font-weight: 600; color: var(--secondary-text-color); }
  .cats::-webkit-scrollbar { display: none; }
  .cats:empty { display: none; }
  .cat {
    flex: none; display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 999px; cursor: pointer;
    font: inherit; font-size: 12.5px; font-weight: 600; color: var(--primary-text-color);
    background: rgba(127,127,127,.12); border: 1px solid transparent;
  }
  .cat b { font-weight: 700; font-size: 11px; color: var(--secondary-text-color); }
  .cat.on { color: #fff; background: var(--tj-a); }
  .cat.on b { color: rgba(255,255,255,.8); }

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
  .chain { font-size: 16px; font-weight: 700; color: var(--primary-text-color); }
  .badge {
    display: inline-flex; align-items: center; gap: 4px; padding: 3px 9px 3px 7px; border-radius: 999px;
    font-size: 10.5px; font-weight: 800; letter-spacing: .04em; text-transform: uppercase; color: #fff;
    background: linear-gradient(135deg, var(--tj-a), color-mix(in srgb, var(--tj-a) 60%, var(--tj-b)));
    box-shadow: 0 2px 8px -2px color-mix(in srgb, var(--tj-a) 80%, transparent);
  }
  .badge svg { width: 12px; height: 12px; fill: #ffd76a; }
  .name { font-size: 13.5px; font-weight: 600; color: var(--primary-text-color); margin-top: 3px; line-height: 1.25; }
  .pack { font-size: 14px; font-weight: 600; color: var(--primary-text-color); margin-top: 4px; }
  .name + .pack { font-size: 13px; font-weight: 500; color: var(--secondary-text-color); margin-top: 2px; }
  .pack .dot { opacity: .4; margin: 0 4px; }
  .pack .total { font-weight: 800; color: var(--primary-text-color); }
  .pack .pant { font-weight: 500; color: var(--secondary-text-color); font-size: 12px; }
  .each { font-size: 12px; color: var(--secondary-text-color); margin-top: 2px; }
  .chips { grid-column: 2 / -1; display: flex; flex-wrap: wrap; gap: 5px; margin-top: -4px; }
  .chip {
    display: inline-flex; align-items: center; gap: 4px; padding: 3px 8px; border-radius: 999px; white-space: nowrap;
    font-size: 11px; font-weight: 600; color: var(--secondary-text-color); background: rgba(127,127,127,.11);
  }
  .chip.label {
    --g: #22c55e;
    color: color-mix(in srgb, var(--g) 72%, var(--primary-text-color));
    background: color-mix(in srgb, var(--g) 13%, transparent);
    box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--g) 35%, transparent);
  }
  .chip.label svg { opacity: 1; }
  .chip svg { width: 12px; height: 12px; fill: currentColor; opacity: .8; }
  .chip.limit { color: #7a4300; background: linear-gradient(135deg, #ffe9b8, #ffd98a); box-shadow: inset 0 0 0 1px rgba(160,100,0,.18); }
  .chip.soon { color: #0b4f8a; background: #d9ecff; }
  .chip.last { color: #8a1c1c; background: #ffdede; }
  .chip.paper {
    cursor: pointer; border: 0; font: inherit; font-size: 11px; font-weight: 700;
    color: var(--tj-a); background: color-mix(in srgb, var(--tj-a) 14%, transparent);
  }
  .chip.paper:hover { background: color-mix(in srgb, var(--tj-a) 22%, transparent); }
  .chip.paper.on { color: #fff; background: var(--tj-a); }

  .price { text-align: right; white-space: nowrap; }
  .unit-price { font-size: 25px; font-weight: 800; line-height: 1; color: var(--primary-text-color); font-variant-numeric: tabular-nums; letter-spacing: -.02em; }
  .unit-price small { font-size: 12px; font-weight: 600; color: var(--secondary-text-color); margin-left: 3px; letter-spacing: 0; }
  .top .unit-price { color: var(--tj-a); font-size: 28px; }
  .meter { margin: 8px 0 0 auto; width: 72px; height: 4px; border-radius: 2px; background: rgba(127,127,127,.18); overflow: hidden; }
  .meter i { display: block; height: 100%; border-radius: 2px; background: rgba(127,127,127,.55); }
  .top .meter i { background: linear-gradient(90deg, var(--tj-a), var(--tj-c)); }
  .diff { font-size: 11.5px; font-weight: 700; color: var(--secondary-text-color); margin-top: 5px; font-variant-numeric: tabular-nums; }

  .flyer { grid-column: 1 / -1; margin-top: 4px; cursor: default; }
  .flyer-frame {
    position: relative; border-radius: 14px; overflow: hidden; background: #fff;
    box-shadow: 0 6px 20px -8px rgba(0,0,0,.35), inset 0 0 0 1px rgba(0,0,0,.06);
  }
  .flyer img { display: block; width: 100%; max-height: 420px; object-fit: contain; background: #fff; }
  .flyer a {
    position: absolute; right: 10px; bottom: 10px; display: inline-flex; align-items: center; gap: 6px;
    padding: 7px 12px; border-radius: 999px; font-size: 12px; font-weight: 700; text-decoration: none;
    color: #fff; background: rgba(0,0,0,.72); backdrop-filter: blur(6px);
  }
  .flyer a svg { width: 14px; height: 14px; fill: currentColor; }

  .empty { padding: 28px 20px; text-align: center; color: var(--secondary-text-color); font-size: 14px; }
  .foot { padding: 2px 22px 14px; font-size: 11px; color: var(--secondary-text-color); opacity: .8; }

  @media (max-width: 420px) {
    .hero { padding: 14px 16px; }
    .title { font-size: 24px; }
    .can { width: 44px; height: 74px; }
    .art { width: 54px; }
    .row { grid-template-columns: 44px 1fr auto; gap: 11px; padding: 12px 10px; }
    .chips { grid-column: 1 / -1; margin-top: 0; }
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
    this._open = new Set();
    this._pending = null;
    this._timer = null;
    this._labels = new Set();
    this._count = null;
  }

  setConfig(config) {
    if (!config.entity) throw new Error("Vælg en Tilbudsjagt-sensor (entity)");
    this._config = { theme: "blue", max_rows: 5, show_header: true, show_updated: true, ...config };
    this._built = null;
    this._sig = null;
    this._restore();
    if (this._hass) this._update();
  }

  set hass(hass) {
    this._hass = hass;
    const st = hass.states[this._config.entity];
    const sig = st ? `${st.last_updated}|${isoToday()}` : "missing";
    if (sig === this._sig && this._built) return;
    this._sig = sig;
    this._update();
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

  get _attrs() {
    return this._hass.states[this._config.entity]?.attributes || {};
  }

  /* Bygger den faste ramme én gang, så søgefeltet ikke mister fokus */
  _build(search) {
    const c = this._config;
    const theme = THEMES[c.theme] || THEMES.blue;
    this.shadowRoot.innerHTML = `<style>${STYLE}</style>
      <ha-card style="--tj-a:${theme.a};--tj-b:${theme.b};--tj-c:${theme.c};--tj-hero:${theme.hero};--tj-surface:var(--ha-card-background, var(--card-background-color, #fff))">
        ${
          c.show_header
            ? `<div class="hero">
                <div class="hero-grid">
                  <div>
                    <div class="kicker">${esc(c.kicker ?? "Tilbudsjagt")}</div>
                    <div class="title"></div>
                    <div class="sub"></div>
                  </div>
                  <div class="art"></div>
                </div>
                ${
                  search
                    ? `<label class="search">${svg("search")}
                        <input type="search" enterkeyhint="search" autocomplete="off" placeholder="Søg vare, fx smør eller kaffe">
                        <span class="spinner"></span>
                        <button type="button" title="Ryd">${svg("close")}</button>
                      </label>`
                    : ""
                }
              </div>`
            : ""
        }
        <div class="cats"></div>
        <div class="tools"></div>
        <div class="body"></div>
        <div class="foot"></div>
      </ha-card>`;

    const root = this.shadowRoot;
    root.querySelector(".body").addEventListener("click", (ev) => this._onBodyClick(ev));
    root.querySelector(".cats").addEventListener("click", (ev) => this._onCategory(ev));
    root.querySelector(".tools").addEventListener("click", (ev) => this._onTools(ev));

    const input = root.querySelector(".search input");
    if (input) {
      input.value = this._attrs.query || "";
      input.addEventListener("input", () => {
        this._syncSearchState();
        clearTimeout(this._timer);
        this._timer = setTimeout(() => this._search(input.value), 900);
      });
      input.addEventListener("keydown", (ev) => {
        if (ev.key === "Enter") {
          clearTimeout(this._timer);
          this._search(input.value);
          input.blur();
        }
      });
      root.querySelector(".search button").addEventListener("click", (ev) => {
        ev.preventDefault();
        input.value = "";
        this._search("");
        input.focus();
      });
    }
    this._built = search ? "search" : "product";
  }

  _search(value) {
    const query = value.trim();
    const entity = this._attrs.query_entity;
    if (!entity || query === (this._attrs.query || "")) {
      this._pending = null;
      this._syncSearchState();
      return;
    }
    this._pending = query;
    this._open.clear();
    this._resetLabels();
    this._syncSearchState();
    this._hass.callService("text", "set_value", { entity_id: entity, value: query });
  }

  _syncSearchState() {
    const box = this.shadowRoot.querySelector(".search");
    if (!box) return;
    box.classList.toggle("has-text", !!box.querySelector("input").value);
    box.classList.toggle("busy", this._pending !== null);
  }

  get _key() {
    return `tilbudsjagt:${this._config.entity}`;
  }

  _restore() {
    this._labels = new Set();
    this._count = null;
    try {
      const saved = JSON.parse(localStorage.getItem(this._key) || "{}");
      this._labels = new Set(saved.labels || []);
      this._count = saved.count ?? null;
    } catch (e) {
      /* ingen lagring tilgængelig */
    }
  }

  _save() {
    try {
      localStorage.setItem(this._key, JSON.stringify({ labels: [...this._labels], count: this._count }));
    } catch (e) {
      /* ingen lagring tilgængelig */
    }
  }

  _resetLabels() {
    if (!this._labels.size) return;
    this._labels.clear();
    this._save();
  }

  _onTools(ev) {
    const lbl = ev.target.closest(".lbl");
    const cnt = ev.target.closest(".count button");
    if (lbl) {
      const name = lbl.dataset.label;
      this._labels.has(name) ? this._labels.delete(name) : this._labels.add(name);
    } else if (cnt) {
      this._count = cnt.dataset.count === "all" ? "all" : Number(cnt.dataset.count);
    } else return;
    this._open.clear();
    this._save();
    this._renderTools();
    this._renderBody();
  }

  /* Tilbud efter mærker og evt. én pr. kæde, før antallet skæres til */
  _filtered() {
    const a = this._attrs;
    let list = a.offers || [];
    if (this._labels.size) list = list.filter((o) => [...this._labels].every((l) => (o.labels || []).includes(l)));
    if (a.one_per_chain) {
      const seen = new Set();
      list = list.filter((o) => !seen.has(o.chain) && seen.add(o.chain));
    }
    return list;
  }

  /* Mærker der skiller tilbuddene ad (ikke dem alle tilbud har) */
  _labelCounts() {
    const offers = this._attrs.offers || [];
    const counts = new Map();
    for (const o of offers) for (const l of o.labels || []) counts.set(l, (counts.get(l) || 0) + 1);
    for (const l of this._labels) if (!counts.has(l)) counts.set(l, 0);
    return [...counts]
      .filter(([l, n]) => n < offers.length || this._labels.has(l))
      .sort((x, y) => y[1] - x[1])
      .slice(0, 8);
  }

  get _limit() {
    return this._count === "all" ? Infinity : this._count || this._config.max_rows;
  }

  _renderTools() {
    const box = this.shadowRoot.querySelector(".tools");
    const a = this._attrs;
    if (a.mode === "search" && !a.query) {
      box.innerHTML = "";
      return;
    }
    const labels = this._labelCounts();
    const total = this._filtered().length;
    const steps = [5, 10, 20].filter((n) => n < total);
    const current = this._count === "all" ? "all" : String(this._count || this._config.max_rows);
    const counter =
      total > 5
        ? `<div class="count"><span>Vis</span>${steps
            .map((n) => `<button type="button" class="${current === String(n) ? "on" : ""}" data-count="${n}">${n}</button>`)
            .join("")}<button type="button" class="${current === "all" ? "on" : ""}" data-count="all">Alle ${total}</button></div>`
        : "";
    const chips = labels
      .map(
        ([l, n]) =>
          `<button type="button" class="lbl ${this._labels.has(l) ? "on" : ""}" data-label="${esc(l)}"><span class="box">${svg("check")}</span>${esc(l)} <b>${n}</b></button>`
      )
      .join("");
    box.innerHTML = chips || counter ? `<div class="labels">${chips}</div>${counter}` : "";
  }

  _onCategory(ev) {
    const btn = ev.target.closest(".cat");
    const entity = this._attrs.category_entity;
    if (!btn || !entity) return;
    this._open.clear();
    this._hass.callService("select", "select_option", { entity_id: entity, option: btn.dataset.value });
  }

  _onBodyClick(ev) {
    const paper = ev.target.closest(".chip.paper");
    if (paper) {
      ev.stopPropagation();
      const id = paper.dataset.id;
      this._open.has(id) ? this._open.delete(id) : this._open.add(id);
      this._renderBody();
      return;
    }
    if (ev.target.closest(".flyer")) return;
    const row = ev.target.closest(".row");
    if (row) window.open(row.dataset.url, "_blank", "noopener");
  }

  _update() {
    const search = this._attrs.mode === "search";
    if (this._built !== (search ? "search" : "product")) this._build(search);

    const a = this._attrs;
    if (search) {
      if (this._lastQuery !== undefined && a.query !== this._lastQuery) this._resetLabels();
      this._lastQuery = a.query;
    }
    if (this._pending !== null && a.query === this._pending) this._pending = null;
    const input = this.shadowRoot.querySelector(".search input");
    if (input && this._pending === null && this.shadowRoot.activeElement !== input) input.value = a.query || "";
    this._syncSearchState();

    this._renderHero(search);
    this._renderCategories(search);
    this._renderTools();
    this._renderBody();
    this._renderFoot();
  }

  _renderHero(search) {
    const c = this._config;
    const a = this._attrs;
    const root = this.shadowRoot;
    const title = root.querySelector(".title");
    if (!title) return;
    const unit = a.unit || "ltr";
    const query = search && a.query ? a.query : "";
    title.textContent = c.title || query || a.friendly_name || "Tilbud";
    const parts = [c.subtitle ?? (UNIT_TITLE[unit] || "Billigste pris")];
    if (c.subtitle == null && search && a.category) parts.push(a.category);
    if (c.subtitle == null && a.include_deposit) parts.push("inkl. pant");
    root.querySelector(".sub").textContent = parts.join(" · ");
    const art = c.image ? `<img src="${esc(c.image)}" alt="">` : unit === "ltr" ? CAN : TAG;
    const holder = root.querySelector(".art");
    if (holder.dataset.art !== art) {
      holder.innerHTML = art;
      holder.dataset.art = art;
    }
  }

  _renderCategories(search) {
    const a = this._attrs;
    const box = this.shadowRoot.querySelector(".cats");
    const cats = a.categories || [];
    if (!search || !a.query || cats.length < 2) {
      box.innerHTML = "";
      return;
    }
    const active = a.category_choice === "alle" ? "alle" : a.category;
    const total = cats.reduce((sum, x) => sum + x.count, 0);
    box.innerHTML =
      cats
        .slice(0, 10)
        .map(
          (x) =>
            `<button type="button" class="cat ${x.name === active ? "on" : ""}" data-value="${esc(x.name)}">${esc(x.name)} <b>${x.count}</b></button>`
        )
        .join("") +
      `<button type="button" class="cat ${active === "alle" ? "on" : ""}" data-value="alle">Alle <b>${total}</b></button>`;
  }

  _row(o, i, ctx) {
    const top = i === 0;
    const [one] = packWords(o);
    const each = o.units > 1 && PACKAGE[o.package] ? `${kr(o.price / o.units)} kr pr. ${one}${o.deposit_included ? " inkl. pant" : ""}` : "";
    const pant = o.deposit && !o.deposit_included ? `<span class="pant"> + pant</span>` : "";
    const diff = Number(o.unit_price) - ctx.best;
    const pct = Math.max(10, Math.min(100, Math.round((ctx.best / Number(o.unit_price)) * 100)));
    const open = this._open.has(String(o.id));

    const chips = [`<span class="chip">${svg("calendar")}${esc(dateRange(o.start, o.end))}</span>`];
    if (o.start > ctx.today) chips.push(`<span class="chip soon">Starter snart</span>`);
    else if (o.end === ctx.today) chips.push(`<span class="chip last">Sidste dag</span>`);
    if (o.limit) chips.push(`<span class="chip limit">${svg("cart")}Maks. ${esc(o.limit)} pr. kunde</span>`);
    for (const l of o.labels || []) if (ctx.labels.has(l)) chips.push(`<span class="chip label">${svg(/økolog/i.test(l) ? "leaf" : "check")}${esc(l)}</span>`);
    if (o.deposit_included) chips.push(`<span class="chip">Inkl. ${kr(o.deposit)} kr pant</span>`);
    for (const note of o.notes || []) chips.push(`<span class="chip">${svg("info")}${esc(note)}</span>`);
    if (o.image) chips.push(`<button type="button" class="chip paper ${open ? "on" : ""}" data-id="${esc(o.id)}">${svg("paper")}${open ? "Skjul avis" : "Se i avisen"}</button>`);

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
        ${ctx.showNames ? `<div class="name">${esc(o.name)}</div>` : ""}
        <div class="pack">${esc(packText(o))}<span class="dot">•</span><span class="total">${kr(o.price)} kr</span>${pant}</div>
        ${each ? `<div class="each">${esc(each)}</div>` : ""}
      </div>
      <div class="price">
        <div class="unit-price">${kr(o.unit_price)}<small>${ctx.short}</small></div>
        <div class="meter"><i style="width:${pct}%"></i></div>
        ${top ? "" : `<div class="diff">${diff > 0.004 ? `+${kr(diff)} ${ctx.short}` : "Samme pris"}</div>`}
      </div>
      <div class="chips">${chips.join("")}</div>
      ${
        open
          ? `<div class="flyer"><div class="flyer-frame">
              <img src="${esc(o.image)}" referrerpolicy="no-referrer" alt="Udsnit af tilbudsavisen">
              <a href="${esc(o.url)}" target="_blank" rel="noopener">${svg("open")}Åbn tilbuddet</a>
            </div></div>`
          : ""
      }
    </div>`;
  }

  _renderBody() {
    const c = this._config;
    const a = this._attrs;
    const st = this._hass.states[c.entity];
    const body = this.shadowRoot.querySelector(".body");
    const all = this._filtered();
    const offers = all.slice(0, this._limit);

    if (!st) {
      body.innerHTML = `<div class="empty">Entiteten ${esc(c.entity)} findes ikke</div>`;
      return;
    }
    if (a.mode === "search" && !a.query) {
      body.innerHTML = `<div class="empty">Skriv en vare i søgefeltet</div>`;
      return;
    }
    if (!offers.length) {
      const why = this._labels.size ? `med ${[...this._labels].map(esc).join(" og ")}` : a.mode === "search" ? `på “${esc(a.query)}”` : "";
      body.innerHTML = `<div class="empty">Ingen tilbud ${why} lige nu</div>`;
      return;
    }

    const unit = a.unit || "ltr";
    const ctx = {
      best: Number(offers[0].unit_price),
      short: UNIT_SHORT[unit] ? `kr/${UNIT_SHORT[unit]}` : "kr",
      today: isoToday(),
      showNames: new Set(offers.map((o) => o.name)).size > 1,
      labels: new Set(this._labelCounts().map(([l]) => l)),
    };
    body.innerHTML = `<div class="list">${offers.map((o, i) => this._row(o, i, ctx)).join("")}</div>`;
    body.querySelectorAll(".logo img").forEach((img) => img.addEventListener("error", () => img.remove()));
  }

  _renderFoot() {
    const foot = this.shadowRoot.querySelector(".foot");
    const a = this._attrs;
    if (!this._config.show_updated || !a.last_fetch) {
      foot.textContent = "";
      return;
    }
    const d = new Date(a.last_fetch);
    const count = a.total_offers ? `${a.total_offers} tilbud fundet · ` : "";
    foot.textContent = `${count}Opdateret ${d.toLocaleDateString("da-DK")} kl. ${d.toLocaleTimeString("da-DK", { hour: "2-digit", minute: "2-digit" })}`;
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
  { name: "max_rows", selector: { number: { min: 1, max: 50, mode: "box" } } },
  { name: "show_header", selector: { boolean: {} } },
  { name: "show_updated", selector: { boolean: {} } },
];

const EDITOR_LABELS = {
  entity: "Sensor",
  title: "Titel",
  subtitle: "Undertitel",
  theme: "Farvetema",
  image: "Billede-URL (valgfri, erstatter ikonet)",
  max_rows: "Antal rækker",
  show_header: "Vis topbanner (og søgefelt)",
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
    description: "Billigste tilbud fra tilbudsugen.dk – også med søgefelt",
    preview: true,
  });
}

console.info(`%c TILBUDSJAGT-CARD %c v${TJ_VERSION} `, "background:#2f7cf6;color:#fff;font-weight:700", "background:#222;color:#fff");
