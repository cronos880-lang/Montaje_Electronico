"""Trazado de Control_Acuario_V1_0.kicad_pcb (paso posterior a generar_pcb.py).

1) vías térmicas en las almohadillas expuestas de U2 y U3;
2) exporta Specctra DSN (anchos provisionales de 0,3 mm para que el enrutador
   pueda salir de los QFN) y, tras Freerouting, importa la sesión SES;
3) añade zonas de cobre anchas en F.Cu para la ruta de potencia y vías de
   unión de masa; rellena zonas y guarda.
Uso:
    python3 herramientas/trazar_pcb.py vias      # paso 1 + exporta placa.dsn
    java -jar freerouting-2.4.1-executable.jar -de placa.dsn -do placa.ses -mp 40 --gui.enabled=false
    python3 herramientas/trazar_pcb.py importar placa.ses
"""
import sys, os, pcbnew
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
PCB = os.path.join(PROJ, 'Control_Acuario_V1_0.kicad_pcb')
mm = pcbnew.FromMM; OX = OY = 100.0

def net(b, name): return b.FindNet(name)

def add_via(b, x, y, n, d=0.6, drill=0.3):
    v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(int(x), int(y))); v.SetWidth(mm(d)); v.SetDrill(mm(drill))
    v.SetNet(n); v.SetViaType(pcbnew.VIATYPE_THROUGH); b.Add(v); return v

def thermal_vias(b):
    g = net(b, '/GND')
    for ref, padnum, nx, ny in (('U2', '31', 2, 4), ('U3', '25', 3, 3)):
        p = [p for p in b.FindFootprintByReference(ref).Pads() if p.GetNumber() == padnum][0]
        c = p.GetPosition(); sx, sy = p.GetSize().x, p.GetSize().y
        if p.GetOrientationDegrees() % 180: sx, sy = sy, sx
        for i in range(nx):
            for j in range(ny):
                x = c.x - sx / 2 + sx * (i + 0.5) / nx; y = c.y - sy / 2 + sy * (j + 0.5) / ny
                q = pcbnew.VECTOR2I(int(x), int(y))
                if any(t.GetNetname() != '/GND' and t.HitTest(q, mm(0.55)) for t in b.GetTracks()):
                    continue  # una pista de otra red pasa por debajo
                add_via(b, x, y, g, 0.6, 0.3)

def set_widths(b, pot, ali):
    ns = b.GetDesignSettings().m_NetSettings
    for n, w in (('Potencia', pot), ('Alimentacion', ali)):
        c = ns.GetNetClassByName(n); c.SetTrackWidth(mm(w))

def zone(b, netname, rect, prio, layer=pcbnew.F_Cu):
    z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(net(b, netname)); z.SetAssignedPriority(prio)
    z.SetLocalClearance(mm(0.3)); z.SetMinThickness(mm(0.3))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    ol = z.Outline(); ol.NewOutline()
    x0, y0, x1, y1 = rect
    for (x, y) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)): ol.Append(int(x), int(y))
    b.Add(z); return z

def pads_bbox(b, items, margin=1.2):
    xs, ys = [], []
    for ref, nums in items:
        f = b.FindFootprintByReference(ref)
        for p in f.Pads():
            if nums is None or p.GetNumber() in nums:
                bb = p.GetBoundingBox(); xs += [bb.GetLeft(), bb.GetRight()]; ys += [bb.GetTop(), bb.GetBottom()]
    m = mm(margin)
    return (min(xs) - m, min(ys) - m, max(xs) + m, max(ys) + m)

POWER = [  # (red, prioridad, pads del grupo)
    ('/BUCK_SW', 5, [('U2', ['1', '2', '3', '4', '5']), ('L1', ['1'])]),
    ('/BUS_36V', 4, [('F1', ['2']), ('D1', ['1']), ('C1', ['1']), ('C2', ['1']), ('C4', ['1']), ('C5', ['1']), ('C6', ['1']), ('U2', ['20', '21', '22'])]),
    ('/BUCK_VOUT', 3, [('L1', ['2']), ('C9', ['1']), ('C10', ['1']), ('C11', ['1']), ('U3', ['1', '2'])]),
    ('/LED_POS', 2, [('U3', ['17', '18']), ('C14', ['1']), ('D3', ['1']), ('J2', ['1'])]),
    ('/LED_NEG', 2, [('J2', ['2']), ('Q1', ['2']), ('D3', ['2'])]),
    ('/DC_IN', 2, [('J1', ['1']), ('F1', ['1'])]),
]

