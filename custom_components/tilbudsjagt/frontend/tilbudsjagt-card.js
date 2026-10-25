/* Tilbudsjagt card – følger med integrationen, ingen ekstra installation. */
const TJ_VERSION = "__VERSION__"; // sættes af release-workflowet

const THEMES = {
  blue: { hero: "linear-gradient(120deg,#0b2a6b 0%,#0d47a1 55%,#d32f2f 140%)", top: "linear-gradient(135deg,#0d47a1 0%,#1976d2 100%)", glow: "rgba(25,118,210,.55)", bar: "#4fc3f7" },
  red: { hero: "linear-gradient(120deg,#4a0710 0%,#a3101d 55%,#e53935 120%)", top: "linear-gradient(135deg,#8e0d1c 0%,#d0182b 100%)", glow: "rgba(208,24,43,.55)", bar: "#ffd54f" },
  green: { hero: "linear-gradient(120deg,#0b3d1f 0%,#1b7a3a 60%,#9ccc65 140%)", top: "linear-gradient(135deg,#1b5e20 0%,#2e9e48 100%)", glow: "rgba(46,158,72,.5)", bar: "#c5e1a5" },
  purple: { hero: "linear-gradient(120deg,#2a0b4d 0%,#5e2ca5 60%,#ec407a 140%)", top: "linear-gradient(135deg,#4a148c 0%,#7b3fd0 100%)", glow: "rgba(123,63,208,.5)", bar: "#f48fb1" },
  orange: { hero: "linear-gradient(120deg,#5d2600 0%,#d35400 60%,#ffb300 140%)", top: "linear-gradient(135deg,#bf4a00 0%,#f57c00 100%)", glow: "rgba(245,124,0,.5)", bar: "#ffe082" },
};

const UNIT_LABEL = { "ltr.": "liter", "kg.": "kg", "stk.": "stk." };
const UNIT_SHORT = { "ltr.": "l", "kg.": "kg", "stk.": "stk" };

const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const kr = (n) => (Number(n) || 0).toFixed(2).replace(".", ",");
const ddmm = (s) => (s ? `${s.slice(8, 10)}.${s.slice(5, 7)}` : "");
const localToday = () => {
  const t = new Date();
  return `${t.getFullYear()}-${String(t.getMonth() + 1).padStart(2, "0")}-${String(t.getDate()).padStart(2, "0")}`;
};

