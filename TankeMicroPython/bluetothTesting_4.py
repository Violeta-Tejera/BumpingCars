from micropython import const
import bluetooth
import struct
from machine import Pin
import time

# Constantes Bluetooth
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
_IRQ_GATTC_WRITE_STATUS = const(17)
_IRQ_GATTC_NOTIFY = const(13)

# UUIDs para servicios HID
_HID_SERVICE_UUID = bluetooth.UUID(0x1812)  # Human Interface Device
_BATTERY_SERVICE_UUID = bluetooth.UUID(0x180F)  # Battery Service
_DEVICE_INFO_UUID = bluetooth.UUID(0x180A)  # Device Information

class GameSirController:
    def __init__(self):
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.led = Pin(2, Pin.OUT)
        self.connected = False
        self.target_addr = None
        self.conn_handle = None
        self.services_discovered = False
        
        # Variables para el manejo de servicios y características
        self.hid_service_handle = None
        self.report_char_handle = None
        self.current_service_handle = None  # Agregado para tracking
        
        self.ble.irq(self._irq_handler)
        
        # Estado de los botones y joysticks
        self.buttons_state = {}
        self.last_report = None
        
        # Mapeo de botones para GameSir G3s
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
        
        print("\n╔════════════════════════════════════╗")
        print("║   Iniciando búsqueda de GameSir    ║")
        print("╚════════════════════════════════════╝\n")
        
        self._start_scan()
    
    def _start_scan(self):
        self.ble.gap_scan(20000, 30000, 30000, True)
    
    def _discover_services(self):
        try:
            print("Descubriendo servicios...")
            self.ble.gattc_discover_services(self.conn_handle)
        except Exception as e:
            print(f"Error en discover_services: {e}")
    
    def _discover_characteristics(self, start_handle, end_handle=0xFFFF):
        try:
            print("Descubriendo características...")
            self.ble.gattc_discover_characteristics(self.conn_handle, start_handle, end_handle)
        except Exception as e:
            print(f"Error en discover_characteristics: {e}")
    
    def _enable_notifications(self, char_handle):
        try:
            print("Habilitando notificaciones...")
            value = struct.pack('<H', 0x0001)  # Habilitar notificaciones
            self.ble.gattc_write(self.conn_handle, char_handle + 1, value)
        except Exception as e:
            print(f"Error en enable_notifications: {e}")
    
    def _irq_handler(self, event, data):
        try:
            if event == _IRQ_SCAN_RESULT:
                addr_type, addr, adv_type, rssi, adv_data = data
                
                addr_str = ':'.join(['%02X' % i for i in addr])
                name = None
                ad_data = bytes(adv_data)
                i = 0
                while i < len(ad_data):
                    length = ad_data[i]
                    if length == 0:
                        break
                    type = ad_data[i + 1]
                    if type == 0x09:  # Complete Local Name
                        name = ad_data[i + 2:i + length + 1].decode('utf-8')
                    i += length + 1
                
                if name and ("GAMESIR" in name.upper() or "GAMEPAD" in name.upper()):
                    print(f"\n║ Dispositivo encontrado: {name}")
                    print(f"║ Dirección: {addr_str}")
                    print(f"║ RSSI: {rssi}dB")
                    
                    self.target_addr = addr
                    self.addr_type = addr_type
                    
                    self.ble.gap_scan(None)
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
                time.sleep_ms(100)  # Pequeña pausa antes de descubrir servicios
                self._discover_services()
            
            elif event == _IRQ_PERIPHERAL_DISCONNECT:
                self.connected = False
                self.led.value(0)
                self.services_discovered = False
                print("\n║ Desconectado. Reiniciando búsqueda...")
                self.target_addr = None
                self._start_scan()
            
            elif event == _IRQ_GATTC_SERVICE_RESULT:
                conn_handle, start_handle, end_handle, uuid = data
                if uuid == _HID_SERVICE_UUID:
                    self.hid_service_handle = start_handle
                    self.current_service_handle = start_handle
                    print("Servicio HID encontrado")
                    self._discover_characteristics(start_handle, end_handle)
            
            elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
                conn_handle, def_handle, value_handle, properties, uuid = data
                if properties & 0x10:  # Propiedad de notificación
                    print("Característica de notificación encontrada")
                    self.report_char_handle = value_handle
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
                
                # Los primeros dos bytes son para botones
                buttons = (data[1] << 8) | data[0] if len(data) >= 2 else 0
                
                # Analizar joysticks (típicamente bytes 3-6)
                lx = data[3] if len(data) > 3 else 128
                ly = data[4] if len(data) > 4 else 128
                rx = data[5] if len(data) > 5 else 128
                ry = data[6] if len(data) > 6 else 128
                
                # Obtener botones presionados
                pressed_buttons = []
                for mask, name in self.button_names.items():
                    if buttons & mask:
                        pressed_buttons.append(name)
                
                # Mostrar estado
                self._print_controller_status(pressed_buttons, lx, ly, rx, ry)
                
        except Exception as e:
            print(f"Error procesando datos: {e}")
    
    def _print_controller_status(self, pressed_buttons, lx, ly, rx, ry):
        print("\033[2J\033[H")  # Limpiar pantalla y mover cursor al inicio
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