# TankesLokos

_No mordemos, sólo nos quemamos con los soldadores_ 

## Componentes (Idea)

- Arduino UNO c/ESP32 - **WeMos D1 ESP32 WROOM WiFi** - _Mirar otros modelos -> buscar alternativas_ (igual es más barata/mejor)
- Un servomotor de 180º para la torreta
- 2 motores -> **Gebildet 8pcs DC3V-12V Motorreductor DC**
                -> Pending seguir mirando:
                       https://www.amazon.es/Gebildet-Motorreductor-Tracci%C3%B3n-Rob%C3%B3tico-Juguetes/dp/B07Z4PYJY4

- FABADA: Leds pueden ser RGB

- 1 led para encendido
- 1 led para munición 
       - En la torreta para indicar al usuario que la bala está cargada

- 1 Emisor láser
- [N=4] -> N:
    - receptores (dianas del láser)
    - leds rojos (se apaga cuando han derribado ese punto débil) 
  
- 1 driver motores L298N.
- Portapilas _Darle una pensada a los voltios_
- buzzer -> ¡Uo! del mainkra/melodía 8 bits
- interruptor (on/off) [la idea es que **NO** se encienda por el simple hecho de meter las pilas]
- Mando bluetooth
 

## Componentes (Idea)

- linterna del chinese o algo así (a modo de foco para la cámara)
- 1 led para captura la bandera _trabajo futuro_

## Ideas extra

- Cuando el tanque dispara...
 - Tanque emite sonido
 - Retroceso sentido opuesto hacia donde mira la torreta

- _¿Altavoz para efectos especiales?_

- Faros en los tanques? (Estética)
 - Quizá pueda afectar a la luz infrarroja (Laser Tag)
 - Quizá sea estético


## Otras consideraciones

Los robots son clientes y un ordenador es el server central.

MicroPython/Python

Hacemos una red local y conectamos un ordenador y todos los robots a ella. Los robots le envían al ordenador los datos y el ordenador corre en la red local un server sencillito con una base de datos.

Laser Tag

Mirar cómo funciona laser tag. Para distinguir las emisiones de cada tanque.

Red:
 - ESP-now
 - Wifi y a correr. Más replicable


## Asalto al Hall

Pedir el espacio entre las 4 columnas y montar allí todo el tinglado. Poner obstáculos para que los robots se escondan por detrás. Imprimir en un dina0 la vista aérea a escala con respecto a lo que comentaré ahora, del campus de cantoblanco. Imprimir unas fotos de la EPS desde 4 lados diferentes y pegárselo a los lados de una caja de fotocopias, ese puede ser uno de los obstáculos. 

Maybe más fácil de transportar en 16 DIN A4.

¿HAcemos algún lore loco metiendo referencias a la carrera para justificar el nombre de "Asalto al Hall"?

- SOPER vs REDES II

- Teleco vs Informática (no conviene enemistarnos xd pero como es un brainstorming lo pongo jajaj)

- HUMANOS contra CYBERDUCKS/TERMIN4T0RS 😜

- Patos vs gatos

Bus autónomo dando vueltas a la EPS:
 - Siguiendo una línea alrededor de la EPS

----------------------------

Sonido:
 - disparar

 En la torreta para que se vea cuando puedes disparar.
  - x1-> Led indicador si tienes bala cargada:
(En la punta del cañón)
       - Led amarillo en la torreta (encima): Bala cargada
  
 - recibir daño
     - x4 -> rojo:
         - encendido de normal
         - apagado cuando han derribado ese punto débil
  
Retroceso:
 - al disparar

Leds La salud, 

----------------------------

## Para el Futuro Wall-e ;)

Cámara super chetada para Computer Vision 

(Este link me lo pasó Javi OSHWDem, el que quedó segundo en laberinto)

https://openmv.io/

## Parte del SetUp

### <a name="mp_placa">MicroPython en la placa

