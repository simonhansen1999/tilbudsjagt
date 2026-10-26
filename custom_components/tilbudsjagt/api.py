"""Henter og fortolker tilbud fra tilbudsugen.dk."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field, replace
import json
import re
from typing import Any

import aiohttp

from .const import ALL, AUTO, BASE_URL, CHAIN_LOGOS, MAX_PAGES, USER_AGENT

_NEXT_DATA_RE = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.DOTALL)
_LIMIT_RE = re.compile(r"\bma(?:ks|x)\.?\s*(\d+)", re.IGNORECASE)
_NOTE_NAMES = {"fl. var.": "Flere varianter"}


class TilbudsugenError(Exception):
    """Siden kunne ikke hentes eller læses."""


@dataclass(frozen=True)
class Offer:
    """Et enkelt tilbud."""

    id: str
    chain: str
    name: str
    category: str
    price: float
    unit_price: float
    unit: str
    units: int
    package: str
    size: float
    start: str
    end: str
    border_shop: bool
    image: str = ""
    limit: int | None = None
    notes: tuple[str, ...] = ()
    labels: tuple[str, ...] = ()
    deposit: float = 0.0
    deposit_included: bool = False

    @property
    def url(self) -> str:
        return f"{BASE_URL}/single/{self.id}"

    @property
    def logo(self) -> str:
        key = self.chain.lower()
        file = CHAIN_LOGOS.get(key)
        if file is None:
            slug = key.replace("ø", "oe").replace("å", "aa").replace("æ", "ae")
            slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
            file = f"{slug}.png"
        return f"{BASE_URL}/chains/{file}"

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("border_shop")
        data["url"] = self.url
        data["logo"] = self.logo
        return data


@dataclass
class OfferPage:
    """Alle tilbud for en søgning."""

    offers: list[Offer] = field(default_factory=list)
    chains: list[str] = field(default_factory=list)
    total: int = 0


@dataclass
class Selection:
    """Resultatet af filtreringen."""

    matched: list[Offer]
    category: str | None
    unit: str
    categories: list[tuple[str, int]]


def normalize_search(text: str) -> str:
    """Gør 'Pepsi Max' eller en tilbudsugen-URL til en slug som 'pepsi-max'."""
    text = text.strip()
    if "/offer/" in text:
        text = text.split("/offer/", 1)[1].split("?")[0].strip("/")
    return re.sub(r"\s+", "-", text.lower())


async def _async_get_page(session: aiohttp.ClientSession, slug: str, page: int) -> dict[str, Any] | None:
    url = f"{BASE_URL}/offer/{slug}" + (f"?page={page}" if page > 1 else "")
    async with session.get(
        url, headers={"User-Agent": USER_AGENT}, timeout=aiohttp.ClientTimeout(total=30)
    ) as resp:
        if resp.status == 404:
            return None
        resp.raise_for_status()
        html = await resp.text()

    match = _NEXT_DATA_RE.search(html)
    if not match:
        raise TilbudsugenError("Fandt ikke __NEXT_DATA__ på siden")
    try:
        return json.loads(match.group(1))["props"]["pageProps"]["data"]
    except (ValueError, KeyError, TypeError) as err:
        raise TilbudsugenError(f"Uventet dataformat: {err}") from err


async def async_fetch_offers(session: aiohttp.ClientSession, slug: str) -> OfferPage:
    """Hent alle tilbud for en søgning, også fra de næste sider."""
    try:
        data = await _async_get_page(session, slug, 1)
    except (aiohttp.ClientError, TimeoutError) as err:
        raise TilbudsugenError(f"Kunne ikke hente siden: {err}") from err
    if data is None:
        return OfferPage()
    return await _async_collect(session, slug, data)


async def _async_collect(session: aiohttp.ClientSession, slug: str, data: dict[str, Any]) -> OfferPage:
    try:
        listing = data["pageOfOrganicProductOffers"]
    except (KeyError, TypeError) as err:
        raise TilbudsugenError(f"Uventet dataformat: {err}") from err

    items = list(listing.get("items") or [])
    last = min(int(listing.get("lastValidPageNumber") or 1), MAX_PAGES)
    for page in range(2, last + 1):
        try:
            more = await _async_get_page(session, slug, page)
        except (aiohttp.ClientError, TimeoutError, TilbudsugenError):
            break
        if not more:
            break
        items.extend((more.get("pageOfOrganicProductOffers") or {}).get("items") or [])

    return parse_listing(data, items)


def parse_listing(data: dict[str, Any], items: list[dict[str, Any]]) -> OfferPage:
    """Lav en OfferPage ud fra sidens data og alle hentede tilbud."""
    seen: set[str] = set()
    offers: list[Offer] = []
    for item in items:
        offer = _parse(item)
        if offer and offer.id not in seen:
            seen.add(offer.id)
            offers.append(offer)

    filter_chains = ((data.get("optionsForFilters") or {}).get("chains")) or []
    chains = {c.get("text") for c in filter_chains if c.get("text")} | {o.chain for o in offers if o.chain}
    listing = data.get("pageOfOrganicProductOffers") or {}
    return OfferPage(
        offers=offers,
        chains=sorted(chains),
        total=int(listing.get("totalNumberOfItems") or len(offers)),
    )


def _parse(item: dict[str, Any]) -> Offer | None:
    try:
        brand = (item.get("brand") or {}).get("name") or ""
        product = (item.get("productName") or {}).get("productName") or ""
        category = (((item.get("productVariant") or {}).get("category")) or {}).get("name") or ""
        limit, notes = _parse_notes(item.get("definedDescription") or [])
        return Offer(
            id=str(item["id"]),
            chain=(item.get("chain") or {}).get("name") or "",
            name=", ".join(part for part in (brand, product) if part),
            category=category,
            price=float(item.get("price") or 0),
            unit_price=float(item.get("pricePerFullUnitOfQuantityType") or 0),
            unit=(item.get("quantityType") or "").rstrip("."),
            units=int(item.get("units") or 1),
            package=(item.get("unitType") or "").rstrip("."),
            size=float(item.get("quantity") or 0),
            start=str(item.get("startDate") or "")[:10],
            end=str(item.get("endDate") or "")[:10],
            border_shop=bool(item.get("isBorderShop")),
            image=item.get("imageUrl") or "",
            limit=limit,
            notes=notes,
            labels=tuple(
                n["name"] for n in item.get("specificNote") or [] if isinstance(n, dict) and n.get("name")
            ),
            deposit=_deposit(item),
        )
    except (KeyError, TypeError, ValueError):
        return None


def _deposit(item: dict[str, Any]) -> float:
    """Samlet pant for tilbuddet ud fra emballage og størrelse.

    Pant A 1 kr: dåser og glasflasker under 1 l.
    Pant B 1,50 kr: plastflasker under 1 l.
    Pant C 3 kr: flasker og dåser på 1 l eller mere.
    Materialet står ikke i dataene, så flasker til og med 33 cl regnes som glas
    og større flasker under 1 l som plast.
    """
    package = (item.get("unitType") or "").rstrip(".")
    if (item.get("quantityType") or "").rstrip(".") != "ltr" or package not in ("ds", "fl"):
        return 0.0
    size = float(item.get("quantity") or 0)
    if size >= 1:
        each = 3.0
    elif package == "ds" or size <= 0.33:
        each = 1.0
    else:
        each = 1.5
    return each * int(item.get("units") or 1)


def with_deposit(offer: Offer) -> Offer:
    """Tilbuddet med pant lagt oven i pris og enhedspris."""
    volume = offer.units * offer.size
    if not offer.deposit or not volume:
        return offer
    price = offer.price + offer.deposit
    return replace(offer, price=price, unit_price=round(price / volume, 2), deposit_included=True)


def _parse_notes(described: list[dict[str, Any]]) -> tuple[int | None, tuple[str, ...]]:
    """Find en evt. grænse pr. kunde og de øvrige noter."""
    limit: int | None = None
    notes: list[str] = []
    for entry in described:
        value = str((entry or {}).get("value") or "").strip()
        if not value:
            continue
        if match := _LIMIT_RE.search(value):
            limit = int(match.group(1))
        else:
            notes.append(_NOTE_NAMES.get(value.lower(), value))
    return limit, tuple(notes)


def words(text: str, sep: str = ",") -> list[str]:
    """Del tekst op i små ord. Komma for filtre, tom sep for mellemrum."""
    parts = text.split(sep) if sep else text.split()
    return [w.strip().lower() for w in parts if w.strip()]


def _chain_in(chain: str, names: list[str]) -> bool:
    chain = chain.lower()
    return any(n.lower() in chain for n in names)


def _pick_category(offers: list[Offer], query: list[str]) -> str | None:
    """Kategorien som flest tilbud med søgeordene i navnet hører til."""
    hits = [o for o in offers if query and all(w in o.name.lower() for w in query)] or offers
    counts = Counter(o.category for o in hits if o.category)
    return counts.most_common(1)[0][0] if counts else None


def select_offers(
    offers: list[Offer],
    opts: dict[str, Any],
    today: str,
    query: list[str] | None = None,
    category: str | None = None,
) -> Selection:
    """Filtrér og sortér tilbuddene efter brugerens valg."""
    query = query or []
    must = words(opts["name_contains"])
    exclude = words(opts["name_excludes"])
    package = opts["package"]

    base = [
        o
        for o in offers
        if o.unit_price > 0
        and (opts["include_border"] or not o.border_shop)
        and (not o.end or o.end >= today)
        and o.units >= opts["min_units"]
        and (package == ALL or o.package == package)
        and all(w in o.name.lower() for w in must)
        and not any(w in o.name.lower() for w in exclude)
        and all(w in f"{o.name} {o.category}".lower() for w in query)
        and (not opts["include_chains"] or _chain_in(o.chain, opts["include_chains"]))
        and not _chain_in(o.chain, opts["exclude_chains"])
    ]
    categories = Counter(o.category for o in base if o.category).most_common()

    choice = category if category is not None else opts["category"]
    chosen = _pick_category(base, query) if choice == AUTO else (None if choice == ALL else choice)
    if chosen:
        base = [o for o in base if o.category == chosen]

    unit = opts["unit"]
    if unit == AUTO:
        counts = Counter(o.unit for o in base if o.unit)
        unit = counts.most_common(1)[0][0] if counts else ALL
    if unit != ALL:
        base = [o for o in base if o.unit == unit]

    if opts["include_deposit"]:
        base = [with_deposit(o) for o in base]
    base.sort(key=lambda o: (o.unit_price, o.price))
    return Selection(matched=base, category=chosen, unit=unit, categories=categories)


def cheapest_per_chain(offers: list[Offer]) -> list[Offer]:
    """Billigste tilbud pr. kæde. Forventer en sorteret liste."""
    seen: set[str] = set()
    return [o for o in offers if not (o.chain in seen or seen.add(o.chain))]


def top_offers(matched: list[Offer], opts: dict[str, Any]) -> list[Offer]:
    """De tilbud der vises på kortet."""
    result = cheapest_per_chain(matched) if opts["one_per_chain"] else matched
    return result[: int(opts["max_results"])]
