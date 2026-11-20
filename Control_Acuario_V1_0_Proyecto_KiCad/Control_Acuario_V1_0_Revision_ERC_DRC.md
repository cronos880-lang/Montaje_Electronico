# Controlador de Acuario V1.0 · Revisión eléctrica A

## Operación prevista

| Estado | Regulador U2 | Protección U3 | MOSFET Q1 |
|---|---|---|---|
| Apagado | Deshabilitado | Deshabilitada | Abierto |
| Continua | Consigna DAC ajustada a la luminaria | Habilitada | Cerrado |
| PWM | Consigna DAC fija o ajustada a la luminaria | Habilitada | Conmutado por GPIO33 |

Las salidas arrancan deshabilitadas mediante resistencias de polarización. El futuro firmware debe escribir la consigna del DAC antes de habilitar U2, comprobar la tensión y habilitar U3 y PWM en ese orden. La selección del voltaje admisible de la luminaria y la advertencia sobre conexión quedan en las instrucciones. El retorno LED_NEG es conmutado. La carga va entre LED_POS y LED_NEG.

## Decisiones de esta revisión

- Entrada aislada externa de 36 V nominal, con margen para obtener 24 V de un buck incluso bajo carga. Se propone conservar la fuente de 36 V como arquitectura de entrada. Una fuente de 36 V y 3 A nominales deja margen para 75 W si su capacidad y temperatura están verificadas. Por ejemplo, a 85 % de eficiencia de la ruta LED y con 6 W de consumo auxiliar, la estimación es 94,2 W o 2,62 A a 36 V. El cálculo es una hipótesis de dimensionamiento.
- El buck de iluminación se integra en la placa. Se propone esta solución para evitar un módulo específico con interfaz de control. La etapa auxiliar de 5 V sigue siendo un módulo Traco de 1 A. Si la cotización acusa su coste, comparar con una auxiliar integrada de 65 V y 1 A, como LMR36510, con su propio cálculo térmico.
- La salida activa cubre aproximadamente 5–24 V. Se obtiene el estado de 0 V por apagado y descarga. El mínimo está condicionado por el rango del DAC y el límite inferior de funcionamiento de U3. La tensión real en la borna tiene tolerancia y caída resistiva. Con resistencias nominales, VBUCK = 23,88 V − 5,91 × VDAC. La escala es aproximadamente 4,8 mV por paso de DAC a 3,3 V. Se ajustarán curva, tiempo de asentamiento y tensión mínima al ensayar.
- U3 ofrece límites por hardware independientes del firmware. 18 / 3,83 ≈ 4,70 A nominales y 69,8 kΩ fija unos 69,8 W nominales. El ajuste de potencia deja margen hacia el máximo de 75 W. La dispersión real, los picos y el efecto del PWM requieren validación. 4,7 A es el dimensionamiento nominal y la protección puede limitar antes por tolerancia. Tampoco se garantiza entregar 75 W continuos. En sobrecarga sostenida U3 queda enclavado hasta rearmarlo. El límite protege frente a sobrecarga, mientras que la elección de la tensión compatible corresponde a la instalación.
- A 36 V de entrada, 400 kHz y L1 = 15 µH, el rizado de corriente ideal máximo se da cerca de 18 V y vale 1,5 A pico a pico. Con −20 % de inductancia inicial resulta 1,875 A, antes del efecto de la corriente y la temperatura. A 4,7 A continuos el pico puede rondar 5,64 A. Verificar saturación con corriente y temperatura, el límite de pico del LM76005 y su comportamiento con carga pulsante. U3 disipa aproximadamente 0,68 W a 4,7 A a partir de 31 mΩ típicos. La temperatura de U2, U3, Q1, inductor y borna se comprobará en la caja. Se cerrarán condensadores cerámicos por capacidad efectiva a tensión, no solo por el valor nominal.
- El RTC funciona a 3,3 V y requiere un módulo sin carga de CR2032. Revisar orden de pines y pull-ups del módulo real. JP1 se abre para alimentar el DevKit por USB y se debe desconectar la fuente de 36 V durante esa operación.
- J5 y J6 son salidas de mando para SSR, con 5 V y retorno conmutado. Cada SSR comercial debe aceptar la tensión disponible al final del cable. Para la bomba pequeña son decisivas su corriente mínima de carga, fuga en OFF y corriente de arranque. El SSR del calentador requiere revisar corriente y disipación. Se mantiene el termostato Eheim y queda por comprobar su actuación y ajuste con el mando externo mantenido en ON. La integración de 230 V queda fuera de la PCB y se valida por separado.

