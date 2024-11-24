from micropython import const
import bluetooth
import struct
from machine import Pin
import time

# Constantes Bluetooth
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)
_IRQ_PERIPHERAL_CONNECT = const(7)
_IRQ_PERIPHERAL_DISCONNECT = const(8)
_IRQ_GATTC_SERVICE_RESULT = const(9)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_NOTIFY = const(13)

# UUID del servicio del GameSir
_GAMESIR_SERVICE_UUID = bluetooth.UUID(0x8650)

class GameSirController:
    def __init__(self):
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.led = Pin(2, Pin.OUT)
        self.connected = False
        self.target_addr = None
        self.conn_handle = None
        self.report_char_handle = None
        self.button_names = {
            0x0001: "A",
            0x0002: "B",
            0x0004: "X",
            0x0008: "Y",
            0x0010: "L1",
            0x0020: "R1",
            0x0040: "L2",
            0x0080: "R2",
            0x0100: "Select",
            0x0200: "Start",
            0x0400: "L3",
            0x0800: "R3",
            0x1000: "D-Pad Up",
            0x2000: "D-Pad Down",
            0x4000: "D-Pad Left",
            0x8000: "D-Pad Right"
        }
        self.last_report = None

        print("\n╔════════════════════════════════════╗")
        print("║   Buscando GameSir G3s...          ║")
        print("╚════════════════════════════════════╝\n")

        self.ble.irq(self._irq_handler)
        self._start_scan()

    def _start_scan(self):
        self.ble.gap_scan(10000, 30000, 30000, True)

    def _enable_notifications(self, char_handle):
        try:
            config = struct.pack('<H', 0x0001)  # Habilitar notificaciones
            self.ble.gattc_write(self.conn_handle, char_handle + 1, config)
        except Exception as e:
            print(f"Error al habilitar notificaciones: {e}")

    def _irq_handler(self, event, data):
        try:
            if event == _IRQ_SCAN_RESULT:
                addr_type, addr, adv_type, rssi, adv_data = data
                name = self._decode_name(adv_data)
                if name and "GAMESIR" in name.upper():
                    print(f"Dispositivo encontrado: {name}")
                    print(f"Dirección: {':'.join('%02X' % b for b in addr)}")
                    self.target_addr = addr
                    self.ble.gap_scan(None)  # Detener el escaneo
                    self.ble.gap_connect(addr_type, addr)

            elif event == _IRQ_PERIPHERAL_CONNECT:
                self.conn_handle = data[0]
                self.connected = True
                self.led.value(1)
                print("\n¡Conexión establecida!")
                self.ble.gattc_discover_services(self.conn_handle)

            elif event == _IRQ_PERIPHERAL_DISCONNECT:
                self.connected = False
                self.led.value(0)
                print("\nDesconectado. Reiniciando búsqueda...")
                self._start_scan()

            elif event == _IRQ_GATTC_SERVICE_RESULT:
                conn_handle, start_handle, end_handle, uuid = data
                if uuid == _GAMESIR_SERVICE_UUID:
                    print("Servicio GameSir encontrado")
                    self.ble.gattc_discover_characteristics(self.conn_handle, start_handle, end_handle)

            elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
                conn_handle, def_handle, value_handle, properties, uuid = data
                if properties & 0x10:  # Soporte para notificaciones
                    self.report_char_handle = value_handle
                    self._enable_notifications(value_handle)

            elif event == _IRQ_GATTC_NOTIFY:
                conn_handle, value_handle, notify_data = data
                if value_handle == self.report_char_handle:
                    self._process_input_report(notify_data)
        except Exception as e:
            print(f"Error en IRQ: {e}")

    def _decode_name(self, adv_data):
        i = 0
        while i < len(adv_data):
            length = adv_data[i]
            if length == 0:
                break
            type = adv_data[i + 1]
            if type == 0x09:  # Complete Local Name
                return adv_data[i + 2:i + 1 + length].decode('utf-8')
            i += 1 + length
        return None

    def _process_input_report(self, data):
        buttons = (data[1] << 8) | data[0]
        lx, ly, rx, ry = data[3], data[4], data[5], data[6]
        pressed_buttons = [name for mask, name in self.button_names.items() if buttons & mask]
        self._print_status(pressed_buttons, lx, ly, rx, ry)

    def _print_status(self, pressed_buttons, lx, ly, rx, ry):
        print("\033[2J\033[H")  # Limpiar pantalla
        print("╔════════════════════════════════════╗")
        print("║       Estado del Control           ║")
        print("╠════════════════════════════════════╣")
        if pressed_buttons:
            print("║ Botones presionados:              ║")
            for button in pressed_buttons:
                print(f"║  ▶ {button:<27} ║")
        else:
            print("║  Ningún botón presionado          ║")
        print("╠════════════════════════════════════╣")
        print(f"║ Joystick Izq: X:{lx:3d} Y:{ly:3d}        ║")
        print(f"║ Joystick Der: X:{rx:3d} Y:{ry:3d}        ║")
        print("╚════════════════════════════════════╝")

# Iniciar controlador
controller = GameSirController()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Programa terminado")
