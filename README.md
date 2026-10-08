# Anatomy RE

Atlas 3D całego ciała, wersja 0.2: **2234 elementy siatki, 1658 nazwanych pojęć źródłowych, 6 681 030 trójkątów**. Zaimportowano wszystkie siatki BodyParts3D 4.0 IS-A / 99% reduction. Pełny import tego zbioru nie oznacza kompletnego odpowiednika Complete Anatomy ani rekonstrukcji z atlasów i filmu.

![Render rzeczywistych siatek](docs/full-body-preview.png)

## Uruchomienie

Rozpakuj całe wydanie ZIP i otwórz `OTWORZ_ATLAS.html` albo `public/index.html`. Wydanie zawiera skompilowany silnik i geometrię. Pakiety są lokalnymi skryptami, co umożliwia uruchomienie bez żądań modułów/modeli przez `file://`; ta ścieżka oczekuje testu interaktywnego. Potrzebna współczesna przeglądarka z WebGL2 i DecompressionStream. Ze względu na wielkość modelu zalecany komputer. Układy są ładowane na żądanie.

Repozytorium źródłowe: `npm ci`, `npm run build`, następnie otwórz `dist/index.html`. Tryb deweloperski: `npm run dev`. Serwowanie builda: `npm run preview`.

## Zaimplementowane funkcje

- Obrót, zoom, wybór siatki; wyszukiwanie nazw EN, FMA i wybranych polskich haseł.
- 15 grup geometrii, widoczność i przezroczystość; ustawienia szkieletu, mięśni, narządów, nerwów i naczyń.
- Izolowanie, ukrywanie, przybliżanie oraz widoki anatomiczne.
- Przybliżone filtry regionów według granic przestrzennych, bez segmentacji anatomicznej.
- Płaszczyzna cięcia powierzchni bez wypełnienia; nie symuluje CT/MRI.
- Lokalny zapis widoku, eksport PNG i widocznych siatek do GLB. Cięcie nie jest utrwalane w eksportowanej geometrii.
- Źródła, identyfikatory, SHA-256 i status oczekującej weryfikacji anatomii.

## Zakres

| Grupa wyświetlania | Elementy siatki |
| --- | ---: |
| Kości, w tym zęby | 232 |
| Mięśnie | 425 |
| Tkanki łączne | 95 |
| Tętnice | 634 |
| Żyły | 392 |
| Układ nerwowy | 146 |
| Układ oddechowy | 104 |
| Układ pokarmowy | 109 |
| Serce | 26 |
| Układ moczowo-płciowy | 18 |
| Układ hormonalny | 7 |
| Powłoki | 3 |
| Narządy zmysłów | 36 |
| Tkanki limfatyczne | 3 |
| Niesklasyfikowane | 4 |

To liczby elementów siatki, nie kompletnych narządów czy mięśni. 1954 przypisania do grup wynikają z przynależności w źródle; 276 z reguł nazw wymagających przeglądu; 4 pozostają niesklasyfikowane. Szczegóły: `public/full-catalog.json`, `docs/full-body-coverage.json`.

Model referencyjny dorosłego mężczyzny ma zredukowaną geometrię. Brakuje modelu kobiecego, kompletnej anatomii limfatycznej i części drobnych struktur, zweryfikowanych przyczepów, ruchu/biomechaniki, mikroskopii, AR i badań obrazowych. Nie wykonano przeglądu anatomisty ani walidacji klinicznej. Nie pozyskano geometrii Complete Anatomy. Atlasy i filmy sekcyjne pozostają kandydatami do przeglądu, nie dowodem odtworzenia siatek.

## Modele GLB i odtworzenie danych

Pakiety są zapisane raz w `public/packs/`. `python3 scripts/unpack_models.py` odtwarza 15 samodzielnych plików `models/full-body/*.glb`, około 183 MB. Wszystkie używają wspólnego układu współrzędnych, metrów i osi Y w górę. Importuj je do Blendera bez osobnego centrowania.

```sh
python3 -m pip install -r requirements.txt
python3 scripts/unpack_models.py
npm run validate:full
python3 scripts/test_reconstruction.py
```

Importer źródłowy przyjmuje oficjalne archiwum `isa_BP3D_4.0_obj_99.zip` ze strony [BodyParts3D](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html):

```sh
python3 scripts/build_full_body.py /sciezka/isa_BP3D_4.0_obj_99.zip
npm run validate:full
npm run build
```

`docs/VERIFICATION.md` opisuje weryfikację i ograniczenia. Starsze pliki kończyny dolnej pozostają materiałem wersji 0.1; aktualny atlas używa `full-catalog.json`.

## Twój fork REA

`PhysiotoIT/rea` jest submodułem przypiętym do `6e4535c1011f1982e9ab07b7ebcd600c19cd494d`.

```sh
git submodule update --init --recursive
cd vendor/rea
npm ci
npm run build:cached
cd ../..
npm run build
npm run rea:inspect
```

ZIP nie zawiera historii Git ani zawartości submodułu. Po rozpakowaniu pobierz go przez `git clone https://github.com/PhysiotoIT/rea.git vendor/rea`, następnie `git -C vendor/rea checkout 6e4535c1011f1982e9ab07b7ebcd600c19cd494d` i powyższe komendy budowania.

REA analizuje oprogramowanie przeglądarki; raport jest w `docs/rea-evidence.json.gz`, podsumowanie w `docs/rea-inspection-summary.json`. Nie rekonstruuje ono powierzchni anatomicznych ani nie sprawdza poprawności anatomii.

[Porównanie z filmem](docs/REFERENCE_ANALYSIS.md) i [proces rekonstrukcji](docs/RECONSTRUCTION.md) opisują pozostały zakres. Triangulacja wymaga skalibrowanych widoków tego samego preparatu i zwraca punkty, nie gotowe siatki.

## Licencje i publikacja

Kod: MIT. BodyParts3D: CC BY 4.0; źródła i modyfikacje w [NOTICE.md](NOTICE.md). Nie zawarto ilustracji atlasów ani klatek filmowych.

Docelowe osobne repozytorium: `PhysiotoIT/anatomy-re`. Wersja 0.2 przygotowana lokalnie. Utworzenie i publikacja repozytorium zdalnego nie zostały potwierdzone.