## Verificaciones

KiCad CLI 9.0.2 abrió el esquema, generó un PDF y exportó la lista de redes. ERC ejecutado con **0 errores y 0 avisos**. Se revisaron 17 redes etiquetadas y cuatro uniones de control en la netlist, incluyendo la cadena de potencia, el retorno conmutado, los mandos SSR y los pines de la sonda. El ERC comprueba conexiones y reglas de esquema. Quedan pendientes la respuesta dinámica, las tolerancias, la compatibilidad de carga y los ensayos funcionales.

Pendientes del trazado: huellas definitivas del ESP32, L1 y F1, verificación mecánica del TSR y conectores, antena libre, capacidad del cobre, vías térmicas y puntos de prueba. Evaluar dos capas y una sola cara SMD con el diseño térmico. La aceptación de un formato de hasta 100 × 100 mm depende del trazado. DRC queda pendiente de la PCB. No hay Gerber, CPL ni paquete de fabricación en esta revisión.

## Fabricación de menor coste

| Fabricante | Precio público de partida | Condición |
|---|---|---|
| JLCPCB | 2 USD por 5 PCB desnudas | Oferta estándar para configuraciones seleccionadas, con formato de referencia hasta 100 × 100 mm. |
| PCBWay | 5 USD por 10 PCB desnudas | Promoción de prototipo estándar. Tiene menor precio anunciado por placa, con un desembolso base mayor. |
| JLCPCB montaje económico | 8,18 USD de preparación y 1,53 USD de plantilla | Añadir montaje, componentes, alimentadores, placa, transporte e impuestos. |
| PCBWay montaje | Desde 29 USD | Revisar montaje y componentes en la cotización. |

Para una primera prueba, la opción a cotizar primero es JLCPCB con 5 placas y el mínimo de unidades que permita montar en una sola cara SMD. Los componentes de inserción, como bornas, zócalos y el módulo de 5 V, se pueden soldar a mano. U2 y U3 llevan pad térmico inferior y se contemplan para reflujo. La comparativa final debe usar las mismas dimensiones, cobre, unidades montadas y portes a destino. Los importes anteriores son tarifas de partida, no presupuestos de este diseño. Sin archivos de fabricación y disponibilidad de los componentes, el coste de la placa montada queda abierto.

Fuentes de fabricación: [JLCPCB PCB](https://jlcpcb.com/es/ads/pcb-prototype), [JLCPCB tarifas de montaje](https://jlcpcb.com/help/article/pcb-assembly-price), [PCBWay PCB](https://www.pcbway.com/En) y [PCBWay montaje](https://www.pcbway.com/pcb-assembly.html).

Fuentes del circuito: [LM76005](https://www.ti.com/lit/ds/symlink/lm76005.pdf), [TPS2663x](https://www.ti.com/lit/ds/symlink/tps2663.pdf), [TSR 1WI](https://www.tracopower.com/tsr1wi-datasheet), [SRP1265A](https://www.bourns.com/docs/Product-Datasheets/SRP1265A.pdf), [ESP32 DevKitC V4](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html), [MCP4725](https://www.microchip.com/en-us/product/MCP4725), [TC4427](https://www.microchip.com/en-us/product/TC4427) y [STP55NF06L](https://www.st.com/en/power-transistors/stp55nf06l.html).
