# Controlador de Acuario V1.0

**Revisión A del esquema, pendiente de aprobación y ensayos.** Abrir `Control_Acuario_V1_0.kicad_pro` con KiCad 9. El esquema nativo y su biblioteca local están en esta carpeta. El PDF permite revisar el circuito sin instalar KiCad.

## Para revisar

- [Esquema en PDF](Control_Acuario_V1_0_Esquema.pdf)
- [Revisión eléctrica, ERC y costes](Control_Acuario_V1_0_Revision_ERC_DRC.md)
- [Lista preliminar de componentes](Control_Acuario_V1_0_BOM.csv)
- [Plan de pruebas](Control_Acuario_V1_0_Plan_Pruebas.md)

## Alcance

Una salida de dos polos para luz monocolor. La consigna de tensión y el PWM se pueden ajustar de forma independiente. Hay dos mandos DC para SSR externos, un ESP32-DevKitC-32E con Wi-Fi y Bluetooth, reloj DS3231 extraíble y sonda DS18B20. El calentador Eheim, de hasta 350 W, conserva su termostato interno. La bomba, de hasta 10 W, y el calentador son cargas externas de 230 V.

La revisión A contiene el esquema. El trazado, las pruebas de banco, el firmware y los archivos para fabricación están pendientes.
