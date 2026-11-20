# Controlador de Acuario V1.0 · Revisión B del esquema

**Estado:** desarrollada y publicada en la rama `acuario-v1-esquema` para revisión. **No aprobada.** Sin pruebas de banco, sin PCB, sin DRC. La revisión A sigue recuperable en el commit `4b8fed1` y en `Control_Acuario_V1_0_Revision_A.zip`.

Herramientas: KiCad 9.0.9 (`kicad-cli`) en Ubuntu 24.04 (entorno en la nube), hojas de datos oficiales de TI y Bourns descargadas el 20/11/2026, catálogo de JLCPCB/LCSC consultado el 20/11/2026. **Hechos** = leído en la hoja de datos o comprobado con KiCad. **Cálculo** = hecho a partir de datos nominales; requiere medida.

## 1. ERC

| Revisión | KiCad | Resultado |
|---|---|---|
| A (re-ejecutado) | 9.0.9 | 0 errores, 1 aviso |
| B | 9.0.9 | 0 errores, 1 aviso |

El aviso es `lib_symbol_mismatch` de U5 (TC4427): el símbolo guardado procede de la librería de KiCad 9.0.2. No afecta a las conexiones. Las redes nuevas (LED_UVLO, LED_ILIM_B, ESP_5V) se comprobaron en la netlist exportada.

## 2. Errores corregidos

### 2.1 U3 nunca habría conectado la salida por debajo de ~15,5 V (crítico)
**Hecho (TPS2663, tabla 5-1 y características eléctricas):** "Connect UVLO pin to GND pin to select the internal default threshold"; con UVLO a 0 V el umbral de IN_SYS es **15,1–15,46–15,9 V** (subida) y 14,47 V (bajada). IN_SYS está unido a la salida del buck. Con la revisión A, las dicroicas a 10–12 V no habrían recibido tensión.
**Corrección:** divisor R27 100 kΩ / R28 33 kΩ desde BUCK_VOUT. Umbral externo 1,2 V → **arranque ≈ 4,84 V, parada ≈ 4,52 V** (cálculo). Mínimo operativo de U3: 4,5 V (hecho).

### 2.2 Corriente de 4,7 A sin disparos prematuros
**Hecho:** I_LIM = 18 / R_ILIM (kΩ), tolerancia ±7 %. Con 3,83 kΩ (rev. A) el mínimo garantizado era 4,37 A: las 7 dicroicas a 12 V (4,67 A teóricos) podían disparar.
**Corrección:** R5 3,3 kΩ + R29 150 Ω = 3,45 kΩ → **5,22 A nominal, 4,85 A mínimo, 5,58 A máximo** (cálculo, ±7 % + resistencias 1 %). Así 4,7 A queda garantizado. El margen superior lo cubre el límite propio del LM76005 (valle del FET inferior 4,5–5,1–5,8 A, hecho), que en sobrecarga entra en hiccup.
Fast-trip del TPS26632 a 2 × I_OL, límite de duración en limitación 129–202 ms, MODE abierto = enclavado (hechos). Se mantiene enclavado: el rearme exige ciclar SHDN (GPIO27).

### 2.3 Potencia
R6 69,8 kΩ → **68 kΩ** (componente básico de JLCPCB): P_LIM ≈ 68 W, ±6 % → 63,9–72,1 W (cálculo sobre la tabla del fabricante). No supera 75 W en ningún caso. A 12 V y 4,7 A se piden 56,4 W: no actúa el límite de potencia.

### 2.4 Otros cambios
- **D1:** SMBJ36A → **SMBJ40A** y símbolo corregido a unidireccional (la rev. A usaba símbolo bidireccional). Con 36 V nominales, la tensión de trabajo de 36 V del SMBJ36A no dejaba margen. Entrada del LM76005: 60 V de trabajo, 65 V de transitorio (hecho). Tensión de bloqueo del SMBJ40A a corriente de pico: 64,5 V (valor típico de la familia, por confirmar con el fabricante elegido).
- **JP1 → D5 (SS34):** evita que el USB y la fuente de 5 V se enfrenten aunque se olvide abrir el puente. El DevKit recibe ≈4,6 V (cálculo con 0,4 V de caída). Su regulador de 3,3 V debe mantener la tensión con ese margen: **ensayo de banco** con Wi-Fi transmitiendo.
- **Coste:** C3 pasa a 10 µF/25 V 0805, D3 a SS54 en SMA (40 V, 5 A), R7 a 6,8 kΩ y R11 a 8,2 kΩ. Todos son componentes básicos de JLCPCB, que no pagan tarifa de carga. R7 6,8 kΩ: con 5,58 A, V_IMON ≈ 1,14 V (ganancia 27,9 µA/A, hecho). R11 8,2 kΩ: 24 V → 1,82 V en el ADC.