def stitching(b, step=3.0, clear=0.25):
    """Vías de unión GND en rejilla, solo donde no tocan cobre de otras redes."""
    g = net(b, '/GND'); added = []
    r = mm(0.3 + clear)
    others = [t for t in b.GetTracks() if t.GetNetname() != '/GND']
    pads = [p for f in b.Footprints() for p in f.Pads() if p.GetNetname() != '/GND' or p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]
    holes = [f.GetPosition() for f in b.Footprints() if f.GetReference().startswith('H')]
    keep = [z for z in b.Zones() if z.GetIsRuleArea()]
    gv = [t for t in b.GetTracks() if t.GetNetname() == '/GND' and t.Type() == pcbnew.PCB_VIA_T]
    y = 2.0
    while y <= 73.0:
        x = 2.0
        while x <= 98.0:
            p = pcbnew.VECTOR2I(mm(OX + x), mm(OY + y)); ok = True
            if any((p - h).EuclideanNorm() < mm(4.0) for h in holes): ok = False
            if ok and any(z.Outline().Contains(p) for z in keep): ok = False
            if ok and any(t.HitTest(p, r) for t in others): ok = False
            if ok and any(pd.HitTest(p, r + mm(0.1)) for pd in pads): ok = False
            if ok and any((p - v.GetPosition()).EuclideanNorm() < mm(2.0) for v in gv + added): ok = False
            if ok: added.append(add_via(b, p.x, p.y, g))
            x += step
        y += step
    return added


def fix_vias_tracks(b):
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            t.SetDrill(mm(0.3)); t.SetWidth(max(t.GetWidth(pcbnew.F_Cu), mm(0.6)))
        # anchos mínimos de Freerouting (0,187 mm) se aceptan: JLCPCB fabrica desde 0,127 mm

def tie_qfn_gnd(b):
    """Une con pista corta las patillas GND de U2/U3 con su almohadilla expuesta."""
    g = net(b, '/GND')
    for ref, ep, pins in (('U2', '31', ['17', '19']), ('U3', '25', ['8', '15'])):
        f = b.FindFootprintByReference(ref)
        e = [p for p in f.Pads() if p.GetNumber() == ep][0].GetPosition()
        for p in f.Pads():
            if p.GetNumber() in pins:
                s = p.GetPosition()
                bb = p.GetBoundingBox(); end = pcbnew.VECTOR2I(e.x, s.y) if bb.GetWidth() > bb.GetHeight() else pcbnew.VECTOR2I(s.x, e.y)
                tr = pcbnew.PCB_TRACK(b); tr.SetStart(s); tr.SetEnd(end); tr.SetWidth(mm(0.25))
                tr.SetLayer(pcbnew.F_Cu); tr.SetNet(g); b.Add(tr)

def gnd_zones_solid(b):
    for z in b.Zones():
        if z.GetNetname() == '/GND' and not z.GetIsRuleArea():
            z.SetPadConnection(pcbnew.ZONE_CONNECTION_THT_THERMAL)
            z.SetThermalReliefSpokeWidth(mm(0.5)); z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)

def via_near_pads(b, refs_pads):
    """Añade una vía GND junto a cada pad indicado (ref, num), unida con pista corta."""
    g = net(b, '/GND'); r = mm(0.55)
    others = [t for t in b.GetTracks() if t.GetNetname() != '/GND']
    pads = [p for f in b.Footprints() for p in f.Pads() if p.GetNetname() != '/GND']
    n = 0
    for ref, num in refs_pads:
        pad = [p for p in b.FindFootprintByReference(ref).Pads() if p.GetNumber() == num][0]
        c = pad.GetPosition(); done = False
        for d in (1.3, 1.6, 2.0, 2.5, 3.0, 3.5, 4.0):
            for ang in range(0, 360, 15):
                import math
                p = pcbnew.VECTOR2I(int(c.x + mm(d) * math.cos(math.radians(ang))), int(c.y + mm(d) * math.sin(math.radians(ang))))
                seg_ok = True
                for k in range(1, 6):
                    q = pcbnew.VECTOR2I(int(c.x + (p.x - c.x) * k / 5), int(c.y + (p.y - c.y) * k / 5))
                    if any(t.HitTest(q, mm(0.35)) for t in others) or any(pd.HitTest(q, mm(0.35)) for pd in pads): seg_ok = False; break
                if not seg_ok: continue
                if any(t.HitTest(p, r) for t in others) or any(pd.HitTest(p, r) for pd in pads): continue
                add_via(b, p.x, p.y, g)
                tr = pcbnew.PCB_TRACK(b); tr.SetStart(c); tr.SetEnd(p); tr.SetWidth(mm(0.4)); tr.SetLayer(pcbnew.F_Cu); tr.SetNet(g); b.Add(tr)
                done = True; n += 1; break
            if done: break
        if not done: print('Sin hueco para vía junto a', ref, num)
    return n


