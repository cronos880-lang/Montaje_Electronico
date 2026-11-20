# Controlador de Acuario V1.0

**Revisión B: esquema y PCB trazada, pendientes de aprobación y ensayos.** Abrir `Control_Acuario_V1_0.kicad_pro` con KiCad 9. El PDF permite revisar el circuito sin instalar KiCad. La revisión A está en el ZIP `Control_Acuario_V1_0_Revision_A.zip` y en el commit `4b8fed1`.

## Para revisar
- [Esquema en PDF (rev. B)](Control_Acuario_V1_0_Esquema.pdf)
- [PCB y guía de fabricación (coste, cómo pedir)](Control_Acuario_V1_0_PCB_y_Fabricacion.md)
- [Revisión final antes del pedido](Control_Acuario_V1_0_Revision_Final_Prepedido.md)
- [Vista 3D cara superior](Control_Acuario_V1_0_PCB_3D_superior.png) · [PDF cara superior](Control_Acuario_V1_0_PCB_cara_superior.pdf) · [PDF cara inferior](Control_Acuario_V1_0_PCB_cara_inferior.pdf)
- [Informe DRC (KiCad 9.0.9)](Control_Acuario_V1_0_DRC.rpt)
- [Archivos de fabricación](fabricacion/)
- [Revisión B: correcciones, cálculos y pendientes](Control_Acuario_V1_0_Revision_B.md)
- [Lista de componentes con referencias LCSC (rev. B)](Control_Acuario_V1_0_BOM.csv)
- [Informe ERC (KiCad 9.0.9)](Control_Acuario_V1_0_ERC.rpt)
- [Revisión A: informe original](Control_Acuario_V1_0_Revision_ERC_DRC.md)
- [Plan de pruebas](Control_Acuario_V1_0_Plan_Pruebas.md)

## Alcance
Una salida de dos polos para luz monocolor, con consigna de tensión (≈5–24 V) y PWM independientes. Dos mandos DC para SSR externos, ESP32-DevKitC-32E con Wi-Fi y Bluetooth, reloj DS3231 extraíble y sonda DS18B20. La PCB solo lleva baja tensión: bomba y calentador de 230 V van en SSR externos, y su integración la valida un profesional cualificado.

PCB trazada con DRC limpio (solo avisos de serigrafía) y archivos de fabricación generados. Pendientes: tu revisión, las pruebas de banco y el firmware. No se ha hecho ningún pedido.
