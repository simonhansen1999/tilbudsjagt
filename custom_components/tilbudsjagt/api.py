"""Henter og fortolker tilbud fra tilbudsugen.dk."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import re
from typing import Any

import aiohttp

from .const import BASE_URL, CHAIN_LOGOS, UNIT_ALL, USER_AGENT

_NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.DOTALL
)


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
    size: float
    start: str
    end: str
    border_shop: bool

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
        return Offer(
            id=str(item["id"]),
            chain=(item.get("chain") or {}).get("name") or "",
            name=", ".join(part for part in (brand, product) if part),
            price=float(item.get("price") or 0),
            unit_price=float(item.get("pricePerFullUnitOfQuantityType") or 0),
            unit=item.get("quantityType") or "",
            units=int(item.get("units") or 1),
            size=float(item.get("quantity") or 0),
            start=str(item.get("startDate") or "")[:10],
            end=str(item.get("endDate") or "")[:10],
            border_shop=bool(item.get("isBorderShop")),
        )
    except (KeyError, TypeError, ValueError):
        return None


def _words(text: str) -> list[str]:
    return [w.strip().lower() for w in text.split(",") if w.strip()]


def filter_offers(offers: list[Offer], opts: dict[str, Any], today: str) -> list[Offer]:
    """Filtrér, sortér efter enhedspris og begræns antallet."""
    must = _words(opts["name_contains"])
    exclude = _words(opts["name_excludes"])
    chains = [c.lower() for c in opts["exclude_chains"]]
    unit = opts["unit"]

    result = [
        o
        for o in offers
        if o.unit_price > 0
        and (unit == UNIT_ALL or o.unit == unit)
        and (opts["include_border"] or not o.border_shop)
        and (not o.end or o.end >= today)
        and o.units >= opts["min_units"]
        and all(w in o.name.lower() for w in must)
        and not any(w in o.name.lower() for w in exclude)
        and not any(c in o.chain.lower() for c in chains)
    ]
    result.sort(key=lambda o: (o.unit_price, o.price))

    if opts["one_per_chain"]:
        seen: set[str] = set()
        result = [o for o in result if not (o.chain in seen or seen.add(o.chain))]

    return result[: int(opts["max_results"])]
