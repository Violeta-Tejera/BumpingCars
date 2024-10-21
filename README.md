# TankesLokos

_No mordemos, sólo nos quemamos con los soldadores_

## Componentes (Idea)

- Arduino UNO c/ESP32
- Portapilas _¿cuántos voltios?_
- Un servomotor de 180º para la torreta
- Una cámara para la torreta
- 4 motores
- 4 ruedas omnidireccionales (imprimir)
- Display 7 segmentos
- 1 led rgb para el color del equipo
- 1 led para encendido
- 1 led para munición _trabajo futuro_
- 1 led para captura la bandera _trabajo futuro_
- 1 driver motores
- linterna del chinese o algo así (a modo de foco para la cámara)

## Ideas extra

- Cuando el tanque dispara...
 - Tanque emite sonido
 - Retroceso sentido opuesto hacia donde mira la torreta

- _¿Altavoz para efectos especiales?_

- Faros en los tanques? (Estética)
 - Quizá pueda afectar a la luz infrarroja (Laser Tag)
 - Quizá sea estético
 - Quizá ayude con el reconocimiento del qr


## Otras consideraciones

Los robots son clientes y un ordenador es el server central.

MicroPython/Python + OpenCV

Hacemos una red local y conectamos un ordenador y todos los robots a ella. Los robots le envían al ordenador los datos y el ordenador corre en la red local un server sencillito con una base de datos.

Decidir entre reconocimiento QR y Laser Tag

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

## Para el Futuro Wall-e ;)

Cámara super chetada para Computer Vision 

(Este link me lo pasó Javi OSHWDem, el que quedó segundo en laberinto)

https://openmv.io/
