# Tilbudsjagt

Find de billigste tilbud i danske supermarkeder direkte i Home Assistant. Data hentes fra [tilbudsugen.dk](https://www.tilbudsugen.dk).

- Følg faste varer som Pepsi Max, kaffe eller smør
- Søg efter alt fra dit dashboard
- Se billigste butik, pris pr. liter/kg, pris pr. dåse, maks. pr. kunde og udsnit fra tilbudsavisen
- Få besked på telefonen, når en vare kommer under din pris
- Færdigt dashboard-kort følger med

## Installation

**Via HACS**
1. Åbn HACS → ⋮ → **Brugerdefinerede repositories**
2. Tilføj `https://github.com/simonhansen1999/tilbudsjagt` med kategorien **Integration**
3. Søg efter **Tilbudsjagt**, installér og genstart Home Assistant

**Manuelt**
1. Hent `tilbudsjagt.zip` fra seneste [release](https://github.com/simonhansen1999/tilbudsjagt/releases)
2. Pak den ud i `config/custom_components/tilbudsjagt/`
3. Genstart Home Assistant

## Kom i gang

Gå til **Indstillinger → Enheder & tjenester → Tilføj integration → Tilbudsjagt** og vælg:

- **En fast vare**: skriv fx `pepsi max`, `kaffe` eller indsæt en `tilbudsugen.dk/offer/…`-adresse
- **Et søgefelt til dashboardet**: søg efter hvad som helst direkte fra kortet

Du kan tilføje så mange varer, du vil, ved at gentage trinnet.

## Filtre

Vælges under opsætningen og kan altid ændres under **Konfigurér** på integrationen.

| Filter | Beskrivelse |
|---|---|
| Navnet skal indeholde | Ord adskilt af komma, fx `pepsi, max`. Alle ord skal stå i varens navn. Kun for faste varer |
| Navnet må ikke indeholde | Ord adskilt af komma, fx `lime, lemon, sodastream` |
| Kategori | **Automatisk** vælger den kategori, de fleste træffere hører til. Søger du på smør, kommer kun kategorien *Smør* med, og fx baguetter med smør sorteres fra |
| Enhed | Automatisk, pr. liter, pr. kg, pr. stk. eller alle |
| Emballage | Alle, dåser eller flasker |
| Mindste antal pr. tilbud | Fx `24` for kun at se kasser/rammer |
| Kun disse kæder | De butikker du handler i. Tom betyder alle |
| Udeluk kæder | Butikker du aldrig vil se |
| Medtag grænsehandel | Viser også tilbud fra grænsebutikker |
| Medregn pant | Lægger pant oven i prisen (se nedenfor) |
| Kun billigste tilbud pr. kæde | Én række pr. butik |
| Antal tilbud | Hvor mange tilbud der vises (kun faste varer – ved søgning vælges antallet på kortet) |
| Opdateringsinterval | Hvor ofte der hentes nye tilbud (standard 12 timer) |

**Pant** beregnes efter de danske satser: dåser og glasflasker under 1 l koster 1 kr, plastflasker under 1 l 1,50 kr, og flasker på 1 l eller mere 3 kr. Tilbudsugen oplyser ikke materialet, så flasker til og med 33 cl regnes som glas.

## Prisovervågning

Få besked på telefonen, når en vare koster din pris eller mindre. En overvågning er uafhængig af dine faste varer og søgninger – den opretter ingen ekstra pris-sensorer.

Alle overvågninger samles under **Prisovervågning** i integrationen. Den oprettes automatisk første gang, du overvåger noget, eller via **Tilføj integration → Tilbudsjagt → Prisovervågning**.

**Opret en overvågning**
- **Overvågningskortet**: tryk **Ny overvågning**, skriv varen og prisen, og vælg enheder
- **🔔 Overvåg pris** på et vare- eller søgekort: bruger samme kategori og filtre som kortet, så fx baguetter med smør ikke tæller med
- **Indstillinger → Tilbudsjagt → Prisovervågning → Konfigurér → Tilføj overvågning**
- Tjenesten `tilbudsjagt.watch` fra en automation

**Se, ret og slet**
- Overvågningskortet viser alle overvågninger med din pris, billigste tilbud lige nu og hvilke enheder der får besked. Dem under din pris står øverst og er fremhævet
- **Ret** ændrer pris og enheder, **Slet** fjerner overvågningen (tryk to gange)
- På vare- og søgekort viser 🔔-knappen, om varen overvåges. Tryk for at rette eller stoppe
- Eller **Konfigurér → Fjern overvågning**

**Beskeden** ser fx sådan ud:

> **Pepsi Max under 7,00 kr/l**
> Meny: 6,63 kr/l – 1 flaske à 1,5 l for 9,95 kr (23.–29. okt.)

Tryk på beskeden for at åbne tilbuddet. Der sendes kun én besked pr. tilbud, også efter genstart. Kommer der et nyt tilbud under prisen, får du en ny besked.

Enhederne er de notify-tjenester, Home Assistant kender, typisk telefoner med Home Assistant-appen.

## Dashboard-kort

Kortet følger med integrationen. Genindlæs browseren én gang efter installationen.

Gå til **Rediger dashboard → Tilføj kort → Tilbudsjagt**, og vælg en sensor. Eller indsæt:

```yaml
type: custom:tilbudsjagt-card
entity: sensor.pepsi_max
theme: blue
max_rows: 5
```

Vælger du sensoren fra et søgefelt, får kortet automatisk et søgefelt og knapper til at skifte kategori. Vælger du `sensor.prisovervagning`, viser kortet dine prisovervågninger.

Over listen kan du:
- **Krydse mærker af**, fx *Økologisk*, *Dansk* eller *Glutenfri*, så kun tilbud med de mærker vises. Der vises kun mærker, som skiller tilbuddene ad
- **Vælge antal**: 5, 10, 20 eller alle

Valgene huskes i din browser. Afkrydsede mærker nulstilles ved en ny søgning.

Tilbudsugen mærker af og til varer som *Økologisk*, selv om de ikke er det. Står samme vare hos en anden butik uden mærket, fjernes det derfor – medmindre navnet selv siger *øko* eller *organic*.

**På kortet**
- Billigste tilbud er fremhævet med **Bedste pris**
- Pakke, samlet pris og pris pr. dåse/flaske
- Prisforskel til det billigste tilbud
- Mærkater for gyldighed, maks. pr. kunde, begrænset parti m.m.
- **Se i avisen** viser udsnittet fra tilbudsavisen
- 🔔 ved tilbud, der er under din overvågede pris
- Tryk på et tilbud for at åbne det på tilbudsugen.dk

**Indstillinger**

| Valg | Standard | Beskrivelse |
|---|---|---|
| `entity` | – | Tilbudsjagt-sensor |
| `title` | varens navn / søgeordet | Overskrift |
| `subtitle` | fx `Billigste literpris` | Undertekst |
| `theme` | `blue` | `blue`, `red`, `green`, `purple` eller `orange` |
| `image` | dåse eller prismærke | URL til eget billede |
| `max_rows` | `5` | Antal rækker |
| `show_header` | `true` | Vis topbanner og søgefelt |
| `show_updated` | `true` | Vis hvornår der sidst er hentet |

## Entiteter

**For hver fast vare**, fx Pepsi Max:

| Entitet | Tilstand |
|---|---|
| `sensor.pepsi_max` | Laveste pris pr. liter/kg/stk. Alle viste tilbud ligger i attributten `offers` |
| `sensor.pepsi_max_billigste_butik` | Butikken med laveste pris. Attributten `prices` har prisen hos alle butikker |

**For prisovervågningen**:

| Entitet | Tilstand |
|---|---|
| `sensor.prisovervagning` | Antal overvågninger. Attributten `watches` har hver overvågning med `id`, `name`, `price`, `notify`, `hit` og billigste tilbud (`best`) |
| `binary_sensor.prisovervagning_prisalarm` | Tændt når mindst én vare er under din pris |

**For et søgefelt**, fx "Tilbudssøgning":

| Entitet | Tilstand |
|---|---|
| `text.tilbudssogning_sog` | Det der søges efter |
| `select.tilbudssogning_kategori` | Automatisk, alle eller en bestemt kategori |
| `sensor.tilbudssogning` | Som for en fast vare |
| `sensor.tilbudssogning_billigste_butik` | Som for en fast vare |

Hvert tilbud i `offers` indeholder bl.a. `chain`, `name`, `category`, `price`, `unit_price`, `units`, `package`, `size`, `start`, `end`, `limit`, `notes`, `deposit`, `image` og `url`.

## Eksempler

**Byg dit eget kort**

```yaml
type: markdown
content: >
  {% for o in state_attr('sensor.pepsi_max', 'offers') %}
  **{{ o.chain }}**: {{ '%.2f' | format(o.unit_price) }} kr/l
  {% if o.limit %}(maks. {{ o.limit }} pr. kunde){% endif %}
  {% endfor %}
```

**Søg fra en automation eller et script**

```yaml
action: text.set_value
target:
  entity_id: text.tilbudssogning_sog
data:
  value: kaffe
```

**Overvåg fra en automation eller et script**

```yaml
action: tilbudsjagt.watch
data:
  query: pepsi max
  price: 7
  notify:
    - mobile_app_min_telefon
```

Brug `entity_id: sensor.pepsi_max` i stedet for `query` for at overvåge med samme filtre som en vare eller søgning. `tilbudsjagt.update_watch` retter pris eller enheder, og `tilbudsjagt.unwatch` fjerner en overvågning (med `watch_id` eller `entity_id`).

**Egen besked når Pepsi Max er billig**

```yaml
triggers:
  - trigger: numeric_state
    entity_id: sensor.pepsi_max
    below: 7
actions:
  - action: notify.notify
    data:
      message: >
        Pepsi Max koster {{ states('sensor.pepsi_max') }} kr/l
        hos {{ states('sensor.pepsi_max_billigste_butik') }}
```

## Godt at vide

- Tilbuddene læses fra tilbudsugen.dk's hjemmeside. Ændrer de siden, kan integrationen holde op med at virke, indtil den er opdateret.
- Der hentes op til 120 tilbud pr. vare.
- Butikslogoer og avisudsnit hentes direkte fra tilbudsugen.dk af din browser.
- Hent ikke oftere end nødvendigt. To gange i døgnet er rigeligt.

## Problemer og ønsker

Opret et [issue](https://github.com/simonhansen1999/tilbudsjagt/issues).

## Ansvarsfraskrivelse

Tilbudsjagt er ikke lavet af eller godkendt af Tilbudsugen.dk eller butikkerne. Navne og logoer tilhører deres ejere. Priser og gyldighed kan afvige fra butikkens egen avis, som altid er gældende.
