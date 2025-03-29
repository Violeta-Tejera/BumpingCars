#include <Bluepad32.h>

// PIN CONNECTIONS
// TODO: Usar "#define"
int ENApin = 4;  // Motor 1 PWM
int IN1pin = 13; // Motor 1 dirección
int IN2pin = 26; // Motor 1 dirección
int IN3pin = 14; // Motor 2 dirección
int IN4pin = 27; // Motor 2 dirección
int ENBpin = 5;  // Motor 2 PWMW
int servoPin = 25; // Pin servo
const int ledPins[] = {16, 23, 17};
const int numLeds = sizeof(ledPins) / sizeof(ledPins[0]); 
const int bumperPins[] = {25, 12}; // LEFT and RIGHT
int remainingLives = 3;
bool bumperState = false;

ControllerPtr myControllers[BP32_MAX_GAMEPADS];

// This callback gets called any time a new gamepad is connected.
// Up to 4 gamepads can be connected at the same time.

void onConnectedController(ControllerPtr ctl) {
  bool foundEmptySlot = false;
  for (int i = 0; i < BP32_MAX_GAMEPADS; i++) {
    if (myControllers[i] == nullptr) {
      Serial.printf("CALLBACK: Controller is connected, index=%d\n", i);
      // Additionally, you can get certain gamepad properties like:
      // Model, VID, PID, BTAddr, flags, etc.
      ControllerProperties properties = ctl->getProperties();
      Serial.printf("Controller model: %s, VID=0x%04x, PID=0x%04x\n", ctl->getModelName().c_str(), properties.vendor_id, properties.product_id);
      myControllers[i] = ctl;
      foundEmptySlot = true;
      break;
      }
  }
  if (!foundEmptySlot) {
    Serial.println("CALLBACK: Controller connected, but could not found empty slot");
  }
}

void onDisconnectedController(ControllerPtr ctl) {
  bool foundController = false;

  for (int i = 0; i < BP32_MAX_GAMEPADS; i++) {
    if (myControllers[i] == ctl) {
      Serial.printf("CALLBACK: Controller disconnected from index=%d\n", i);
      myControllers[i] = nullptr;
      foundController = true;
      break;
    }
  }

  if (!foundController) {
    Serial.println("CALLBACK: Controller disconnected, but not found in myControllers");
  }
}

// == SEE CONTROLLER VALUES IN SERIAL MONITOR == //

void dumpGamepad(ControllerPtr ctl) {
  Serial.printf(
    "idx=%d, dpad: 0x%02x, buttons: 0x%04x, axis L: %4d, %4d, axis R: %4d, %4d, brake: %4d, throttle: %4d, "
    "misc: 0x%02x, gyro x:%6d y:%6d z:%6d, accel x:%6d y:%6d z:%6d\n",
    ctl->index(),        // Controller Index
    ctl->dpad(),         // D-pad
    ctl->buttons(),      // bitmask of pressed buttons
    ctl->axisX(),        // (-511 - 512) left X Axis
    ctl->axisY(),        // (-511 - 512) left Y axis
    ctl->axisRX(),       // (-511 - 512) right X axis
    ctl->axisRY(),       // (-511 - 512) right Y axis
    ctl->brake(),        // (0 - 1023): brake button
    ctl->throttle(),     // (0 - 1023): throttle (AKA gas) button
    ctl->miscButtons(),  // bitmask of pressed "misc" buttons
    ctl->gyroX(),        // Gyro X
    ctl->gyroY(),        // Gyro Y
    ctl->gyroZ(),        // Gyro Z
    ctl->accelX(),       // Accelerometer X
    ctl->accelY(),       // Accelerometer Y
    ctl->accelZ()        // Accelerometer Z
  );
}

// == GAME CONTROLLER ACTIONS SECTION == //

