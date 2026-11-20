# Controlador de Acuario V1.0 · PCB (revisión B) y guía de fabricación

**Estado:** desarrollada y publicada para revisión. **No aprobada. No fabricada.** No hay pruebas de banco. No se ha hecho ningún pedido: solo tú decides si encargar y dónde.

## 1. Placa

| Dato | Valor |
|---|---|
| Tamaño | 100 × 75 mm, 2 capas, FR-4 de 1,6 mm, cobre de 1 oz (35 µm) |
| Componentes | 80 huellas (76 del esquema y 4 taladros M3). Montaje SMD en una sola cara (la superior) |
| Trazado | 604 pistas y 533 vías (unas 400 son vías de unión de masa). Ancho mínimo 0,187 mm, holgura mínima 0,2 mm, vía de 0,6/0,3 mm |
| Masa | Plano completo en la cara inferior y relleno de masa en la superior |
| Potencia | Pistas anchas trazadas a mano y bloqueadas (2,5 mm en la entrada; 1,2–2 mm en el bus de 36 V, la conmutación, la salida del buck y la salida a la luz). Cada red de potencia tiene además una zona de cobre continua: se ha comprobado que cada red forma **un solo trozo** que une todos sus pads de potencia |
| Antena del ESP32 | Sobresale 6 mm por el borde superior de la placa. Zona sin cobre en la parte que queda sobre la placa |
| Conectores | J1 (36 V) abajo a la izquierda, J2 (luz) a la derecha, J3/J4/J5 (RTC, sonda, módulo SSR) en el borde superior |

**Verificación (KiCad 9.0.9, `kicad-cli pcb drc --schematic-parity`, informe en `Control_Acuario_V1_0_DRC.rpt`):**
- 0 pads sin conectar, 0 cortocircuitos, 0 violaciones de holgura o anchura y 0 errores de huella.
- Sin diferencias entre el esquema y la placa.
- Quedan 42 avisos de serigrafía: textos superpuestos o encima de pads. Son estéticos: el fabricante recorta la serigrafía que cae sobre los pads.

**Cálculos de corriente (estimaciones, no medidas):**
- IPC-2221 en capa externa de 1 oz: una pista de 2 mm admite ≈ 5,3 A con +20 °C de calentamiento. Las zonas de cobre añaden sección.
- Las patillas de los QFN se conectan con tramos cortos de 0,25 mm, igual que en un diseño de referencia típico. Su calentamiento debe comprobarse en banco a 4,7 A.

## 2. Cambios del esquema hechos durante el trazado
- **C9:** 47 µF / 50 V → **220 µF / 35 V de baja ESR** (NXH35V220M8*11.5, LCSC C346959, 56 mΩ y 945 mA a 100 kHz). Con 400 kHz, la tabla 8-1 de TI para el LM76005 recomienda 150 µF a 12 V y 100 µF a 24 V; la revisión anterior se quedaba corta. El total queda muy por debajo del máximo de 800–1200 µF que indica TI.
- **C10/C11:** 22 µF → 10 µF / 50 V en 1210, porque el valor de 22 µF no está en el catálogo de JLCPCB.
- **F1:** portafusibles de pinzas 5 × 20 mm, fácil de reponer. Fusible **T5A**, elegido para la fuente de 24 V y 5 A del usuario.
- **L1:** huella con el patrón recomendado por Bourns (14,2 / 8,0 / 5,0 mm).
- **A1:** huella propia del zócalo del ESP32-DevKitC V4, hecha con las cotas oficiales de Espressif.
- ERC: 0 errores y 1 aviso de versión del símbolo TC4427, sin efecto eléctrico.