## 3. Comprobaciones sin cambio
- **Consigna:** V_FB = 0,987–1,006–1,017 V (hecho). VBUCK = 23,86 − 6,09 × VDAC con R2 = 3,0 kΩ y R3 = 8,2 kΩ (cambio por stock en la revisión final; antes 2,94 kΩ / 8,45 kΩ): unos 3,8 V con DAC a 3,3 V (U3 solo conecta por encima de ≈ 4,8 V) y 23,9 V con DAC a 0 V (cálculo). El MCP4725 usa su alimentación de 3,3 V como referencia, así que la tolerancia del 3,3 V del DevKit pasa a la salida (≈ ±0,2 V con un 2 %). Se compensa calibrando con LED_V_ADC.
- **Seguridad de la consigna:** el DAC a 0 V da la tensión **máxima**. Si el ESP32 se reinicia, R4 y R8 bajan EN y SHDN y la salida se apaga. Medidas obligatorias en firmware: grabar 4095 en la EEPROM del MCP4725 (U4 es ahora el MCP4725A1: dirección I²C 0x62) (arranque al mínimo), limitar el código mínimo según la luminaria configurada y apagar si LED_V_ADC supera la consigna.
- **LM76005:** RT abierto → 400 kHz (350–450 kHz); SS/TRK abierto → arranque suave de 6,3 ms; SYNC/MODE a GND → modo automático PFM/DCM con carga ligera; BIAS a 5 V permitido (hechos). En modo automático, la salida baja despacio sin carga al reducir la consigna (R24 3,3 kΩ la descarga). Con lámpara conectada no afecta.
- **L1 SRP1265A-150M:** 15 µH, R_DC 23,2 mΩ típ. / 28 mΩ máx., I_rms 9 A, I_sat 12,5 A (hecho). Pico ≈ 5,4–5,6 A a 4,7 A: margen holgado. Pérdidas ≈ 0,6 W (cálculo).
- **Térmica U2 a 12 V / 4,7 A (estimación):** ≈ 0,7 W en el FET superior, 0,7 W en el inferior y ≈ 0,7 W de conmutación. Unos 2 W con R_θJA 29,6 °C/W (placa de evaluación de TI) dan ≈ +60 °C. **Ajustado:** se resolverá con cobre y vías en la PCB. Si hiciera falta, se puede bajar a 300 kHz con R_T. Hay que medirlo en la caja.
- **U3 a 4,7 A:** R_ON 33–45 mΩ a 85 °C → 0,7–1,0 W (cálculo).
- **ESP32:** ADC en ADC1 (GPIO34/35, compatibles con Wi-Fi), SSR en GPIO16/17 (no son pines de arranque), I²C en 21/22. El ESP32 clásico (WROOM-32E) admite Bluetooth clásico SPP, necesario para el protocolo VirtuinoCM de Acuaris.

## 4. Luminarias actuales (información del usuario)
Las 7 dicroicas admiten 12–24 V, admiten mal el PWM y trabajan hoy a **10 V en continua** para limitar la corriente. El modo continuo es el principal: 10 V está dentro del rango (U3 arranca desde ≈4,8 V). El PWM queda para otras luminarias. Si se probara con estas, hay que medir los picos de cada pulso, porque el fast-trip de U3 (2 × I_OL en 3,2 µs, hecho) podría enclavarlo.

## 5. Mando de los SSR (módulo DollaTek del usuario)
**Hechos (ficha Amazon B07DK3ZZSL):** 2 canales, alimentación 5 V / 160 mA, entrada 0–2,5 V = OFF y 3,3–5 V = ON (**disparo a nivel alto**), relés Omron, carga AC 100–240 V 2 A, fusible de 2 A en salida.
- Los mandos de la rev. A (5 V + retorno conmutado) **no servían** para este módulo. Una salida directa del ESP32 (3,3 V nominal) quedaría justo en el umbral de 3,3 V.
- **Rev. B:** J5 único de 4 vías (DC+, DC−, CH1 bomba, CH2 calentador) y etapa de 5 V en alto por canal: Q2/Q3 (N) + Q4/Q5 (P, AO3401A), R30/R31 10 kΩ y R32/R33 47 kΩ. Todos son básicos de JLCPCB. Al arrancar o reiniciar, el GPIO queda en alta impedancia: R21/R23 apagan Q2/Q3, R30/R31 apagan Q4/Q5 y R32/R33 llevan CH a 0 V → **SSR apagados**. J6 desaparece.
- El módulo toma unos 160 mA del carril de 5 V (TSR de 1 A): ESP32 (≈0,25 A típicos, picos mayores) + módulo + resto ≈ 0,5 A (estimación).
- **Riesgos de red (validación cualificada):** calentador de 350 W ≈ 1,52 A a 230 V en un SSR de 2 A con fusible de 2 A: margen escaso por temperatura (comprobar calentamiento o usar otro SSR con disipador). Bomba de 10 W ≈ 43 mA: no he podido leer la hoja de datos Omron (descarga bloqueada). Si el SSR tiene corriente mínima de carga o fuga apreciable, la bomba puede no arrancar o zumbar en reposo: hay que comprobarlo en banco por el profesional.

## 6. PCB
La placa está trazada y las huellas pendientes están resueltas. C9 pasa a 220 µF / 35 V de baja ESR y C10/C11 a 10 µF / 50 V. Detalles, DRC, costes y cómo pedirla en `Control_Acuario_V1_0_PCB_y_Fabricacion.md`. Fuente: el usuario usará la suya de 24 V. Es válida, con la salida limitada a ≈ 21–22 V; detalles en la sección 8 de la guía de fabricación.

## 7. Coste orientativo (tarifas publicadas, no presupuesto)
Tarifas JLCPCB "Economic PCBA" (página oficial, actualizada el 22/10/2026): preparación 8,18 $, plantilla 1,53 $, **3,07 $ por cada componente extendido distinto**, rayos X de QFN 1,64 $/unidad, mano de obra de soldadura manual 3,58 $ por pedido.
- Componentes SMD extendidos de la rev. B: 16 (Q4/Q5 y sus resistencias son básicos) → ≈ 49 $ de tarifa por pedido, el mayor coste para 1–2 placas.
- Componentes por placa (precios JLCPCB de 1 unidad): ≈ 13 $.
- Fuera de JLCPCB: TSR 1-4850WI, DevKit, RTC, sonda, fuente de 36 V y F1.
La comparativa con PCBWay, portes e IVA se hará con los archivos de fabricación (paso 4 del encargo).
