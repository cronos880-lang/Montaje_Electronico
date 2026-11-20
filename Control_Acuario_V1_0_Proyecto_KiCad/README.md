# Controlador de Acuario V1.0

**Revisión B del esquema, pendiente de aprobación y ensayos.** Abrir `Control_Acuario_V1_0.kicad_pro` con KiCad 9. El PDF permite revisar el circuito sin instalar KiCad. La revisión A está en el ZIP `Control_Acuario_V1_0_Revision_A.zip` y en el commit `4b8fed1`.

## Para revisar
- [Esquema en PDF (rev. B)](Control_Acuario_V1_0_Esquema.pdf)
- [Revisión B: correcciones, cálculos y pendientes](Control_Acuario_V1_0_Revision_B.md)
- [Lista de componentes con referencias LCSC (rev. B)](Control_Acuario_V1_0_BOM.csv)
- [Informe ERC (KiCad 9.0.9)](Control_Acuario_V1_0_ERC.rpt)
- [Revisión A: informe original](Control_Acuario_V1_0_Revision_ERC_DRC.md)
- [Plan de pruebas](Control_Acuario_V1_0_Plan_Pruebas.md)

## Alcance
Una salida de dos polos para luz monocolor, con consigna de tensión (≈5–24 V) y PWM independientes. Dos mandos DC para SSR externos, ESP32-DevKitC-32E con Wi-Fi y Bluetooth, reloj DS3231 extraíble y sonda DS18B20. La PCB solo lleva baja tensión: bomba y calentador de 230 V van en SSR externos, y su integración la valida un profesional cualificado.

El trazado, el DRC, las pruebas de banco, el firmware y los archivos de fabricación están pendientes.
