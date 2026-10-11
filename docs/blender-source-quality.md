# Pełny atlas w Blenderze i szczegółowość źródłowa

## Co rzeczywiście zostało wykonane

- Blender 4.3.2 odczytał wszystkie siedem anatomicznych plików FBX Z-Anatomy.
- 2913 właściwych siatek i 8 198 244 trójkąty wyeksportowano bez decymacji,
  subdivide i displacementu do osobnego katalogu `atlas-source.json`.
- Znaczniki opisów `.j`/`.i`, powierzchnie przyczepów `.o…`/`.e…`, puste
  płaszczyzny i pomocnicze obiekty pozostają w osobnej kolekcji Blendera;
  nie są liczone jako modele anatomii w aplikacji.
- Wszystkie 2336 siatek dotychczasowego atlasu odtworzono jako niezależne
  obiekty Blendera. Zachowano identyfikatory, układy i pochodzenie.
- Sześć autorskich modeli dopracowano do 206 072 trójkątów: pierścień ma
  14 poglądowych rowków koncentrycznych, więzadła podłużne bruzdy i gęstszą
  powierzchnię, jądro i kaletki gładsze powierzchnie. Rowki nie są pomiarami
  histologicznymi; modele nadal mają status `schematic` i `unreviewed`.

To rekonstrukcja sceny z otwartych modeli oraz rozwój sześciu własnych modeli.
Nie oznacza ręcznego wyrzeźbienia od początku wszystkich struktur człowieka.

## Plik Blendera

`modeling/anatomy-full-source.blend` zawiera dwa widoki:

| View Layer | Zawartość |
|---|---|
| SOURCE QUALITY · original geometry | Pełna geometria Z-Anatomy, kolekcje według układów |
| CURRENT ATLAS · complete editable reference | Wszystkie modele dotychczasowego atlasu, również nowe uzupełnienia |

Zbiory mają różne układy położenia. Widoki są rozdzielone i nie udają
zarejestrowanych do siebie skanów. Każdy model można wybrać i edytować osobno.
W pliku są spakowane ilustracje OpenStax, źródłowe nazwy i dokumenty licencji.
Duży plik `.blend` jest generowany lokalnie i pomijany w zwykłym Git;
skrypt, audyt oraz wszystkie pakiety przeglądarkowe pozostają w repozytorium.

## Zakres szczegółowości i pozostała praca

Pełna geometria jest najwyższą rozdzielczością pozyskanych FBX, a nie
gwarancją jakości profesjonalnego komercyjnego atlasu. Rozdzielczość
poszczególnych źródłowych siatek jest nierówna: np. prawa rzepka ma tylko
276 trójkątów. Podział takiej powierzchni nie odzyska jej prawdziwych
szczegółów anatomicznych. Dalsza poprawa wymaga lepszych danych dla danej
struktury, opracowania z kilku widoków i przeglądu anatomisty.

Dotychczasowy uproszczony BodyParts3D zawiera 2 288 268 trójkątów z
6 681 030 oryginalnych. Pobranie archiwum z serwera BodyParts3D zwraca
w tym środowisku 403; nie odtworzono utraconej geometrii z uproszczonej siatki.
Pełny Z-Anatomy jest spójną alternatywną bazą; nazwy i podział struktur
różnią się od BodyParts3D. Dopasowane stare pojęcia są zgodnościami nazw,
a nie nową walidacją ontologii FMA.

W nowym katalogu są m.in. źródłowe jądra krążków, torebki stawowe i trzy
rozróżnione rodzaje kaletek przedrzepkowych. Niektóre wcześniejsze luki
wynikały z zakresu importu 96 siatek, a nie z braku w całym Z-Anatomy.
Nie opracowano anatomii żeńskiej, wariantów ani pełnej mikroanatomii.

## Odtworzenie

```sh
bash scripts/fetch-source-models.sh /tmp/anatomy-z-original
blender -b --factory-startup --python modeling/build_additions.py
node scripts/import-blender-models.mjs
blender -b --factory-startup --python modeling/build_full_atlas.py -- /tmp/anatomy-z-original
npm run validate:atlas
npm run validate:source
npm run validate:tours
blender -b modeling/anatomy-full-source.blend --python modeling/verify_full_scene.py
npm run check
npm run build
```

Weryfikacja pełnego katalogu porównuje liczbę wierzchołków i trójkątów
każdej siatki przed i po eksporcie, wszystkie indeksy, granice powierzchni,
pojęcia, licencje i pakiety gzip. `modeling/source-quality-audit.json`
zawiera wyniki oraz SHA-256 każdego oryginalnego FBX.

`verify_full_scene.py` ponownie otwiera zapisany projekt i porównuje wszystkie
5249 obiektów z buforami aplikacji, z tolerancją 0,5 µm. Transformacje FBX
są wypalone w wierzchołki, animacje nie są importowane, a współdzielone
siatki są kopiowane przed przekształceniem. Pozwala to zachować odbicia,
skalę i położenie również po ponownym otwarciu pliku Blendera.

Źródło: Z-Anatomy PC-Version, dokładny commit
`6c7f9016bd5899ac8edafd31b9900c151df42ed6`, CC BY-SA 4.0.
Autorzy: współtwórcy Z-Anatomy, w tym Gauthier Kervyn i Lluís Vinent Juanico;
dane pochodzą częściowo z BodyParts3D, © DBCLS.
