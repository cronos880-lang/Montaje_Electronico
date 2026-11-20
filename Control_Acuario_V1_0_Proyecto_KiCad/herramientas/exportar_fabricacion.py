"""Genera los archivos de fabricación en ../fabricacion/ (KiCad 9 kicad-cli).

Gerber + taladros Excellon (ZIP para el fabricante), BOM y CPL en formato JLCPCB
con códigos LCSC tomados de Control_Acuario_V1_0_BOM.csv. Los componentes de
inserción (THT) y los externos quedan fuera del montaje SMT: lista aparte.
"""
import csv, os, re, subprocess, zipfile, io
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
PCB = os.path.join(PROJ, 'Control_Acuario_V1_0.kicad_pcb')
OUT = os.path.join(PROJ, 'fabricacion'); GER = os.path.join(OUT, 'gerber')
os.makedirs(GER, exist_ok=True)
run = lambda *a: subprocess.run(['kicad-cli', *a], check=True, capture_output=True, text=True)
for f in os.listdir(GER): os.remove(os.path.join(GER, f))
run('pcb', 'export', 'gerbers', '--layers', 'F.Cu,B.Cu,F.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts',
    '--subtract-soldermask', '--no-x2', '-o', GER + '/', PCB)
run('pcb', 'export', 'drill', '--format', 'excellon', '--excellon-separate-th', '--generate-map', '--map-format', 'pdf', '-o', GER + '/', PCB)
zp = os.path.join(OUT, 'Control_Acuario_V1_0_Gerber.zip')
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in sorted(os.listdir(GER)):
        if not f.endswith('.pdf'): z.write(os.path.join(GER, f), f)
# Códigos LCSC desde la BOM del proyecto
lcsc, manual = {}, set()
with open(os.path.join(PROJ, 'Control_Acuario_V1_0_BOM.csv'), encoding='utf8') as fh:
    for row in csv.DictReader(fh, delimiter=';'):
        refs = row['Referencias'].split()
        code = row['LCSC'].strip()
        mont = row['Montaje'].strip()
        for r in refs:
            if code.startswith('C') and mont == 'SMT': lcsc[r] = code
            else: manual.add(r)
# CPL desde KiCad
pos = os.path.join(OUT, 'pos.csv')
run('pcb', 'export', 'pos', '--format', 'csv', '--units', 'mm', '--side', 'front', '--smd-only', '-o', pos, PCB)
rows = list(csv.DictReader(open(pos, encoding='utf8')))
os.remove(pos)
cpl = os.path.join(OUT, 'Control_Acuario_V1_0_CPL_JLCPCB.csv'); bom = os.path.join(OUT, 'Control_Acuario_V1_0_BOM_JLCPCB.csv')
groups = {}
with open(cpl, 'w', newline='', encoding='utf8') as fh:
    w = csv.writer(fh); w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
    for r in rows:
        ref = r['Ref']
        if ref not in lcsc: continue
        w.writerow([ref, r['PosX'] + 'mm', r['PosY'] + 'mm', 'Top', r['Rot']])
        groups.setdefault((r['Val'], r['Package'], lcsc[ref]), []).append(ref)
with open(bom, 'w', newline='', encoding='utf8') as fh:
    w = csv.writer(fh); w.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #'])
    for (val, pkg, code), refs in sorted(groups.items(), key=lambda kv: kv[1][0]):
        w.writerow([val, ','.join(sorted(refs, key=lambda s: (re.sub(r'\d', '', s), int(re.sub(r'\D', '', s) or 0)))), pkg, code])
smd_sin = sorted(r['Ref'] for r in rows if r['Ref'] not in lcsc)
with open(os.path.join(OUT, 'Montaje_manual.txt'), 'w', encoding='utf8') as fh:
    fh.write('Componentes NO montados por el fabricante (soldar a mano o externos):\n')
    fh.write(' '.join(sorted(manual)) + '\n')
    if smd_sin: fh.write('SMD sin código LCSC (revisar): ' + ' '.join(smd_sin) + '\n')
print('Gerber:', zp); print('BOM:', bom, len(groups), 'líneas'); print('CPL:', cpl, sum(len(v) for v in groups.values()), 'posiciones')
print('SMD sin LCSC:', smd_sin)
