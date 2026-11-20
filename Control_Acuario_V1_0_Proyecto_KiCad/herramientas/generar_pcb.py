"""Genera Control_Acuario_V1_0.kicad_pcb a partir de la netlist del esquema.

Uso (KiCad 9, Python con módulo pcbnew):
    kicad-cli sch export netlist -o net.net Control_Acuario_V1_0.kicad_sch
    python3 herramientas/generar_pcb.py net.net
Coloca componentes, asigna redes, dibuja contorno, taladros y planos.
No traza pistas: el trazado se hace aparte.
"""
import re, sys, os, pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
OUT = os.path.join(PROJ, 'Control_Acuario_V1_0.kicad_pcb')
FPROOT = '/usr/share/kicad/footprints'
OX, OY = 100.0, 100.0          # origen de la placa en coordenadas KiCad
W, H = 100.0, 75.0             # tamaño de la placa (mm)
mm = pcbnew.FromMM

# Colocación: ref -> (x, y, rot, cara)  [mm respecto a la esquina superior izquierda]
PLACE = {
    # --- ESP32 arriba a la izquierda; la antena sobresale por el borde superior ---
    'A1': (2.6, 1.9, 0, 'F'),
    # Bajo el DevKit (componentes bajos): I2C, sonda y mandos SSR
    'R12': (8.0, 8.0, 0, 'F'), 'R13': (8.0, 10.5, 0, 'F'), 'R9': (8.0, 13.0, 0, 'F'), 'R16': (8.0, 15.5, 0, 'F'),
    'R14': (14.0, 8.0, 0, 'F'), 'R15': (14.0, 10.5, 0, 'F'), 'D2': (14.0, 13.0, 0, 'F'), 'C17': (14.0, 15.5, 0, 'F'),
    'R4': (36.0, 54.0, 90, 'F'), 'R8': (88.0, 73.0, 0, 'F'), 'C16': (44.5, 44.5, 0, 'F'),
    'Q2': (8.0, 22.0, 0, 'F'), 'R20': (8.0, 26.0, 0, 'F'), 'R21': (8.0, 28.5, 0, 'F'),
    'Q4': (14.0, 22.0, 0, 'F'), 'R30': (14.0, 26.0, 0, 'F'), 'R32': (14.0, 28.5, 0, 'F'),
    'Q3': (8.0, 34.0, 0, 'F'), 'R22': (8.0, 38.0, 0, 'F'), 'R23': (8.0, 40.5, 0, 'F'),
    'Q5': (14.0, 34.0, 0, 'F'), 'R31': (14.0, 38.0, 0, 'F'), 'R33': (14.0, 40.5, 0, 'F'),
    'D5': (21.0, 44.0, 0, 'F'), 'R25': (20.0, 27.0, 0, 'F'), 'D4': (20.0, 31.0, 0, 'F'),
    # --- Conectores de señal en el borde superior ---
    'J4': (36.5, 3.0, 90, 'F'), 'J3': (46.5, 3.0, 90, 'F'), 'J5': (60.0, 3.0, 90, 'F'),
    # --- Fuente auxiliar 5 V y DAC ---
    'U1': (78.0, 12.0, 0, 'F'), 'C3': (73.0, 18.0, 0, 'F'), 'C20': (78.0, 18.0, 0, 'F'), 'C18': (83.0, 18.0, 0, 'F'),
    'U4': (40.0, 44.5, 0, 'F'),
    # --- Entrada 36 V (abajo a la izquierda) ---
    'J1': (6.0, 62.0, 90, 'F'), 'F1': (13.5, 70.5, 0, 'F'), 'D1': (20.0, 58.0, 180, 'F'), 'C1': (30.0, 62.0, 180, 'F'),
    # --- Buck ---
    'U2': (43.0, 62.0, 180, 'F'), 'C2': (37.2, 71.5, 0, 'F'), 'C4': (37.2, 68.0, 0, 'F'), 'C5': (37.2, 64.5, 0, 'F'), 'C6': (38.6, 59.0, 90, 'F'),
    'C7': (48.2, 62.6, 0, 'F'), 'C8': (47.9, 60.35, 0, 'F'), 'L1': (58.5, 62.0, 0, 'F'),
    'R1': (40.0, 54.5, 0, 'F'), 'R2': (40.0, 52.0, 0, 'F'), 'R3': (40.0, 49.5, 0, 'F'),
    'C9': (66.0, 49.5, 0, 'F'), 'C10': (68.0, 63.5, 270, 'F'), 'C11': (66.0, 70.3, 0, 'F'), 'R24': (59.0, 71.5, 0, 'F'),
    # --- Protección U3 y medida ---
    'U3': (73.0, 62.0, 0, 'F'), 'C13': (69.3, 57.8, 90, 'F'), 'C14': (78.5, 60.0, 270, 'F'),
    'R27': (70.0, 73.0, 0, 'F'), 'R28': (74.5, 73.0, 0, 'F'),
    'R5': (71.6, 68.5, 0, 'F'), 'R29': (79.0, 68.5, 0, 'F'), 'R6': (79.0, 73.0, 0, 'F'), 'C12': (83.5, 73.0, 0, 'F'),
    'R7': (77.0, 55.0, 0, 'F'), 'R8x': None,
    'R10': (20.0, 16.0, 0, 'F'), 'R11': (20.0, 18.5, 0, 'F'), 'C15': (20.0, 21.0, 0, 'F'),
    # --- Salida de luz, PWM y retorno conmutado (derecha) ---
    'J2': (94.0, 58.5, 270, 'F'), 'Q1': (83.5, 70.3, 0, 'F'), 'D3': (86.5, 61.5, 270, 'F'),
    'R19': (90.0, 41.0, 0, 'F'), 'R26': (84.0, 41.0, 0, 'F'), 'C9x': None,
    'U5': (76.0, 40.0, 0, 'F'), 'R17': (82.0, 46.0, 0, 'F'), 'R18': (80.0, 34.0, 0, 'F'), 'C19': (70.0, 36.0, 0, 'F'),
}
PLACE = {k: v for k, v in PLACE.items() if v}

