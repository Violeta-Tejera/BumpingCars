from micropython import const
import bluetooth
import struct
from machine import Pin
import time

# Bluetooth Constants
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)
_IRQ_PERIPHERAL_CONNECT = const(7)
_IRQ_PERIPHERAL_DISCONNECT = const(8)
_IRQ_GATTC_SERVICE_RESULT = const(9)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_READ_RESULT = const(15)
_IRQ_GATTC_NOTIFY = const(13)

# GameSir Service UUID (modified for both Android/iOS mode)
_GAMESIR_SERVICE_UUID = bluetooth.UUID('00001812-0000-1000-8000-00805f9b34fb')  # HID Service
_GAMESIR_REPORT_CHAR_UUID = bluetooth.UUID('00002A4D-0000-1000-8000-00805f9b34fb')  # HID Report

class GameSirController:
    def __init__(self):
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.led = Pin(2, Pin.OUT)
        self.connected = False
        self.target_addr = None
        self.conn_handle = None
        self.services_discovered = False
        self.characteristics_found = False
        self.report_char_handle = None
        self.last_report = None
        
        # Button mapping for GameSir G3s
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
        
        self.ble.irq(self._irq_handler)
        
        print("\n╔════════════════════════════════════╗")
        print("║   Iniciando búsqueda de GameSir    ║")
        print("╚════════════════════════════════════╝\n")
        
        self._start_scan()
    
    def _start_scan(self):
        self.ble.gap_scan(20000, 30000, 30000, True)
    
    def _discover_services(self):
        try:
            print("Iniciando descubrimiento de servicios...")
            self.ble.gattc_discover_services(self.conn_handle)
            time.sleep_ms(500)  # Esperar un poco para que se completen los resultados
        except Exception as e:
            print(f"Error en discover_services: {e}")
    
    def _discover_characteristics(self, start_handle, end_handle):
        try:
            print(f"Descubriendo características... ({start_handle} - {end_handle})")
            self.ble.gattc_discover_characteristics(self.conn_handle, start_handle, end_handle)
            time.sleep_ms(500)  # Esperar un poco para que se completen los resultados
        except Exception as e:
            print(f"Error en discover_characteristics: {e}")
    
    def _enable_notifications(self, char_handle):
        try:
            print(f"Habilitando notificaciones...")
            # Enable notifications (0x0001) for the characteristic
            self.ble.gattc_write(self.conn_handle, char_handle + 1, struct.pack('<H', 0x0001))
        except Exception as e:
            print(f"Error al habilitar notificaciones: {e}")
    
    def _irq_handler(self, event, data):
        try:
            if event == _IRQ_SCAN_RESULT:
                addr_type, addr, adv_type, rssi, adv_data = data
                
                name = None
                i = 0
                while i < len(adv_data):
                    if adv_data[i] == 0:
                        break
                    length = adv_data[i]
                    type = adv_data[i + 1]
                    if type == 0x09:  # Complete Local Name
                        name = str(adv_data[i + 2:i + length + 1], 'utf-8')
                    i += length + 1
                
                if name and ("GAMESIR" in name.upper() or "GAMEPAD" in name.upper()):
                    print(f"\n║ Dispositivo encontrado: {name}")
                    print(f"║ Dirección: {''.join(['%02X' % i for i in addr])}")
                    print(f"║ RSSI: {rssi}dB")
                    
                    self.target_addr = addr
                    self.addr_type = addr_type
                    self.ble.gap_scan(None)
                    time.sleep_ms(100)
                    self.ble.gap_connect(addr_type, addr)
            
            elif event == _IRQ_SCAN_DONE:
                if not self.connected and not self.target_addr:
                    print("\n║ Escaneo completado. Reiniciando búsqueda...")
                    self._start_scan()
            
            elif event == _IRQ_PERIPHERAL_CONNECT:
                conn_handle, addr_type, addr = data
                self.conn_handle = conn_handle
                self.connected = True
                self.led.value(1)
                print("\n╔════════════════════════════════════╗")
                print("║     ¡Conexión establecida! 🎮      ║")
                print("╚════════════════════════════════════╝")
                time.sleep_ms(300)
                self._discover_services()
            
            elif event == _IRQ_PERIPHERAL_DISCONNECT:
                self.connected = False
                self.led.value(0)
                self.services_discovered = False
                self.characteristics_found = False
                print("\n║ Desconectado. Reiniciando búsqueda...")
                self.target_addr = None
                self._start_scan()
            
            elif event == _IRQ_GATTC_SERVICE_RESULT:
                conn_handle, start_handle, end_handle, uuid = data
                print(f"Servicio encontrado: {uuid}")
                
                if uuid == _GAMESIR_SERVICE_UUID:
                    print("¡Servicio HID encontrado!")
                    self._discover_characteristics(start_handle, end_handle)
            
            elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
                conn_handle, def_handle, value_handle, properties, uuid = data
                print(f"Característica encontrada: {uuid}")
                
                if uuid == _GAMESIR_REPORT_CHAR_UUID:
                    print("¡Característica de informe encontrada!")
                    self.report_char_handle = value_handle
                    self.characteristics_found = True
                    self._enable_notifications(value_handle)
            
            elif event == _IRQ_GATTC_NOTIFY:
                conn_handle, value_handle, notify_data = data
                if value_handle == self.report_char_handle:
                    self._process_input_report(notify_data)
                    
        except Exception as e:
            print(f"Error en irq_handler: {e}")
    
    def _process_input_report(self, data):
        try:
            if data != self.last_report:
                self.last_report = data
                
                # Imprimir datos brutos
                print(f"Datos brutos recibidos: {[hex(x) for x in data]}")
                
                # Procesar datos basados en el modo (Android/iOS o normal)
                if len(data) >= 7:  # Modo estándar
                    buttons = (data[1] << 8) | data[0]
                    lx = data[3]
                    ly = data[4]
                    rx = data[5]
                    ry = data[6]
                    
                    # Obtener botones presionados
                    pressed_buttons = []
                    for mask, name in self.button_names.items():
                        if buttons & mask:
                            pressed_buttons.append(name)
                    
                    # Mostrar estado
                    self._print_controller_status(pressed_buttons, lx, ly, rx, ry)
                
                else:
                    print("Formato de datos desconocido")
                    
        except Exception as e:
            print(f"Error procesando datos: {e}")
    
    def _print_controller_status(self, pressed_buttons, lx, ly, rx, ry):
        print("\033[2J\033[H")  # Limpiar pantalla
        print("╔════════════════════════════════════╗")
        print("║       Estado del Control           ║")
        print("╠════════════════════════════════════╣")
        
        if pressed_buttons:
            print("║ Botones presionados:             ║")
            for button in pressed_buttons:
                print(f"║  ▶ {button:<27} ║")
        else:
            print("║  Ningún botón presionado         ║")
        
        print("╠════════════════════════════════════╣")
        print(f"║ Joystick Izq: X:{lx:3d} Y:{ly:3d}        ║")
        print(f"║ Joystick Der: X:{rx:3d} Y:{ry:3d}        ║")
        print("╚════════════════════════════════════╝")

# Iniciar el controlador
print("Iniciando sistema...")
controller = GameSirController()

# Mantener el programa en ejecución
try:
    while True:
        time.sleep_ms(100)
        if not controller.connected:
            controller.led.value(not controller.led.value())
except KeyboardInterrupt:
    print("\nPrograma terminado por el usuario")
    controller.ble.active(False)
