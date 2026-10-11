# Anatomy RE

Samodzielny atlas 3D z pełną geometrią Z-Anatomy wyeksportowaną przez Blender oraz opcjonalnym trybem lekkim opartym na BodyParts3D i modelach edukacyjnych. Repozytorium zawiera oba katalogi anatomii i 46 pakietów geometrii. Można je uruchomić bez sąsiednich repozytoriów.

## Otwieranie w przeglądarce przez GitHub Pages

Gotowa strona wraz z modelami jest publikowana na gałęzi `gh-pages`.
Właściciel repozytorium włącza ją jednorazowo w
[Settings → Pages](https://github.com/PhysiotoIT/anatomy-re/settings/pages):

1. **Source:** `Deploy from a branch`.
2. **Branch:** `gh-pages`; folder: `/ (root)`.
3. Kliknij **Save** i poczekaj, aż GitHub zakończy publikację.

Po publikacji adres atlasu to `https://physiotoit.github.io/anatomy-re/`.
Odwiedzający nie potrzebuje Git, Node.js ani terminala. Pierwsze otwarcie
pobiera modele, więc wymaga połączenia z Internetem. Przycisk **All**
włącza wszystkie układy; **Tryb lekki** zmniejsza ilość ładowanej geometrii.

Do aktualizacji gotowej strony służy `bash scripts/publish-pages.sh`.
Skrypt buduje atlas z prefiksem `/anatomy-re/`, zapisuje stronę na gałęzi
`gh-pages` i wysyła ją bez zmiany głównego katalogu roboczego oraz bez
wymuszania nadpisania historii. Wymaga Node.js, Git oraz prawa do push.

## Uruchomienie na swoim komputerze

Wymagany jest Node.js 22.13 lub nowszy.

### Pobranie przez Git

Zainstaluj Git i Node.js (zalecana wersja 24 LTS), a następnie w terminalu
Windows wykonaj:

```sh
git clone --branch codex/anatomy-atlas https://github.com/PhysiotoIT/anatomy-re.git
cd anatomy-re
npm ci
npm run dev -- --open
```

Przeglądarka otworzy atlas działający na Twoim komputerze. Pozostaw terminal
otwarty. Repozytorium zawiera oba kompletne zestawy modeli; po instalacji
zależności atlas nie pobiera anatomii z zewnętrznych serwisów. Pierwsze
pobranie może potrwać kilka minut ze względu na rozmiar geometrii.
Włącz wszystkie układy przyciskiem **All**.

Jeżeli masz już ten klon, pobierz i przełącz gałąź:

```sh
git fetch origin
git switch codex/anatomy-atlas
npm ci
npm run dev -- --open
```

Późniejsze aktualizacje na tej gałęzi pobieraj poleceniem `git pull`.

### Sprawdzenie i budowanie

```sh
npm ci
npm run validate:atlas
npm run validate:source
npm run validate:tours
npm run check
npm run dev
```

Serwer deweloperski uruchamia się pod `http://localhost:3016/`. Do zbudowania wersji statycznej użyj `npm run build`; pliki wynikowe pojawią się w `dist/`. Można je serwować poleceniem `npm run preview`. Przeglądarka potrzebuje WebGL; `DecompressionStream` przyspiesza pobieranie skompresowanych modeli.

`localhost` zawsze oznacza komputer, na którym otwarto przeglądarkę. Serwer
uruchomiony w środowisku chmurowym nie jest dostępny pod tym adresem na
komputerze użytkownika. To środowisko nie udostępnia publicznego podglądu.

### Gotowa paczka dla Windows

Archiwum `outputs/anatomy-re-windows.zip` zawiera zbudowaną aplikację,
wszystkie modele i oficjalny przenośny Node.js dla Windows 10/11 x64.
Rozpakuj **całe archiwum**, wejdź do folderu `anatomy-re` i otwórz
`Uruchom-atlas.cmd`. Przeglądarka otworzy atlas po uruchomieniu serwera.
Pozostaw okno terminala otwarte. Nie jest potrzebna instalacja Node.js,
`npm` ani połączenie z Internetem. Wszystkie układy włącz przyciskiem **All**.

`scripts/package-windows.py` tworzy tę paczkę z `dist/` oraz oficjalnego
`node.exe`, którego SHA-256 musi odpowiadać plikowi `SHASUMS256.txt` tej samej
wersji z nodejs.org. `scripts/portable-server.mjs` udostępnia wyłącznie katalog
aplikacji na `127.0.0.1`; modele są przechowywane raz, w gzip. Paczka i jej
SHA-256 są generowanymi plikami, pomijanymi w Git.

## Obecny zakres

- Domyślny tryb „Pełna geometria”: 2913 modeli Z-Anatomy, 8 198 244 trójkąty i 5373 pojęcia katalogu. Oryginalna topologia jest zachowana bez dodatkowego uproszczenia. „Tryb lekki” przywraca dotychczasowy katalog. Zbiory są rozdzielone, ponieważ mają inne położenie i podział struktur.
- Pełny projekt Blendera zawiera 5249 edytowalnych obiektów anatomii w dwóch widokach: pełne źródło i wszystkie dotychczasowe modele. [Opis projektu i odtwarzanie](docs/blender-source-quality.md).
- Tryb lekki: 2234 siatki z BodyParts3D, 96 dodatkowych siatek Z-Anatomy oraz 6 autorskich modeli edukacyjnych: pierścień i jądro krążka L4–L5, obustronne więzadła rzepki i kaletki przedrzepkowe. Katalog zawiera 3598 pojęć i 2 612 284 trójkąty w 17 pakietach. Sześć modeli Blendera ma łącznie 206 072 trójkąty, w tym poglądowe warstwy pierścienia i podłużne bruzdy więzadeł.
- Obracanie i przybliżanie modelu, wybór struktury, wyszukiwanie po nazwie i identyfikatorze, izolowanie wybranej struktury oraz przełączanie widoczności układów.
- W panelu wybranej struktury suwak „Wygaszenie otoczenia” płynnie osłabia pozostałe widoczne tkanki, pozostawiając wskazaną strukturę pełną i podświetloną.
- Oryginalne identyfikatory źródłowe i krótkie opisy edukacyjne w panelu struktur.
- Tryb nauki z pięcioma prowadzonymi trasami (krążenie, układ nerwowy, mechanika i stabilność kolana oraz budowa krążka L4–L5): każda prowadzi kamerę do kolejnych struktur, dobiera warstwy i pokazuje etykietę przy modelu. Po trasie dostępny jest krótki quiz z wynikiem.
- W każdej trasie jest spis struktur do szybkiego przejścia między tematami oraz tryb zapamiętywania: ukrywa nazwę i opis bieżącej struktury do chwili kliknięcia „Pokaż nazwę i opis”.
- Przekrój modelu płaszczyzną strzałkową, czołową lub poprzeczną, z regulacją jej położenia. Płaszczyzna ucina widoczne powierzchnie, ale nie wypełnia przeciętych siatek i nie reprezentuje obrazu CT ani MRI.
- Przełącznik „Modele edukacyjne” udostępnia sześć uzupełnień z Blendera. Są oznaczone jako uproszczone i bez przeglądu anatomisty. Wyszukiwarka rozpoznaje ich polskie nazwy, a widok z góry pozwala obejrzeć budowę krążka. Lekcje automatycznie przygaszają i ograniczają otaczający kontekst.

W pełnym trybie dostępne są również dwie lekcje źródłowe: krążek L4–L5 oraz torebka i kaletki kolana. Lekcje z dotychczasowego atlasu pojawiają się, gdy wszystkie ich pojęcia mają jednoznaczne odpowiedniki w nowym katalogu.

Raport luk i analiza ilustracji: [`docs/atlas-gaps.md`](docs/atlas-gaps.md). Edytowalny projekt: [`modeling/atlas-additions.blend`](modeling/atlas-additions.blend). Skrypt [`modeling/build_additions.py`](modeling/build_additions.py) odtwarza modele w Blenderze, a `node scripts/import-blender-models.mjs` aktualizuje katalog bez dublowania siatek. Ilustracje OpenStax 1e i ich licencja są zachowane w `references/openstax/`.

Trasy są zapisane w `app/study-tours.json`. `npm run validate:tours` sprawdza, czy ich pojęcia i układy rzeczywiście istnieją w katalogu oraz czy wskazane struktury są widoczne po włączeniu wybranych warstw. Opisy są edukacyjne i nie zastępują zweryfikowanej treści klinicznej.

## Wzorzec nauki i inspiracja Kenhub

Użytkownik wskazał Kenhub jako punkt odniesienia. Przełożyliśmy na atlas 3D sekwencję: wybór tematu → oglądanie oznaczonej struktury w kontekście → samodzielne przypomnienie nazwy → quiz identyfikacyjny z wynikiem. Spis struktur pozwala wrócić do wybranego elementu lekcji. To własna implementacja oparta na ogólnym wzorcu nauki anatomii, nie kopia materiałów ani interfejsu Kenhub. Próba bezpośredniego odczytu serwisu i jego filmów w tym środowisku zwróciła HTTP 403, więc bieżących ekranów Kenhub nie mogliśmy zweryfikować. Do dokładnego porównania konkretnej prezentacji potrzebny będzie dostępny film lub zrzuty ekranu.

Jako drugi punkt odniesienia użytkownik podał 3D4Medical. Dodałem kontrolę wygaszania kontekstu do pracy z wybraną strukturą w modelu 3D. To autorska funkcja atlasu, nie odtworzenie konkretnego ekranu 3D4Medical: próby odczytu `3d4medical.com` przez proxy także otrzymują HTTP 403, a bez proxy domena nie jest osiągalna. Dokładne porównanie widoków i zachowań wymaga dostępnego nagrania lub zrzutów.

To referencyjna anatomia dorosłego mężczyzny. Dane nie przedstawiają wszystkich struktur ani wariantów anatomicznych. Atlas nie służy do diagnostyki lub planowania zabiegów. Blender eksportuje pełną geometrię do pakietów aplikacji. Nie ma eksportu GLB ani rekonstrukcji z filmów. Opis tych funkcji znajdował się w poprzednim README, ale ich kod i dane nie były obecne w historii tego repozytorium.

## Źródło i licencje

Kod aplikacji pochodzi z repozytorium `PhysiotoIT/human-atlas` i jest udostępniany na licencji MIT (patrz `LICENSE`). Oryginalne modele i metadane BodyParts3D 4.0 są objęte CC BY 4.0; dodatkowe, przetworzone modele Z-Anatomy są objęte CC BY-SA 4.0. Autorskie modele z Blendera i wykorzystane ilustracje OpenStax 1e są objęte CC BY 4.0. Szczegóły pochodzenia, przekształceń i warunków udostępniania znajdują się w [`public/ATTRIBUTION.md`](public/ATTRIBUTION.md). Weryfikację liczby siatek, pojęć, trójkątów, zamknięcia nowych powierzchni i spójności buforów uruchamia `npm run validate:atlas`.

Pełne modele Z-Anatomy, ich metadane, renderowane podglądy i złożony projekt Blendera: CC BY-SA 4.0. Oryginalna licencja: `references/zanatomy/LICENSE.txt`. Rozdzielczość źródłowych siatek jest nierówna; większa liczba trójkątów nie oznacza zatwierdzenia poprawności anatomii.