## 3. Archivos de fabricación (`fabricacion/`)
| Archivo | Uso |
|---|---|
| `Control_Acuario_V1_0_Gerber.zip` | Gerber y taladros Excellon: se sube tal cual a JLCPCB o PCBWay |
| `Control_Acuario_V1_0_BOM_JLCPCB.csv` | Lista de montaje SMD con códigos LCSC (41 líneas) |
| `Control_Acuario_V1_0_CPL_JLCPCB.csv` | Posiciones de montaje (65 componentes SMD, cara superior) |
| `Montaje_manual.txt` | Componentes que **no** monta el fabricante: los soldarás tú o son módulos externos |
| `gerber/` | Los mismos archivos sueltos y los mapas de taladros en PDF |

Para regenerarlos: `python3 herramientas/exportar_fabricacion.py`.

## 4. Coste orientativo (tarifas publicadas el 20/11/2026; NO es un presupuesto)

**JLCPCB, "Economic PCBA"** (precios en USD sin envío ni IVA). Las tarifas salen de su página de precios de montaje y los precios de componentes, de su catálogo:

| Concepto | 1 placa montada | 2 placas montadas |
|---|---|---|
| PCB desnuda (5 unidades, 2 capas, ≤ 100 × 100 mm), oferta publicada | ≈ 2 | ≈ 2 |
| Preparación del montaje | 8,18 | 8,18 |
| Plantilla de pasta | 1,53 | 1,53 |
| Componentes "extendidos" (16 × 3,07) | 49,12 | 49,12 |
| Rayos X de QFN (U2 y U3, 1,64 por pieza) | 3,28 | 6,56 |
| Uniones SMT (≈ 210 por placa × 0,0016) | ≈ 0,34 | ≈ 0,67 |
| Componentes SMD (precios de 1 unidad) | ≈ 13,6 | ≈ 27,2 |
| **Total aproximado** | **≈ 78 $** | **≈ 95 $** |

- La segunda placa cuesta solo unos 17 $ más, porque casi todo es coste fijo. La página publica además un "pre-reflow soldering" de 0,016 $ por unión; si se aplicara, sumaría unos 3–7 $.
- No he podido confirmar si el montaje económico admite una sola placa: el configurador lo dirá al pedir. Si exige un mínimo de 2, **la segunda sale casi al precio de los componentes**.
- Faltan el envío a España y el **IVA del 21 %**, que JLCPCB cobra en el pedido.

**PCBWay:**
- Tarifas publicadas: 5 $ por 10 PCB desnudas y montaje "desde 29 $".
- No cobra 3,07 $ por cada componente extendido, pero los componentes los compra PCBWay y entran en su presupuesto.
- **Sin subir los archivos no se puede saber cuál sale más barato.** Lo correcto es pedir las dos cotizaciones con el mismo ZIP: mismas medidas, cobre y número de placas montadas.

**Aparte (no lo monta el fabricante):** convertidor Traco TSR 1-4850WI (no está en JLCPCB; Mouser o Farnell), Q1 STP55NF06L, C1, C9, las dos bornas MKDS, las pinzas y el fusible 5 × 20 T5A, las tiras de pines y dos tiras hembra 1 × 19 para el DevKit, el ESP32-DevKitC-32E, el módulo DS3231, la sonda DS18B20, la fuente de 36 V (≥ 3 A) y tu módulo de 2 SSR. Son componentes de inserción fáciles de soldar a mano.

## 5. Cómo pedirlo en JLCPCB (cuando apruebes la revisión)
1. En jlcpcb.com, entra en **Order now** y sube `fabricacion/Control_Acuario_V1_0_Gerber.zip`.
2. Opciones de la PCB: 2 capas, FR-4, 1,6 mm, 5 unidades, color verde (el más barato), acabado HASL sin plomo y cobre de 1 oz.
3. Activa **PCB Assembly**: Economic, cara superior y el número de placas montadas (1 o 2). Deja que JLCPCB añada los taladros de utillaje.
4. Sube la BOM `Control_Acuario_V1_0_BOM_JLCPCB.csv` y el CPL `Control_Acuario_V1_0_CPL_JLCPCB.csv`. Comprueba que los 41 componentes aparecen emparejados y con stock.
   - Tras la revisión final, U4 (MCP4725A1) y R2/R3 tienen stock holgado. Vigila el TPS26632 (U3), con 93 unidades al consultarlo.
