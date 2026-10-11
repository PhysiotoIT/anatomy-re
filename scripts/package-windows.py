"""Package the built site and a checksum-verified official portable Node.exe."""
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
runtime=Path(sys.argv[1])
version=(runtime/'version.txt').read_text().strip()
expected=next(line.split()[0] for line in (runtime/'SHASUMS256.txt').read_text().splitlines()
              if line.split()[-1]=='win-x64/node.exe')
assert hashlib.sha256((runtime/'node.exe').read_bytes()).hexdigest()==expected
dist=ROOT/'dist'
assert (dist/'index.html').is_file()
outputs=ROOT/'outputs'
outputs.mkdir(exist_ok=True)
target=outputs/'anatomy-re-windows.zip'
launcher='''@echo off
cd /d "%~dp0"
title Anatomy RE
"runtime\\node.exe" "portable-server.mjs"
pause
'''.replace('\n','\r\n')
instructions='''ANATOMY RE - WINDOWS

1. Rozpakuj CALY plik ZIP (prawy przycisk > Wyodrebnij wszystkie).
2. Otworz folder anatomy-re i kliknij Uruchom-atlas.cmd.
3. Atlas otworzy sie w przegladarce. Zostaw okno terminala otwarte.
4. W panelu Systems wybierz All, aby pokazac wszystkie uklady.

Nie uruchamiaj pliku z podgladu ZIP. Nie trzeba instalowac Node.js ani npm.
Przegladarka potrzebuje WebGL. Modele sa w paczce; atlas dziala bez Internetu.
Galeria renderow: http://localhost:3016/previews/index.html (po uruchomieniu).

Jesli port 3016 jest zajety, zamknij poprzednie okno atlasu.
Wymagany Windows 10/11 x64; wspolczesny Chrome lub Edge.
'''
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
 for path in sorted(dist.rglob('*')):
  if not path.is_file() or path.suffix=='.bin': continue
  # gzip geometry is already compressed; avoid duplicating the raw model files.
  archive.write(path,Path('anatomy-re/www')/path.relative_to(dist),
                compress_type=zipfile.ZIP_STORED if path.suffix=='.gz' else zipfile.ZIP_DEFLATED)
 archive.write(ROOT/'scripts/portable-server.mjs','anatomy-re/portable-server.mjs')
 for name in ['node.exe','LICENSE.txt','SHASUMS256.txt','version.txt']:
  archive.write(runtime/name,'anatomy-re/runtime/'+name)
 archive.write(ROOT/'LICENSE','anatomy-re/LICENSE-app.txt')
 archive.write(ROOT/'references/zanatomy/LICENSE.txt','anatomy-re/LICENSE-Z-Anatomy.txt')
 archive.write(ROOT/'references/openstax/LICENSE-CC-BY-4.0.txt','anatomy-re/LICENSE-CC-BY-4.0.txt')
 archive.writestr('anatomy-re/Uruchom-atlas.cmd',launcher)
 archive.writestr('anatomy-re/PRZECZYTAJ.txt',instructions)
 source=json.loads((dist/'models/atlas-source.json').read_text())
 light=json.loads((dist/'models/atlas.json').read_text())
 for catalogue in [source,light]:
  for chunk in catalogue['chunks']:
   assert (dist/chunk['gzip'].lstrip('/')).stat().st_size==chunk['gzipBytes']
 audit=dict(nodeVersion=version,nodeSHA256=expected,
            sourceParts=len(source['parts']),sourceTriangles=source['triangles'],lightParts=len(light['parts']))
 archive.writestr('anatomy-re/bundle-info.json',json.dumps(audit,indent=2)+'\n')
print(target,round(target.stat().st_size/1024/1024,1),'MiB; official Node checksum verified')
digest=hashlib.sha256(target.read_bytes()).hexdigest()
target.with_suffix('.zip.sha256').write_text(digest+'  '+target.name+'\n')