def via_in_islands(b):
    """Pone una vía GND en cada trozo de plano GND de F.Cu que no tenga vía ni pad pasante."""
    g = net(b, '/GND'); n = 0
    gvias = [t.GetPosition() for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == '/GND']
    pth = [p.GetPosition() for f in b.Footprints() for p in f.Pads() if p.GetNetname() == '/GND' and p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]
    for z in b.Zones():
        if z.GetNetname() != '/GND' or z.GetLayer() != pcbnew.F_Cu or z.GetIsRuleArea(): continue
        polys = z.GetFilledPolysList(pcbnew.F_Cu)
        for i in range(polys.OutlineCount()):
            one = pcbnew.SHAPE_POLY_SET(); one.AddOutline(polys.Outline(i))
            if any(one.Contains(p) for p in gvias + pth): continue
            bb = polys.Outline(i).BBox(); best = None
            step = mm(0.25); y = bb.GetTop()
            while y < bb.GetBottom() and best is None:
                x = bb.GetLeft()
                while x < bb.GetRight():
                    c = pcbnew.VECTOR2I(int(x), int(y))
                    if all(one.Contains(pcbnew.VECTOR2I(int(c.x + dx), int(c.y + dy))) for dx in (-mm(0.45), 0, mm(0.45)) for dy in (-mm(0.45), 0, mm(0.45))):
                        best = c; break
                    x += step
                y += step
            if best is not None:
                add_via(b, best.x, best.y, g); n += 1
            else:
                print('Isla GND sin sitio para vía en', bb.Centre().x / 1e6, bb.Centre().y / 1e6)
    return n


def tidy_silk(b):
    """Referencias de serigrafía a 0,8 mm para reducir solapes."""
    for f in b.Footprints():
        r = f.Reference(); r.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8))); r.SetTextThickness(mm(0.12))


# Pistas de potencia trazadas a mano (coordenadas en mm desde la esquina superior izquierda).
# (red, ancho, [puntos])  -- se bloquean para que el enrutador automático no las mueva.
POWER_TRACKS = [
    ('/DC_IN', 2.5, [(6.0, 62.0), (6.0, 66.5), (10.0, 70.5), (13.5, 70.5), (18.5, 70.5)]),
    ('/BUS_36V', 2.0, [(28.5, 70.5), (33.5, 70.5), (35.72, 70.5)]),
    ('/BUS_36V', 1.5, [(35.72, 71.5), (35.72, 62.0)]),
    ('/BUS_36V', 1.0, [(35.72, 62.0), (41.14, 62.0)]),
    ('/BUS_36V', 0.6, [(38.6, 59.95), (38.6, 62.0)]),
    ('/BUS_36V', 1.5, [(30.0, 62.0), (35.72, 62.0)]),
    ('/BUS_36V', 1.0, [(22.15, 58.0), (28.0, 58.0), (30.0, 60.0), (30.0, 62.0)]),
    ('/BUCK_SW', 0.6, [(45.9, 62.9), (45.9, 64.5)]),
    ('/BUCK_SW', 1.2, [(45.9, 64.25), (52.95, 64.25)]),
    ('/BUCK_SW', 0.6, [(49.15, 62.6), (49.15, 64.25)]),
    ('/BUCK_VOUT', 1.5, [(64.05, 62.0), (68.0, 62.0)]),
    ('/BUCK_VOUT', 1.0, [(68.0, 62.0), (69.9, 61.0)]),
    ('/BUCK_VOUT', 0.6, [(69.9, 60.75), (69.9, 62.75)]),
    ('/BUCK_VOUT', 0.6, [(69.3, 58.75), (69.9, 60.2), (69.9, 60.75)]),
    ('/BUCK_VOUT', 1.5, [(64.3, 63.0), (64.53, 70.3)]),
    ('/BUCK_VOUT', 1.0, [(64.05, 60.0), (64.5, 53.0), (66.0, 49.5)]),
    ('/LED_POS', 1.0, [(76.3, 61.25), (76.3, 59.05)]),
    ('/LED_POS', 1.5, [(76.3, 59.05), (78.5, 59.05)]),
    ('/LED_POS', 2.0, [(78.5, 59.05), (80.5, 58.5), (94.0, 58.5)]),
    ('/LED_POS', 1.5, [(86.5, 59.5), (86.5, 58.5)]),
    ('/LED_NEG', 2.0, [(94.0, 63.58), (86.5, 63.58), (86.04, 66.5), (86.04, 70.3)]),
    ('/BUCK_BOOT', 0.25, [(44.86, 62.0), (46.4, 62.0), (47.25, 62.6)]),
    ('/BUCK_VCC', 0.25, [(44.86, 61.0), (46.95, 61.0), (46.95, 60.35)]),
    ('/VCC_5V', 0.3, [(44.86, 60.5), (45.9, 60.5), (45.9, 58.0)]),
]
STUBS = [  # (ref, pad, punto destino) a 0,25 mm desde patillas de QFN
    ('U2', '1', (45.9, 64.5)), ('U2', '2', (45.9, 64.0)), ('U2', '3', (45.9, 63.5)), ('U2', '4', (45.9, 63.0)), ('U2', '5', (45.9, 62.9)),
    ('U3', '1', (69.9, 60.75)), ('U3', '2', (69.9, 61.25)), ('U3', '5', (69.9, 62.75)),
    ('U3', '17', (76.3, 61.25)), ('U3', '18', (76.3, 60.75)),
]