5. En la vista previa de colocación, **revisa la orientación de la patilla 1** de U2, U3, U4, U5, D1, D3, D5, D2, D4, Q2–Q5 y L1. JLCPCB a veces necesita corregir el giro. Puedes marcar "Confirm Parts Placement" (0,45 $) para que te lo enseñen antes de montar.
6. Para comparar, haz lo mismo en PCBWay (PCB Assembly → Quote) con los mismos archivos.
7. **No pagues hasta revisar el presupuesto completo.** Yo no hago pedidos ni autorizo la fabricación.

## 6. Pendiente antes de dar la placa por buena
- Tu revisión de la placa (colocación, conectores y medidas de la caja).
- Pruebas de banco del plan de pruebas: arranque, consigna 5–24 V, disparo a 4,7 A, temperaturas de U2, U3, L1 y Q1, PWM y la integración de los SSR por un profesional cualificado.
- Firmware del ESP32 (más adelante) y el perfil de hardware en Acuaris.

## 7. Herramientas usadas
- KiCad 9.0.9 (`kicad-cli` y el módulo Python `pcbnew`) para el esquema, el ERC, la PCB, el DRC, los Gerber y los renders.
- **Freerouting 2.4.1** (GPL-3.0, de Maven Central, con la suma de control verificada), con OpenJDK 25, solo para el trazado automático de señales. **No forma parte del proyecto**; aprobado por el usuario para esta tarea. La sesión resultante está en `herramientas/Control_Acuario_V1_0.ses`.
- Scripts reproducibles en `herramientas/`: `generar_pcb.py` (colocación), `trazar_pcb.py` (potencia, vías e importación del trazado) y `exportar_fabricacion.py`.

## 8. Alimentación con una fuente de 24 V (la que tiene el usuario)
La placa funciona igual con una fuente aislada de 24 V que con una de 36 V, sin cambiar componentes. Todos los cálculos siguientes son estimaciones con datos nominales, pendientes de medir:
- **Tensión máxima de salida:** el buck reduce tensión, así que con 24 V de entrada la salida máxima a plena carga ronda **21–22 V**, no 24 V. Cálculo: ciclo máximo ≈ 0,95 con t_OFF,mín de 130 ns a 400 kHz, menos las caídas en el MOSFET interno, en L1 y en U3. Para tus dicroicas, que trabajan a 10 V y admiten 12–24 V, no es un problema. Con DAC = 0, la consigna (23,9 V) supera lo alcanzable: el firmware debe limitar el código del DAC.
- **Corriente de la fuente:** potencia de salida / 0,9 / 24 V, más ≈ 0,3 A del ESP32 y los SSR.
  - 56 W (siete dicroicas a 12 V): ≈ 2,9 A.
  - 75 W (máximo previsto): ≈ 3,8 A. Para llegar al máximo, la fuente debe dar **4 A o más (≈ 100 W)**.
- **Fusible:** con 24 V y la carga cerca de 75 W, la corriente de entrada (≈ 3,8 A) quedaría muy cerca de un T4A. Por eso el diseño pasa a **T5A**.
- **Fuente del usuario: 24 V y 5 A como mínimo (120 W).** Cubre las 7 dicroicas (≈ 2,9 A) y el máximo de 75 W (≈ 3,8 A) con margen.
- **Convertidor de 5 V (Traco TSR 1-4850WI):** entrada de 9 a 72 V según su hoja de datos, así que funciona a 24 V.
- **TVS SMBJ40A:** con 24 V queda más margen que con 36 V.
- La fuente debe ser **aislada (tipo SELV)**, como las fuentes de LED comerciales.