Link de culto de [MicroPython](https://dancruzmx.medium.com/micropython-en-una-wemos-esp32-d1-r32-e6078150a1a8) para nuestra placa

*IMPORTANTE: en el apartado de Instalación del FirmWare 

con esptool instalado (pip install esptool)

pone 2 comandos a continuación pero a mí me han funcionado los de la documentación oficial referenciada de MicroPython (son parecidos)

Bajarse este [bin](https://micropython.org/resources/firmware/ESP32_GENERIC-20241025-v1.24.0.bin) para el ESP32 (v1.24.0)

Proviene de este [enlace](https://micropython.org/download/ESP32_GENERIC/) por si queda desactualizado. Y en ese caso modificar el nombre del .bin en el segundo comando (aplica a cualquier OS) ;)

(si se trabaja en Windows seguir los comandos del arículo ;)

En la misma ruta donde está instalado el .bin Y CON LA PLACA CONECTADA AL PC!!!:

- _esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash_
- _esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 ESP32_GENERIC-20241025-v1.24.0.bin_

_Ignoren la parte de PRUEBAS del artículo ;)_

### MicroPython IDE

Lo suyo sería trabajar con el IDE de Arduino pero no he conseguido crear el entorno de MicroPython deseado. No he encontrado forma de instalar plugins de MicroPyton ni nada por el estilo. Si la hay, es que me he rendido antes 😅.

Sin embargo he encontrado otro (también de Arduino) enfocado en MicroPython llamado [Arduino Lab For MicorPython](https://labs.arduino.cc/en/labs/micropython). Este Link lleva a una página de descargas para descargar el IDE en fucnión del SO con el que se esté trabajando. Linux en mi caso 😈

La ventaja es que no hay que realizar pasos adicionales de configuración en el propio IDE a diferencia del IDE de Arduino convenvional. En otras palabras, si hemos seguido los pasos del [apartado anterior](#mp_placa) y hemos conectado la placa al ordenador ya tenemos MicroPython Ready To Go 😎 !!! Tiene una interfaz bastante simple e intuitiva.

Permítanme añadir que me sorprende lo _straightforward_ que es 😜 !!!

*Observaciones:
  - Si por lo que sea os da por mover ficheros de sitio o cambiar el nombre de la ruta donde se encuentra el proyecto, el IDE es tan simple que sencillamente explota 💥 y no deja abrir el proyecto. No tiene digamos un apartado de File -> Open...
      Solución:
        Si estáis en Linux 🐧, este comando me ha salvado la vida:
            _rm -rf ~/.config/Arduino Lab for MicroPython/Local Storage_

  Esto hará que la próxima vez que se abra te pregunte por la ubicación del directorio que quieras abrir.

## No tan importante

No he encontrado el GameSir **G**3s pero he encontrado este que es de la misma marca y a un precio asequible:
[GameSir **T**3s](https://es.aliexpress.com/item/1005007038130995.html?spm=a2g0o.productlist.main.1.1d27FrMRFrMRgV&algo_pvid=b3bc0426-7b90-4c2f-83f4-332a1c6af81f&algo_exp_id=b3bc0426-7b90-4c2f-83f4-332a1c6af81f-0&pdp_npi=4%40dis%21EUR%2144.40%2115.85%21%21%21329.41%21117.58%21%40211b612817323869328777304ecb59%2112000039179975857%21sea%21ES%210%21ABX&curPageLogUid=IlovW96HRhiG&utparam-url=scene%3Asearch%7Cquery_from%3A)

⚠️ No garantizo que también funcione este con la placa (Asumiendo que funciona con el Gamesir G3s) ⚠️
*La placa "**WeMos D1 ESP32 WROOM WiFi**"

Problema que veo de primeras es que sé que el ESP32 y el G3s soportan bluetooth por debajo de 5.0 pero este ni idea. Parece que hay retrocompatibilidad tras una búsqueda rápida en Google. Pending investigar + sobre el tema.

### Datasheets

### Mandos

#### [G3s](https://www.mijoya.com.mx/images/GameSir%20G3s%20USER%20Mannual%20FINAL%2020161101.pdf)
#### [T3s](https://cdn.shopify.com/s/files/1/2241/8433/files/GameSir-T3s.pdf?v=1654507846) (Las instrucciones, que no he encontrado la datasheet 😅)

### Placas

#### [ESP 32](https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf)
#### [Repo arduino-esp32](https://github.com/espressif/arduino-esp32): tiene bastantes referencias

## Importante

Diseño que tiene las ruedas por eslabones: https://www.thingiverse.com/thing:467807

At the moment las pruebas se están haciendo con la placa: **WeMos D1 ESP32 WROOM WiFi**
