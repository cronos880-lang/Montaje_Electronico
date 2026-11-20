# Controlador de Acuario V1.0 · Revisión final antes del pedido (revisión B)

**Estado:** revisión hecha y correcciones aplicadas. **No aprobada, no fabricada, no probada en banco.** Esta revisión reduce el riesgo, pero no sustituye a las pruebas.

## Método
1. Se exportó del esquema la conexión de cada patilla de cada componente (netlist de KiCad 9.0.9).
2. Se contrastó cada integrado con su hoja de datos oficial y cada conector con su uso.
3. En la PCB se comprobaron disipación, desacoplos, stock en JLCPCB, DRC y paridad con el esquema.

## Comprobado y correcto
| Componente | Comprobación | Fuente |
|---|---|---|
| U2 LM76005 | SW 1-5 a L1; BOOT con 470 nF (pide 470 nF); VCC con 2,2 µF (pide 2,2 µF); NC 7 y 23 libres; NC 19, 27-30 a masa; RT libre (400 kHz); SS libre (6,3 ms); SYNC/MODE a masa (modo automático); EN con pull-down y mando del ESP32; PVIN 20-22; PGND 24-26; AGND y almohadilla a masa | Hoja de datos TI, tabla de patillas |
| U3 TPS26632 | IN 1-2 e IN_SYS 5 unidos; B_GATE y DRV libres (sin FET externo); UVLO con divisor (≈ 4,8 V); ILIM 3,45 kΩ (≥ 3 kΩ); PLIM 68 kΩ (60,4–150 kΩ); dVdT 10 nF (mínimo 10 nF, ≈ 5 V/ms); SHDN 0–5 V, umbral ≤ 2 V, pull-down 10 kΩ; IMON 6,8 kΩ (≥ 1 kΩ); FLT de drenador abierto con pull-up a 3,3 V; MODE libre (enclavado); OUT 17-18 | Hoja de datos TI |
| ESP32-DevKitC | Orden de las dos filas igual a las tablas oficiales de Espressif, con la antena hacia arriba. ADC en GPIO34/35/39 (solo entrada, ADC1, compatibles con Wi-Fi). Pines de arranque (0, 2, 5, 12, 15) sin usar. GPIO16/17 libres en la versión 32E | docs.espressif.com |
| U4 MCP4725 | 1 VOUT, 2 VSS, 3 VDD, 4 SDA, 5 SCL, 6 A0 a masa; 3,3 V | Símbolo y huella oficiales de KiCad |
| U5 TC4427 | IN_A del PWM con pull-down; IN_B a masa; OUT_A a la puerta de Q1 por 22 Ω; VDD 5 V | Símbolo oficial de KiCad |
| Q1–Q5 | TO-220 G-D-S; SOT-23 G-S-D (AO3400A/AO3401A); los mandos de SSR quedan apagados al arrancar | Símbolos y huellas oficiales |
| Diodos | D1 cátodo a 36/24 V; D3 cátodo a LED+ (rueda libre); D4 BAT54S como recorte 0–3,3 V del ADC; D5 aísla el USB; D2 cátodo a la línea de la sonda | — |
| Tensiones de los condensadores | Entrada 63/100 V; salida 35/50 V (máx. 24 V); BOOT y VCC 16 V | — |
| Disipación | R24 0,17 W en 2010; R19 58 mW en 1206; Q1 ≈ 0,44 W a 4,7 A; U3 0,7–1,0 W | Cálculo |
| Conectores | J3 RTC, J4 sonda, J5 módulo SSR y J1/J2 potencia, con rótulos de pines en serigrafía | — |

## Defectos encontrados en esta revisión y corregidos
1. **Faltaba el condensador de 1 µF junto a BIAS (U2, patilla 9).** TI lo pide expresamente y el más cercano estaba a 35 mm. C20 (1 µF) pasa a 4,6 mm de BIAS, con pista directa.
2. **Vías térmicas incompletas:** solo 5 de 8 en U2 y 3 de 9 en U3. El enrutador automático había pasado pistas por la cara inferior bajo esos integrados, cortando el plano de masa que los refrigera. Se prohíben pistas en la cara inferior bajo sus almohadillas térmicas. Ahora están las 8 y las 9 vías.
3. **Riesgo de stock en JLCPCB:** MCP4725A0 (4 uds), R2 de 2,94 kΩ al 0,1 % (5) y R3 de 8,45 kΩ al 0,1 % (7). Con las mermas de montaje el pedido podía fallar. Cambios:
   - **U4 → MCP4725A1T-E/CH** (C61423, 772 uds). Es idéntico y en la misma huella; solo cambia la **dirección I²C a 0x62** (dato para el firmware).
   - **R2 → 3,0 kΩ 0,1 %** (C728652, > 100 000 uds) y **R3 → 8,2 kΩ 0,1 %** (C351543, > 10 000 uds). Nueva consigna: **VBUCK ≈ 23,86 − 6,09 × VDAC** (antes 23,88 − 5,91 × VDAC). El máximo apenas cambia (≈ 23,9 V con DAC = 0).
4. **D2:** el supresor elegido es unidireccional y el símbolo era bidireccional. Se corrige el símbolo; la orientación ya era correcta (cátodo a la sonda).

## Riesgos que quedan (solo se resuelven con la placa en la mano)
- **Orientación de montaje en JLCPCB:** revisar la vista previa (patilla 1 de U2, U3, U4, U5, D1–D5, Q2–Q5 y L1) o pedir "Confirm Parts Placement".
- **Regulación:** estabilidad de la consigna con el DAC, temperatura a 4,7 A y respuesta al PWM. Hay que medirlas según el plan de pruebas.
- **PWM con lámparas que llevan condensador o driver interno:** el disparo rápido de U3 puede enclavar la salida. Con tus dicroicas en continua a 10 V no aplica.
- **Bomba de 10 W con el SSR Omron del módulo:** posible problema de corriente mínima o de fuga. Es de la parte de 230 V, que valida un profesional.
- **Firmware pendiente.** Requisitos para él:
  - Grabar 4095 en la EEPROM del DAC (dirección 0x62).
  - Limitar la consigna a la fuente de 24 V (≈ 21–22 V).
  - Orden de encendido: DAC → BUCK_EN → comprobar tensión → LED_EN → PWM.
  - Apagar si LED_V_ADC supera la consigna.
- **Mecánica:** comprobar que entra el cable USB del DevKit y el hueco de la caja para la antena.