function packText(o) {
  const n = Number(o.size) || 0;
  let size;
  if (o.unit === "ltr.") size = n < 1 ? `${Math.round(n * 100)} cl` : `${String(n).replace(".", ",")} l`;
  else if (o.unit === "kg.") size = n < 1 ? `${Math.round(n * 1000)} g` : `${String(n).replace(".", ",")} kg`;
  else size = `${String(n).replace(".", ",")} stk.`;
  return o.units > 1 ? `${o.units} × ${size}` : size;
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

const CAN_SVG = `<svg width="50" height="82" viewBox="0 0 60 100" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="tjb" x1="0" x2="1"><stop offset="0" stop-color="#05070d"/><stop offset=".45" stop-color="#2a3246"/><stop offset="1" stop-color="#05070d"/></linearGradient><linearGradient id="tjm" x1="0" x2="1"><stop offset="0" stop-color="#8a93a6"/><stop offset=".5" stop-color="#f1f4fa"/><stop offset="1" stop-color="#8a93a6"/></linearGradient></defs><path d="M8 12 L8 88 Q8 96 30 96 Q52 96 52 88 L52 12 Q52 18 30 18 Q8 18 8 12 Z" fill="url(#tjb)"/><ellipse cx="30" cy="12" rx="22" ry="5.5" fill="url(#tjm)"/><ellipse cx="30" cy="12" rx="16" ry="3.2" fill="#cfd5e2"/><path d="M8 42 Q30 50 52 42 L52 62 Q30 70 8 62 Z" fill="var(--tj-bar)"/><rect x="13" y="22" width="4" height="68" rx="2" fill="#fff" opacity=".13"/></svg>`;

const STYLE = `
  :host { display:block; }
  ha-card { background:none; box-shadow:none; border:none; display:flex; flex-direction:column; gap:8px; color:#fff; }
  .hero { display:grid; grid-template-columns:1fr auto; align-items:center; padding:14px 18px; border-radius:16px; background:var(--tj-hero); box-shadow:0 4px 18px var(--tj-glow); }
  .kicker { font-size:11px; letter-spacing:3px; opacity:.8; text-transform:uppercase; }
  .title { font-size:28px; font-weight:800; letter-spacing:1px; line-height:1.15; text-transform:uppercase; }
  .sub { font-size:12px; opacity:.85; margin-top:2px; }
  .art { transform:rotate(10deg); filter:drop-shadow(0 4px 6px rgba(0,0,0,.55)); }
  .art img { max-width:64px; max-height:82px; object-fit:contain; }
  .row { display:grid; grid-template-columns:22px 46px 1fr auto; align-items:center; column-gap:10px; padding:10px 14px; border-radius:14px; background:linear-gradient(135deg,#252b38 0%,#1b1f29 100%); border:1px solid rgba(255,255,255,.14); cursor:pointer; }
  .row.first { background:var(--tj-top); box-shadow:0 0 18px var(--tj-glow); }
  .rank { width:22px; height:22px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:800; color:#222; background:#9aa3b5; }
  .rank.r1 { background:linear-gradient(135deg,#ffe082,#ffb300); }
  .rank.r2 { background:linear-gradient(135deg,#eceff1,#90a4ae); }
  .rank.r3 { background:linear-gradient(135deg,#ffcc80,#a1662f); }
  .logo { width:46px; height:46px; border-radius:12px; background:#fff; position:relative; overflow:hidden; display:flex; align-items:center; justify-content:center; border:1px solid rgba(255,255,255,.25); }
  .first .logo { border:2px solid #ffd54f; box-shadow:0 0 10px rgba(255,213,79,.6); }
  .logo span { position:absolute; color:#333; font-weight:800; font-size:15px; }
  .logo img { position:relative; width:100%; height:100%; object-fit:contain; background:#fff; padding:3px; box-sizing:border-box; }
  .chain { font-weight:700; font-size:16px; line-height:1.2; }
  .prod { opacity:.75; font-size:12px; margin-top:2px; }
  .dates { font-size:11px; margin-top:3px; opacity:.9; }
  .tag { border-radius:6px; padding:0 6px; margin-left:4px; font-weight:700; color:#111; }
  .soon { background:#ffb300; }
  .last { background:#ff8a80; }
  .price { text-align:right; }
  .big { font-size:26px; font-weight:800; line-height:1; }
  .unit { font-size:12px; opacity:.75; }
  .track { margin:6px 0 0 auto; height:4px; width:96px; border-radius:2px; background:rgba(255,255,255,.18); }
  .fill { height:4px; border-radius:2px; background:var(--tj-bar); }
  .empty { padding:14px; border-radius:14px; background:#1b1f29; opacity:.7; text-align:center; }
  .foot { font-size:11px; opacity:.6; padding:0 4px; color:var(--primary-text-color); }
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
    const sig = st ? `${st.last_updated}|${localToday()}` : "missing";
    if (sig === this._sig) return;
    this._sig = sig;
    this._render();
  }

  getCardSize() {
    return 2 + (this._config?.max_rows ?? 5);
  }

  getGridOptions() {
    return { columns: 12, min_columns: 6 };
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

  _render() {
    const c = this._config;
    const theme = THEMES[c.theme] || THEMES.blue;
    const st = this._hass.states[c.entity];
    const a = st?.attributes || {};
    const offers = (a.offers || []).slice(0, c.max_rows);
    const unit = a.unit || "ltr.";
    const short = UNIT_SHORT[unit] ? `kr/${UNIT_SHORT[unit]}` : "kr";
    const today = localToday();
    const min = offers.length ? Number(offers[0].unit_price) : 0;

    const header = c.show_header
      ? `<div class="hero">
          <div>
            <div class="kicker">${esc(c.kicker ?? "Tilbudsjagt")}</div>
            <div class="title">${esc(c.title || st?.attributes.friendly_name || "Tilbud")}</div>
            <div class="sub">${esc(c.subtitle ?? `Billigste tilbud pr. ${UNIT_LABEL[unit] || "stk."}`)}</div>
          </div>
          <div class="art">${c.image ? `<img src="${esc(c.image)}" alt="">` : CAN_SVG}</div>
        </div>`
      : "";

    const rows = offers.length
      ? offers
          .map((o, i) => {
            const pct = Math.max(8, Math.min(100, Math.round((min / Number(o.unit_price)) * 100)));
            const tag =
              o.start > today
                ? `<span class="tag soon">starter snart</span>`
                : o.end === today
                ? `<span class="tag last">sidste dag</span>`
                : "";
            return `<div class="row ${i === 0 ? "first" : ""}" data-url="${esc(o.url)}">
              <div class="rank ${i < 3 ? `r${i + 1}` : ""}">${i + 1}</div>
              <div class="logo"><span>${esc(initials(o.chain))}</span><img src="${esc(o.logo)}" referrerpolicy="no-referrer" alt=""></div>
              <div>
                <div class="chain">${esc(o.chain)}</div>
                <div class="prod">${esc(o.name)} · ${esc(packText(o))} = ${kr(o.price)} kr</div>
                <div class="dates">${ddmm(o.start)}–${ddmm(o.end)}${tag}</div>
              </div>
              <div class="price">
                <span class="big">${kr(o.unit_price)}</span><span class="unit"> ${short}</span>
                <div class="track"><div class="fill" style="width:${pct}%"></div></div>
              </div>
            </div>`;
          })
          .join("")
      : `<div class="empty">${st ? "Ingen tilbud lige nu" : `Entiteten ${esc(c.entity)} findes ikke`}</div>`;

    let foot = "";
    if (c.show_updated && a.last_fetch) {
      const d = new Date(a.last_fetch);
      foot = `<div class="foot">Sidst opdateret: ${d.toLocaleDateString("da-DK")} kl. ${d.toLocaleTimeString("da-DK", { hour: "2-digit", minute: "2-digit" })}</div>`;
    }

    this.shadowRoot.innerHTML = `<style>${STYLE}</style>
      <ha-card style="--tj-hero:${theme.hero};--tj-top:${theme.top};--tj-glow:${theme.glow};--tj-bar:${theme.bar}">
        ${header}${rows}${foot}
      </ha-card>`;

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
  image: "Billede-URL (valgfri)",
  max_rows: "Antal rækker",
  show_header: "Vis topbanner",
  show_updated: "Vis 'sidst opdateret'",
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

console.info(`%c TILBUDSJAGT-CARD %c v${TJ_VERSION} `, "background:#0d47a1;color:#fff;font-weight:700", "background:#222;color:#fff");
