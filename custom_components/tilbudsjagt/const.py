"""Konstanter for Tilbudsjagt."""

DOMAIN = "tilbudsjagt"

BASE_URL = "https://www.tilbudsugen.dk"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
ATTRIBUTION = "Data fra Tilbudsugen.dk"

CONF_SEARCH = "search"
CONF_SLUG = "slug"
CONF_NAME = "name"
CONF_NAME_CONTAINS = "name_contains"
CONF_NAME_EXCLUDES = "name_excludes"
CONF_UNIT = "unit"
CONF_PACKAGE = "package"
CONF_MIN_UNITS = "min_units"
CONF_EXCLUDE_CHAINS = "exclude_chains"
CONF_INCLUDE_BORDER = "include_border"
CONF_INCLUDE_DEPOSIT = "include_deposit"
CONF_ONE_PER_CHAIN = "one_per_chain"
CONF_MAX_RESULTS = "max_results"
CONF_UPDATE_HOURS = "update_hours"

UNIT_ALL = "alle"
UNITS = ["ltr", "kg", "stk", UNIT_ALL]
PACKAGES = [UNIT_ALL, "ds", "fl"]

DEFAULTS = {
    CONF_NAME_CONTAINS: "",
    CONF_NAME_EXCLUDES: "",
    CONF_UNIT: "ltr",
    CONF_PACKAGE: UNIT_ALL,
    CONF_MIN_UNITS: 1,
    CONF_EXCLUDE_CHAINS: [],
    CONF_INCLUDE_BORDER: False,
    CONF_INCLUDE_DEPOSIT: False,
    CONF_ONE_PER_CHAIN: True,
    CONF_MAX_RESULTS: 5,
    CONF_UPDATE_HOURS: 12,
}

# Kæder hvor logo-filnavnet på tilbudsugen.dk ikke følger slug + ".png"
CHAIN_LOGOS = {
    "meny": "meny.png",
    "rema 1000": "rema-1000.svg",
    "kvickly": "kvickly.png",
    "netto": "netto.png",
    "superbrugsen": "super-brugsen.png",
    "365discount": "coop365.png",
    "bilka": "bilka.png",
    "føtex": "foetex.png",
    "lidl": "lidl.png",
    "løvbjerg": "loevbjerg.png",
    "spar": "SPAR.jpg",
    "fakta": "fakta.png",
    "fakta tyskland": "fakta.png",
    "calle": "calle.png",
    "poetzsch padborg": "poetzsch-padborg.jpg",
    "nielsen discount": "nielsens-discount.svg",
    "købmandsgården": "koebmandsgaarden.png",
}
