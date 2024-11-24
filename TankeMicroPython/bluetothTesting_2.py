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

# UUID del servicio HID
_HID_SERVICE_UUID = bluetooth.UUID(0x1812)
_HID_REPORT_CHAR_UUID = bluetooth.UUID(0x2A4D)

class GameSirController:
    def __init__(self):
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.led = Pin(2, Pin.OUT)
        self.connected = False
        self.target_addr = None
        
        # Configuración de callbacks
        self.ble.irq(self._irq_handler)
        
        # Estado de los botones
        self.buttons_state = {}
        
        # Mapeo de botones para GameSir G3s
        self.button_names = {
            0x01: "A",
            0x02: "B", 
            0x04: "X",
            0x08: "Y",
            0x10: "L1",
            0x20: "R1",
            0x40: "L2",
            0x80: "R2",
            0x100: "Select",
            0x200: "Start",
            0x400: "L3",
            0x800: "R3",
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
    
    def _irq_handler(self, event, data):
        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            
            # Convertir la dirección a string para mejor manejo
            addr_str = ':'.join(['%02X' % i for i in addr])
            
            # Buscar el nombre del dispositivo en los datos de advertising
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
            
            # Si encontramos un dispositivo GameSir
            if name and ("GAMESIR" in name.upper() or "GAMEPAD" in name.upper()):
                print(f"\n║ Dispositivo encontrado: {name}")
                print(f"║ Dirección: {addr_str}")
                print(f"║ RSSI: {rssi}dB")
                
                self.target_addr = addr
                self.addr_type = addr_type
                
                # Detener el escaneo e intentar conectar
                self.ble.gap_scan(None)
                self.ble.gap_connect(addr_type, addr)
        
        elif event == _IRQ_SCAN_DONE:
            if not self.connected and not self.target_addr:
                print("\n║ Escaneo completado. Reiniciando búsqueda...")
                self._start_scan()
        
        elif event == _IRQ_PERIPHERAL_CONNECT:
            # Se estableció la conexión
            conn_handle, addr_type, addr = data
            self.connected = True
            self.led.value(1)
            print("\n╔════════════════════════════════════╗")
            print("║     ¡Conexión establecida! 🎮      ║")
            print("╚════════════════════════════════════╝")
        
        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            # Desconexión
            self.connected = False
            self.led.value(0)
            print("\n║ Desconectado. Reiniciando búsqueda...")
            self.target_addr = None
            self._start_scan()
        
        elif event == _IRQ_GATTC_NOTIFY:
            # Procesar datos de botones
            self._handle_button_data(data[2])
    
    def _handle_button_data(self, data):
        if len(data) >= 2:
            buttons = (data[1] << 8) | data[0]
            
            # Detectar cambios en los botones
            changed = False
            for mask, name in self.button_names.items():
                current_state = bool(buttons & mask)
                if self.buttons_state.get(name) != current_state:
                    changed = True
                    self.buttons_state[name] = current_state
            
            # Si hubo cambios, mostrar estado actual
            if changed:
                self._print_active_buttons()
    
    def _print_active_buttons(self):
        active_buttons = [name for name, state in self.buttons_state.items() if state]
        
        print("\n╔════════════════════════════════════╗")
        print("║       Botones Presionados          ║")
        print("╠════════════════════════════════════╣")
        
        if active_buttons:
            for button in active_buttons:
                print(f"║  ▶ {button:<27} ║")
        else:
            print("║  Ningún botón presionado         ║")
            
        print("╚════════════════════════════════════╝")

# Iniciar el controlador
print("Iniciando sistema...")
controller = GameSirController()

# Mantener el programa en ejecución
try:
    while True:
        time.sleep_ms(100)
        if not controller.connected:
            controller.led.value(not controller.led.value())  # Parpadeo mientras busca
except KeyboardInterrupt:
    print("\nPrograma terminado por el usuario")
    controller.ble.active(False)