def parse_netlist(path):
    t = open(path, encoding='utf8').read()
    comps = {}
    for m in re.finditer(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)\s*\(footprint "([^"]*)"\)(.*?)\(tstamps "([^"]+)"\)', t, re.S):
        comps[m.group(1)] = dict(value=m.group(2), fp=m.group(3), uuid=m.group(5))
    pads = {}
    for m in re.finditer(r'\(net \(code "\d+"\) \(name "([^"]+)"\)(.*?)(?=\(net \(code|\Z)', t, re.S):
        for r, p in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(2)):
            pads[(r, p)] = m.group(1)
    return comps, pads

def load_fp(fp):
    lib, name = fp.split(':')
    path = os.path.join(PROJ, 'Acuario.pretty') if lib == 'Acuario' else os.path.join(FPROOT, lib + '.pretty')
    f = pcbnew.FootprintLoad(path, name)
    f.SetFPID(pcbnew.LIB_ID(lib, name))
    return f

def main(netpath):
    comps, pads = parse_netlist(netpath)
    b = pcbnew.BOARD()
    b.SetCopperLayerCount(2)
    ds = b.GetDesignSettings()
    ds.m_TrackMinWidth = mm(0.2); ds.m_MinClearance = mm(0.2); ds.m_ViasMinSize = mm(0.6); ds.m_MinThroughDrill = mm(0.3)
    ds.m_CopperEdgeClearance = mm(0.4)
    # Clases de red
    nc = ds.m_NetSettings
    defc = nc.GetDefaultNetclass(); defc.SetTrackWidth(mm(0.25)); defc.SetClearance(mm(0.2)); defc.SetViaDiameter(mm(0.6)); defc.SetViaDrill(mm(0.3))
    pw = pcbnew.NETCLASS('Potencia'); pw.SetTrackWidth(mm(2.0)); pw.SetClearance(mm(0.2)); pw.SetViaDiameter(mm(1.0)); pw.SetViaDrill(mm(0.5))
    mid = pcbnew.NETCLASS('Alimentacion'); mid.SetTrackWidth(mm(0.6)); mid.SetClearance(mm(0.2)); mid.SetViaDiameter(mm(0.8)); mid.SetViaDrill(mm(0.4))
    nc.SetNetclass('Potencia', pw); nc.SetNetclass('Alimentacion', mid)
    for n in ['/DC_IN', '/BUS_36V', '/BUCK_SW', '/BUCK_VOUT', '/LED_POS', '/LED_NEG', '/GND']:
        nc.SetNetclassPatternAssignment(n, 'Potencia')
    for n in ['/VCC_5V', '/ESP_5V', '/VCC_3V3']:
        nc.SetNetclassPatternAssignment(n, 'Alimentacion')
    # Redes
    netinfo = {}
    for name in sorted(set(pads.values())):
        ni = pcbnew.NETINFO_ITEM(b, name); b.Add(ni); netinfo[name] = ni
    # Componentes
    missing = [r for r in comps if r not in PLACE]
    if missing: raise SystemExit('Sin colocación: %s' % missing)
    for ref, c in sorted(comps.items()):
        f = load_fp(c['fp'])
        f.SetReference(ref); f.SetValue(c['value'])
        f.SetPath(pcbnew.KIID_PATH('/' + c['uuid']))
        x, y, rot, side = PLACE[ref]
        b.Add(f)
        if side == 'B': f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
        f.SetPosition(pcbnew.VECTOR2I(mm(OX + x), mm(OY + y)))
        f.SetOrientationDegrees(rot)
        for p in f.Pads():
            n = pads.get((ref, p.GetNumber()))
            if n: p.SetNet(netinfo[n])
    # Contorno
    pts = [(0, 0), (W, 0), (W, H), (0, H)]
    for i in range(4):
        s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1))
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % 4]
        s.SetStart(pcbnew.VECTOR2I(mm(OX + x1), mm(OY + y1))); s.SetEnd(pcbnew.VECTOR2I(mm(OX + x2), mm(OY + y2))); b.Add(s)
    # Taladros M3 (sin cobre)
    for (x, y) in [(96.5, 3.5), (4.0, 71.5), (95.0, 70.8), (34.5, 30.0)]:
        h = load_fp('MountingHole:MountingHole_3.2mm_M3')
        h.SetReference('H%d' % (len([1 for _ in b.Footprints() if _.GetReference().startswith('H')]) + 1))
        h.SetPosition(pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))); h.SetBoardOnly(True); h.SetExcludedFromBOM(True); h.SetExcludedFromPosFiles(True); b.Add(h)
    # Plano de masa en la cara inferior (toda la placa) y superior
    for layer, prio in ((pcbnew.B_Cu, 0), (pcbnew.F_Cu, 0)):
        z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(netinfo['/GND']); z.SetAssignedPriority(prio)
        z.SetLocalClearance(mm(0.3)); z.SetMinThickness(mm(0.25))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL); z.SetThermalReliefGap(mm(0.3)); z.SetThermalReliefSpokeWidth(mm(0.5))
        ol = z.Outline(); ol.NewOutline()
        for (x, y) in pts: ol.Append(mm(OX + x), mm(OY + y))
        b.Add(z)
    # Zona prohibida de cobre bajo la antena del ESP32 (la parte que queda sobre la placa)
    ax0, ax1 = PLACE['A1'][0] + 3.7, PLACE['A1'][0] + 21.7
    k = pcbnew.ZONE(b); k.SetIsRuleArea(True); k.SetDoNotAllowTracks(True); k.SetDoNotAllowVias(True); k.SetDoNotAllowCopperPour(True)
    k.SetDoNotAllowPads(False); k.SetDoNotAllowFootprints(False)
    k.SetLayerSet(pcbnew.LSET.AllCuMask()); ol = k.Outline(); ol.NewOutline()
    for (x, y) in [(ax0, 0), (ax1, 0), (ax1, PLACE['A1'][1] - 0.3), (ax0, PLACE['A1'][1] - 0.3)]: ol.Append(mm(OX + x), mm(OY + y))
    b.Add(k)
    pcbnew.SaveBoard(OUT, b)
    print('Guardado', OUT, len(comps), 'componentes')

if __name__ == '__main__':
    main(sys.argv[1])
