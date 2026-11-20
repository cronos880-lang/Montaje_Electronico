"""Rótulos de serigrafía (cara superior) para conectores, fusible y orientación.
Idempotente: borra los textos de placa en F.SilkS y los vuelve a crear.
Uso: python3 herramientas/serigrafia.py
"""
import os, pcbnew
PCB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Control_Acuario_V1_0.kicad_pcb')
mm = pcbnew.FromMM; OX = OY = 100.0
# (texto, x, y, altura mm, rotación)
TEXTS = [
    # Sonda J4
    ('3V3', 36.5, 5.9, 0.8, 0), ('DQ', 39.04, 5.9, 0.8, 0), ('GND', 41.58, 5.9, 0.8, 0),
    ('SONDA', 39.04, 7.6, 0.9, 0),
    # Reloj J3
    ('3V3', 46.5, 5.9, 0.8, 0), ('GND', 49.04, 5.9, 0.8, 0), ('SDA', 51.58, 5.9, 0.8, 0), ('SCL', 54.12, 5.9, 0.8, 0),
    ('RELOJ DS3231', 50.31, 7.6, 0.9, 0),
    # Módulo SSR J5
    ('5V', 60.0, 5.9, 0.8, 0), ('GND', 62.54, 5.9, 0.8, 0), ('CH1', 65.08, 5.9, 0.8, 0), ('CH2', 67.62, 5.9, 0.8, 0),
    ('MODULO SSR', 63.81, 7.6, 0.9, 0), ('CH1 BOMBA  CH2 CALENTADOR', 63.81, 9.1, 0.8, 0),
    # Entrada J1
    ('+VIN', 13.0, 62.0, 0.9, 0), ('GND', 13.0, 56.9, 0.9, 0), ('ENTRADA 24-36V', 15.4, 59.5, 0.8, 90),
    # Salida de luz J2
    ('SALIDA LUZ', 94.0, 52.4, 1.0, 0), ('+ arriba  - abajo', 94.0, 54.1, 0.8, 0),
    # Fusible
    ('FUSIBLE T4A 5x20', 17.5, 66.3, 0.8, 0),
    # DevKit
    ('ESP32-DevKitC: USB abajo', 15.3, 50.6, 0.8, 0),
    # Título
    ('CONTROLADOR ACUARIO V1.0 rev.B', 60.0, 22.0, 1.4, 0),
]

def main():
    b = pcbnew.LoadBoard(PCB)
    for d in list(b.GetDrawings()):
        if isinstance(d, pcbnew.PCB_TEXT) and d.GetLayer() == pcbnew.F_SilkS:
            b.Remove(d)
    for s, x, y, h, rot in TEXTS:
        t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetLayer(pcbnew.F_SilkS)
        t.SetPosition(pcbnew.VECTOR2I(mm(OX + x), mm(OY + y)))
        t.SetTextSize(pcbnew.VECTOR2I(mm(h), mm(h))); t.SetTextThickness(mm(max(0.12, h * 0.15)))
        t.SetTextAngleDegrees(rot); b.Add(t)
    pcbnew.SaveBoard(PCB, b); print('Rótulos:', len(TEXTS))

if __name__ == '__main__':
    main()