def power_tracks(b):
    P = lambda x, y: pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))
    def seg(netname, w, a, c):
        tr = pcbnew.PCB_TRACK(b); tr.SetStart(a); tr.SetEnd(c); tr.SetWidth(mm(w)); tr.SetLayer(pcbnew.F_Cu)
        tr.SetNet(net(b, netname)); tr.SetLocked(True); b.Add(tr)
    segs = []  # (red, ancho, a, c) en mm
    for netname, w, pts in POWER_TRACKS:
        for a, c in zip(pts, pts[1:]): segs.append((netname, w, a, c))
    for ref, num, dst in STUBS:
        p = [p for p in b.FindFootprintByReference(ref).Pads() if p.GetNumber() == num][0]
        a = (p.GetPosition().x / 1e6 - OX, p.GetPosition().y / 1e6 - OY)
        segs.append((p.GetNetname(), 0.25, a, dst))
    # Partir cada segmento en los puntos donde termina otro de la misma red (uniones en T):
    # el enrutador automático solo reconoce uniones en extremos.
    ends = {}
    for n, w, a, c in segs: ends.setdefault(n, set()).update([a, c])
    for n, w, a, c in segs:
        ax, ay = a; cx, cy = c; L2 = (cx - ax) ** 2 + (cy - ay) ** 2
        cuts = [0.0, 1.0]
        for (px, py) in ends[n]:
            if L2 == 0: break
            u = ((px - ax) * (cx - ax) + (py - ay) * (cy - ay)) / L2
            if 1e-6 < u < 1 - 1e-6:
                qx, qy = ax + u * (cx - ax), ay + u * (cy - ay)
                if (qx - px) ** 2 + (qy - py) ** 2 < 1e-6: cuts.append(u)
        cuts = sorted(set(cuts))
        for u0, u1 in zip(cuts, cuts[1:]):
            seg(n, w, P(ax + u0 * (cx - ax), ay + u0 * (cy - ay)), P(ax + u1 * (cx - ax), ay + u1 * (cy - ay)))

if __name__ == '__main__':
    b = pcbnew.LoadBoard(PCB)
    if sys.argv[1] == 'vias':
        power_tracks(b)
        smd_gnd = [(f.GetReference(), p.GetNumber()) for f in b.Footprints() for p in f.Pads()
                   if p.GetNetname() == '/GND' and p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and f.GetReference() not in ('U2', 'U3')]
        print('Vías de salida GND:', via_near_pads(b, smd_gnd))
        pcbnew.SaveBoard(PCB, b)
        set_widths(b, 0.3, 0.3)
        pcbnew.ExportSpecctraDSN(b, os.path.join(os.getcwd(), 'placa.dsn'))
        print('DSN exportado')
    elif sys.argv[1] == 'importar':
        assert pcbnew.ImportSpecctraSES(b, sys.argv[2])
        set_widths(b, 2.0, 0.6)
        for name, prio, items in POWER:
            zone(b, name, pads_bbox(b, items), prio)
        thermal_vias(b); tie_qfn_gnd(b); tidy_silk(b)
        fix_vias_tracks(b); gnd_zones_solid(b)
        ds = b.GetDesignSettings(); ds.m_TrackMinWidth = mm(0.15); ds.m_MinResolvedSpokes = 1
        vias = stitching(b)
        filler = pcbnew.ZONE_FILLER(b); filler.Fill(b.Zones())
        print('Vías en islas GND:', via_in_islands(b))
        filler.Fill(b.Zones())
        gz = [z for z in b.Zones() if z.GetNetname() == '/GND' and not z.GetIsRuleArea()]
        def in_plane(p, layer):
            return any(z.GetLayer() == layer and z.GetFilledPolysList(layer).Contains(p) for z in gz)
        quitar = [v for v in vias if not (in_plane(v.GetPosition(), pcbnew.F_Cu) and in_plane(v.GetPosition(), pcbnew.B_Cu))]
        for v in quitar: b.Remove(v)
        print('Vías de unión retiradas por no tocar ambos planos:', len(quitar))
        filler.Fill(b.Zones())
        pcbnew.SaveBoard(PCB, b)
        print('Importado; vías de unión candidatas:', len(vias))
