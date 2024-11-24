import bluetooth
from machine import Pin, Timer
from time import sleep_ms

class GameSirController:
    def __init__(self):
        # Inicializar bluetooth
        self.bt = bluetooth.BLE()
        self.bt.active(True)
        
        # LED indicador de conexión
        self.led = Pin(2, Pin.OUT)
        self.connected = False
        
        # Callback handlers
        self.bt.irq(self.bt_irq)
        
        # Características del GameSir G3s
        self.GAMESIR_NAME = "GameSir-G3s"
        self.buttons_mapping = {
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
            0x1000: "Up",
            0x2000: "Down",
            0x4000: "Left",
            0x8000: "Right"
        }
        
        # Buffer para los datos del control
        self.last_buttons = 0
        
        print("Iniciando búsqueda del GameSir G3s...")
        self._start_scanning()
    
    def _start_scanning(self):
        self.bt.gap_scan(0, 30000, 30000)
    
    def bt_irq(self, event, data):
        if event == 1: # _IRQ_SCAN_RESULT
            addr_type, addr, adv_type, rssi, adv_data = data
            if self.GAMESIR_NAME in str(adv_data):
                print(f"\nGameSir G3s encontrado! RSSI: {rssi}dB")
                self.bt.gap_scan(None) # Detener escaneo
                self.bt.gap_connect(addr_type, addr)
                
        elif event == 3: # _IRQ_SCAN_COMPLETE
            if not self.connected:
                self._start_scanning()
                
        elif event == 7: # _IRQ_PERIPHERAL_CONNECT
            print("\n¡Conectado al GameSir G3s!")
            self.connected = True
            self.led.value(1)
            
        elif event == 8: # _IRQ_PERIPHERAL_DISCONNECT
            print("\nDesconectado. Reiniciando búsqueda...")
            self.connected = False
            self.led.value(0)
            self._start_scanning()
            
        elif event == 9: # _IRQ_GATTC_SERVICE_RESULT
            # Manejar descubrimiento de servicios
            pass
            
        elif event == 11: # _IRQ_GATTC_CHARACTERISTIC_RESULT
            # Configurar notificaciones para los botones
            pass
            
        elif event == 13: # _IRQ_GATTC_NOTIFY
            conn_handle, value_handle, notify_data = data
            self._process_buttons(notify_data)
    
    def _process_buttons(self, data):
        if len(data) >= 2:
            buttons = (data[1] << 8) | data[0]
            if buttons != self.last_buttons:
                self._print_pressed_buttons(buttons)
                self.last_buttons = buttons
    
    def _print_pressed_buttons(self, buttons):
        print("\n╔══════════════════════════╗")
        print("║    Botones Presionados   ║")
        print("╠══════════════════════════╣")
        
        pressed = []
        for mask, name in self.buttons_mapping.items():
            if buttons & mask:
                pressed.append(name)
        
        if pressed:
            for button in pressed:
                print(f"║ ▶ {button:<20} ║")
        else:
            print("║ Ningún botón presionado  ║")
            
        print("╚══════════════════════════╝")

# Crear instancia y mantener el programa corriendo
controller = GameSirController()

# Mantener el script ejecutándose
try:
    while True:
        sleep_ms(100)
except KeyboardInterrupt:
    print("\nPrograma terminado por el usuario")
    controller.bt.active(False)