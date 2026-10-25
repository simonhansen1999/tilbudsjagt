"""Henter og fortolker tilbud fra tilbudsugen.dk."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json
import re
from typing import Any

import aiohttp

from .const import BASE_URL, CHAIN_LOGOS, UNIT_ALL, USER_AGENT

_NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.DOTALL
)
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
    price: float
    unit_price: float
    unit: str
    units: int
    package: str
    size: float
    start: str
    end: str
    border_shop: bool
    limit: int | None = None
    notes: tuple[str, ...] = ()
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


def normalize_search(text: str) -> str:
    """Gør 'Pepsi Max' eller en tilbudsugen-URL til en slug som 'pepsi-max'."""
    text = text.strip()
    if "/offer/" in text:
        text = text.split("/offer/", 1)[1].split("?")[0].strip("/")
    return re.sub(r"\s+", "-", text.lower())


async def async_fetch_offers(session: aiohttp.ClientSession, slug: str) -> list[Offer]:
    """Hent alle tilbud for en søgning."""
    try:
        async with session.get(
            f"{BASE_URL}/offer/{slug}",
            headers={"User-Agent": USER_AGENT},
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            resp.raise_for_status()
            html = await resp.text()
    except (aiohttp.ClientError, TimeoutError) as err:
        raise TilbudsugenError(f"Kunne ikke hente siden: {err}") from err

    match = _NEXT_DATA_RE.search(html)
    if not match:
        raise TilbudsugenError("Fandt ikke __NEXT_DATA__ på siden")

    try:
        data = json.loads(match.group(1))
        items = data["props"]["pageProps"]["data"]["pageOfOrganicProductOffers"]["items"]
    except (ValueError, KeyError, TypeError) as err:
        raise TilbudsugenError(f"Uventet dataformat: {err}") from err

    return [offer for item in items if (offer := _parse(item))]


def _parse(item: dict[str, Any]) -> Offer | None:
    try:
        brand = (item.get("brand") or {}).get("name") or ""
        product = (item.get("productName") or {}).get("productName") or ""
        limit, notes = _parse_notes(item.get("definedDescription") or [])
        return Offer(
            id=str(item["id"]),
            chain=(item.get("chain") or {}).get("name") or "",
            name=", ".join(part for part in (brand, product) if part),
            price=float(item.get("price") or 0),
            unit_price=float(item.get("pricePerFullUnitOfQuantityType") or 0),
            unit=(item.get("quantityType") or "").rstrip("."),
            units=int(item.get("units") or 1),
            package=(item.get("unitType") or "").rstrip("."),
            size=float(item.get("quantity") or 0),
            start=str(item.get("startDate") or "")[:10],
            end=str(item.get("endDate") or "")[:10],
            border_shop=bool(item.get("isBorderShop")),
            limit=limit,
            notes=notes,
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
    return replace(
        offer, price=price, unit_price=round(price / volume, 2), deposit_included=True
    )


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


def _words(text: str) -> list[str]:
    return [w.strip().lower() for w in text.split(",") if w.strip()]


def match_offers(offers: list[Offer], opts: dict[str, Any], today: str) -> list[Offer]:
    """Tilbud der opfylder filtrene, sorteret efter enhedspris."""
    must = _words(opts["name_contains"])
    exclude = _words(opts["name_excludes"])
    chains = [c.lower() for c in opts["exclude_chains"]]
    unit = opts["unit"]
    package = opts["package"]
    if opts["include_deposit"]:
        offers = [with_deposit(o) for o in offers]

    result = [
        o
        for o in offers
        if o.unit_price > 0
        and (unit == UNIT_ALL or o.unit == unit)
        and (package == UNIT_ALL or o.package == package)
        and (opts["include_border"] or not o.border_shop)
        and (not o.end or o.end >= today)
        and o.units >= opts["min_units"]
        and all(w in o.name.lower() for w in must)
        and not any(w in o.name.lower() for w in exclude)
        and not any(c in o.chain.lower() for c in chains)
    ]
    result.sort(key=lambda o: (o.unit_price, o.price))
    return result


def cheapest_per_chain(offers: list[Offer]) -> list[Offer]:
    """Billigste tilbud pr. kæde. Forventer en sorteret liste."""
    seen: set[str] = set()
    return [o for o in offers if not (o.chain in seen or seen.add(o.chain))]


def top_offers(matched: list[Offer], opts: dict[str, Any]) -> list[Offer]:
    """De tilbud der vises på kortet."""
    result = cheapest_per_chain(matched) if opts["one_per_chain"] else matched
    return result[: int(opts["max_results"])]