void processGamepad(ControllerPtr ctl) {
  // There are different ways to query whether a button is pressed.
  // By query each button individually:
  // a(), b(), x(), y(), l1(), etc...
 
  if(remainingLives > 0){
    //== LEFT JOYSTICK - UP ==//
    if (ctl->axisY() <= -25) {
      // map joystick values to motor speed
      int motorSpeed = map(ctl->axisY(), -25, -508, 70, 255);
      // move motors/robot forward
      digitalWrite(IN1pin, HIGH);
      digitalWrite(IN2pin, LOW);
      analogWrite(ENApin, motorSpeed);
      digitalWrite(IN3pin, LOW);
      digitalWrite(IN4pin, HIGH);
      analogWrite(ENBpin, motorSpeed);
    }

    //== LEFT JOYSTICK - DOWN ==//
    if (ctl->axisY() >= 25) {
      // map joystick values to motor speed
      int motorSpeed = map(ctl->axisY(), 25, 512, 70, 255);
      // move motors/robot in reverse
      digitalWrite(IN1pin, LOW);
      digitalWrite(IN2pin, HIGH);
      analogWrite(ENApin, motorSpeed);
      digitalWrite(IN3pin, HIGH);
      digitalWrite(IN4pin, LOW);
      analogWrite(ENBpin, motorSpeed);
    }

    //== RIGHT JOYSTICK - LEFT ==//
    if (ctl->axisRX() <= -25) {
      // map joystick values to motor speed
      int motorSpeed = map(ctl->axisRX(), -25, -508, 70, 255);
      // turn robot left - move right motor forward, keep left motor still
      digitalWrite(IN1pin, HIGH);
      digitalWrite(IN2pin, LOW);
      analogWrite(ENApin, motorSpeed);
      digitalWrite(IN3pin, HIGH);
      digitalWrite(IN4pin, LOW);
      analogWrite(ENBpin, motorSpeed);
    }

    //== RIGHT JOYSTICK - RIGHT ==//
    if (ctl->axisRX() >= 25) {
      // map joystick values to motor speed
      int motorSpeed = map(ctl->axisRX(), 25, 512, 70, 255);
      // turn robot right - move left motor forward, keep right motor still
      digitalWrite(IN1pin, LOW);
      digitalWrite(IN2pin, HIGH);
      analogWrite(ENApin, motorSpeed);
      digitalWrite(IN3pin, LOW);
      digitalWrite(IN4pin, HIGH);
      analogWrite(ENBpin, motorSpeed);
    }

    //== LEFT JOYSTICK DEADZONE ==//
    if (ctl->axisY() > -25 && ctl->axisY() < 25 && ctl->axisRX() > -25 && ctl->axisRX() < 25) {
      // keep motors off
      analogWrite(ENApin,0);
      analogWrite(ENBpin, 0);
    }

      dumpGamepad(ctl);

  }

}

void processControllers() {
  for (auto myController : myControllers) {
    if (myController && myController->isConnected() && myController->hasData()) {
      if (myController->isGamepad()) {
        processGamepad(myController);
      }
      else {
        Serial.println("Unsupported controller");
      }
    }
  }
}



// Arduino setup function. Runs in CPU 1
void setup() {
  pinMode(ENApin, OUTPUT);
  pinMode(IN1pin, OUTPUT);
  pinMode(IN2pin, OUTPUT);
  pinMode(IN3pin, OUTPUT);
  pinMode(IN4pin, OUTPUT);
  pinMode(ENBpin, OUTPUT);

  for(int i = 0; i < numLeds; i++) pinMode(ledPins[i], OUTPUT);
  for(int i = 0; i < numLeds; i++) digitalWrite(ledPins[i], HIGH);

  pinMode(bumperPins[0], INPUT_PULLUP);
  pinMode(bumperPins[1], INPUT_PULLUP);

  Serial.begin(115200);
  Serial.printf("Firmware: %s\n", BP32.firmwareVersion());
  const uint8_t* addr = BP32.localBdAddress();
  Serial.printf("BD Addr: %2X:%2X:%2X:%2X:%2X:%2X\n", addr[0], addr[1], addr[2], addr[3], addr[4], addr[5]);

  // Setup the Bluepad32 callbacks
  BP32.setup(&onConnectedController, &onDisconnectedController);

  // "forgetBluetoothKeys()" should be called when the user performs
  // a "device factory reset", or similar.
  // Calling "forgetBluetoothKeys" in setup() just as an example.
  // Forgetting Bluetooth keys prevents "paired" gamepads to reconnect.
  // But it might also fix some connection / re-connection issues.
  BP32.forgetBluetoothKeys();

  // Enables mouse / touchpad support for gamepads that support them.
  // When enabled, controllers like DualSense and DualShock4 generate two connected devices:
  // - First one: the gamepad
  // - Second one, which is a "virtual device", is a mouse.
  // By default, it is disabled.
  BP32.enableVirtualDevice(false);
}

// Arduino loop function. Runs in CPU 1.
void loop() {
  // This call fetches all the controllers' data.
  // Call this function in your main loop.

  bool dataUpdated = BP32.update();
  if (dataUpdated)
    processControllers();

    
  if(remainingLives > 0){
    if ((digitalRead(bumperPins[0]) == LOW || digitalRead(bumperPins[1]) == LOW) && !bumperState) {
        digitalWrite(ledPins[remainingLives-1], LOW);
        remainingLives--;
        bumperState = true;
    }else if(digitalRead(bumperPins[0]) == HIGH && digitalRead(bumperPins[1]) == HIGH){
      bumperState = false;
    }
  }else{
    for(int i = 0; i < numLeds; i++) digitalWrite(ledPins[i], LOW);
    delay(1000);
    for(int i = 0; i < numLeds; i++) digitalWrite(ledPins[i], HIGH);
  }

  delay(50); 
  // The main loop must have some kind of "yield to lower priority task" event.
  // Otherwise, the watchdog will get triggered.
  // If your main loop doesn't have one, just add a simple `vTaskDelay(1)`.
  // Detailed info here:
  // https://stackoverflow.com/questions/66278271/task-watchdog-got-triggered-the-tasks-did-not-reset-the-watchdog-in-time

  //     vTaskDelay(1);
}