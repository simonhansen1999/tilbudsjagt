# Tilbudsjagt

Home Assistant-integration, der finder de billigste tilbud på en vare fra [tilbudsugen.dk](https://www.tilbudsugen.dk) – fx Pepsi Max, Coca-Cola eller kaffe. Inkluderer et færdigt dashboard-kort.

## Installation

**HACS**
1. HACS → ⋮ → *Brugerdefinerede repositories*
2. Tilføj `https://github.com/simonhansen1999/tilbudsjagt`, kategori **Integration**
3. Installér *Tilbudsjagt* og genstart Home Assistant

**Manuelt**
- Kopiér `custom_components/tilbudsjagt` til `config/custom_components/` og genstart

## Opsætning

Indstillinger → Enheder & tjenester → Tilføj integration → **Tilbudsjagt**

1. **Vare**: fx `pepsi max` eller en hel `tilbudsugen.dk/offer/…`-adresse
2. **Filtre**:
   - **Navnet skal indeholde**: fx `pepsi, max`
   - **Navnet må ikke indeholde**: fx `sodastream, koncentrat, lime`
   - **Enhed**: pr. liter, kg, stk. eller alle
   - **Emballage**: alle, dåser eller flasker
   - **Mindste antal pr. tilbud**: fx `24` for kun kasser/rammer
   - **Udeluk kæder**: vælg fra listen
   - **Medtag grænsehandel**
   - **Medregn pant**: lægger pant oven i pris og literpris (dåser og glas under 1 l: 1 kr, plast under 1 l: 1,50 kr, 1 l og derover: 3 kr). Materialet står ikke i dataene, så flasker til og med 33 cl regnes som glas
   - **Kun billigste tilbud pr. kæde**
   - **Antal tilbud** og **opdateringsinterval** (standard 12 timer)

Tilføj flere varer ved at køre opsætningen igen. Filtrene kan ændres senere under **Konfigurér**.

## Sensorer

To sensorer pr. vare, fx for Pepsi Max:

- `sensor.pepsi_max`
  - **Tilstand**: billigste enhedspris (kr/l, kr/kg eller kr/stk)
  - **Attributter**: `offers` (de viste tilbud med `chain`, `name`, `price`, `unit_price`, `units`, `package`, `size`, `start`, `end`, `limit`, `notes`, `deposit`, `deposit_included`, `url`, `logo`), `chains`, `total_offers`, `unit`, `include_deposit`, `url`, `last_fetch`
- `sensor.pepsi_max_billigste_butik`
  - **Tilstand**: kæden med den laveste enhedspris, fx `Meny`
  - **Attributter**: `unit_price`, `price`, `product`, `url`, `price_unit` og `prices` med billigste enhedspris for **alle** kæder, der opfylder filtrene

Eksempel i en skabelon:

```jinja
{{ states('sensor.pepsi_max_billigste_butik') }} –
{{ state_attr('sensor.pepsi_max_billigste_butik', 'unit_price') }} kr/l
```

## Kort

Kortet følger med integrationen – ingen ekstra installation eller ressource. Genindlæs browseren efter første opsætning.

Dashboard → Rediger → Tilføj kort → **Tilbudsjagt**, eller:

```yaml
type: custom:tilbudsjagt-card
entity: sensor.pepsi_max
title: Pepsi Max
theme: blue        # blue, red, green, purple, orange
max_rows: 5
```

| Valg | Standard | Beskrivelse |
|---|---|---|
| `entity` | – | Tilbudsjagt-sensor |
| `title` | sensorens navn | Overskrift |
| `subtitle` | `Billigste literpris` | Undertekst |
| `kicker` | `Tilbudsjagt` | Lille tekst over titlen |
| `theme` | `blue` | Farvetema |
| `image` | dåse-ikon | URL til eget billede i stedet for dåsen |
| `max_rows` | `5` | Antal rækker |
| `show_header` | `true` | Vis topbanner |
| `show_updated` | `true` | Vis "Sidst opdateret" |

Tryk på en række for at åbne tilbuddet.

## Begrænsninger

- Tilbudsugen viser kun de første 30 tilbud pr. vare. Danske butikker ligger først, så de billigste er som regel med.
- Integrationen læser sidens indlejrede data. Ændrer tilbudsugen.dk deres side, kan den holde op med at virke.
- Hent ikke oftere end nødvendigt.

## Ansvarsfraskrivelse

Ikke lavet af eller godkendt af Tilbudsugen.dk eller butikkerne. Navne og logoer tilhører deres ejere. Logoer hentes direkte fra tilbudsugen.dk af browseren.
