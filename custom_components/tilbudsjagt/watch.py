"""Hjælpere til prisovervågning: enheder og beskedtekst."""

from __future__ import annotations

from homeassistant.core import HomeAssistant

from .api import Offer

# notify-tjenester der ikke er en enhed
_NOT_DEVICES = {"notify", "persistent_notification", "send_message"}
_UNITS = {"ltr": "l", "kg": "kg", "stk": "stk"}
_MONTHS = ["jan.", "feb.", "mar.", "apr.", "maj", "jun.", "jul.", "aug.", "sep.", "okt.", "nov.", "dec."]
_PACKAGES = {"ds": ("dåse", "dåser"), "fl": ("flaske", "flasker")}


def notify_targets(hass: HomeAssistant) -> list[str]:
    """Enheder der kan få besked, fx 'mobile_app_simons_iphone'."""
    return sorted(s for s in hass.services.async_services_for_domain("notify") if s not in _NOT_DEVICES)


def kr(value: float) -> str:
    return f"{value:.2f}".replace(".", ",")


def _dates(start: str, end: str) -> str:
    try:
        _, sm, sd = (int(x) for x in start.split("-"))
        _, em, ed = (int(x) for x in end.split("-"))
    except ValueError:
        return ""
    if sm == em:
        return f"{sd}.–{ed}. {_MONTHS[em - 1]}"
    return f"{sd}. {_MONTHS[sm - 1]} – {ed}. {_MONTHS[em - 1]}"


def _pack(offer: Offer) -> str:
    size = offer.size
    if offer.unit == "ltr":
        amount = f"{round(size * 100)} cl" if size < 1 else f"{kr(size).rstrip('0').rstrip(',')} l"
    elif offer.unit == "kg":
        amount = f"{round(size * 1000)} g" if size < 1 else f"{kr(size).rstrip('0').rstrip(',')} kg"
    else:
        amount = f"{size:g} stk."
    one, many = _PACKAGES.get(offer.package, ("", ""))
    if not one:
        return f"{offer.units} × {amount}" if offer.units > 1 else amount
    return f"{offer.units} {many} à {amount}" if offer.units > 1 else f"1 {one} à {amount}"


def describe(offer: Offer) -> str:
    """Én linje om tilbuddet, fx 'Meny: 6,63 kr/l – 1 flaske à 1,5 l for 9,95 kr (23.–29. okt.)'."""
    unit = _UNITS.get(offer.unit, "stk")
    text = f"{offer.chain}: {kr(offer.unit_price)} kr/{unit} – {_pack(offer)} for {kr(offer.price)} kr"
    if offer.limit:
        text += f", maks. {offer.limit} pr. kunde"
    dates = _dates(offer.start, offer.end)
    return f"{text} ({dates})" if dates else text
