#include <Servo.h>
#include <ArduinoJson.h>
#include <HX711.h>

// Pin definitions
const int SERVO_X_PIN = 9;
const int SERVO_Y_PIN = 10;
const int SERVO_Z_PIN = 11;
const int PUMP_PIN = 6;
const int UV_LED_PIN = 5;
const int SCALE_DOUT_PIN = 2;
const int SCALE_SCK_PIN = 3;
const int LIMIT_SWITCH_X = A0;
const int LIMIT_SWITCH_Y = A1;
const int LIMIT_SWITCH_Z = A2;

// System constants
const float STEPS_PER_ML = 100.0;  // Pump steps per milliliter
const float SCALE_CALIBRATION_FACTOR = -1000.0;  // Adjust based on calibration
const unsigned long STERILIZATION_TIME = 300000;  // 5 minutes in milliseconds
const int SERVO_SPEED_DELAY = 15;  // Delay between servo movements (ms)

// System components
Servo servoX, servoY, servoZ;
HX711 scale;

// System state
bool isRunning = false;
bool isSterilizing = false;
float targetVolume = 0.0;
float currentWeight = 0.0;
unsigned long sterilizationStartTime = 0;

// JSON document for communication
StaticJsonDocument<200> doc;

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  
  // Initialize servos
  servoX.attach(SERVO_X_PIN);
  servoY.attach(SERVO_Y_PIN);
  servoZ.attach(SERVO_Z_PIN);
  
  // Initialize pins
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(UV_LED_PIN, OUTPUT);
  pinMode(LIMIT_SWITCH_X, INPUT_PULLUP);
  pinMode(LIMIT_SWITCH_Y, INPUT_PULLUP);
  pinMode(LIMIT_SWITCH_Z, INPUT_PULLUP);
  
  // Initialize scale
  scale.begin(SCALE_DOUT_PIN, SCALE_SCK_PIN);
  scale.set_scale(SCALE_CALIBRATION_FACTOR);
  scale.tare();
  
  // Home all axes
  homeAxes();
  
  isRunning = true;
}

void loop() {
  // Check for incoming commands
  if (Serial.available()) {
    String jsonString = Serial.readStringUntil('\n');
    DeserializationError error = deserializeJson(doc, jsonString);
    
    if (error) {
      sendError("Invalid JSON command");
      return;
    }
    
    processCommand();
  }
  
  // Check sterilization status
  if (isSterilizing) {
    if (millis() - sterilizationStartTime >= STERILIZATION_TIME) {
      stopSterilization();
    }
  }
  
  // Monitor limit switches
  checkLimitSwitches();
}

void processCommand() {
  const char* cmd = doc["cmd"];
  
  if (strcmp(cmd, "MOVE") == 0) {
    moveRobotArm();
  }
  else if (strcmp(cmd, "DISPENSE") == 0) {
    dispenseLiquid();
  }
  else if (strcmp(cmd, "STERILIZE") == 0) {
    startSterilization();
  }
  else if (strcmp(cmd, "EMERGENCY_STOP") == 0) {
    emergencyStop();
  }
  else {
    sendError("Unknown command");
  }
}

void moveRobotArm() {
  int x = doc["x"] | 90;  // Default to center position
  int y = doc["y"] | 90;
  int z = doc["z"] | 90;
  int speed = doc["speed"] | 50;
  
  // Constrain values
  x = constrain(x, 0, 180);
  y = constrain(y, 0, 180);
  z = constrain(z, 0, 180);
  speed = constrain(speed, 1, 100);
  
  // Calculate delay based on speed
  int moveDelay = map(speed, 1, 100, 50, 5);
  
  // Move each axis smoothly
  moveServoSmooth(servoX, x, moveDelay);
  moveServoSmooth(servoY, y, moveDelay);
  moveServoSmooth(servoZ, z, moveDelay);
  
  sendAck();
}

void moveServoSmooth(Servo &servo, int targetPos, int moveDelay) {
  int currentPos = servo.read();
  
  if (currentPos < targetPos) {
    for (int pos = currentPos; pos <= targetPos; pos++) {
      servo.write(pos);
      delay(moveDelay);
    }
  }
  else {
    for (int pos = currentPos; pos >= targetPos; pos--) {
      servo.write(pos);
      delay(moveDelay);
    }
  }
}

void dispenseLiquid() {
  float volume = doc["volume"];
  int pumpId = doc["pump"];
  float targetWeight = volume;  // Assuming 1ml = 1g
  
  // Reset scale
  scale.tare();
  
  // Dispense liquid using closed-loop control
  while (currentWeight < targetWeight) {
    // Activate pump
    digitalWrite(PUMP_PIN, HIGH);
    
    // Read weight
    currentWeight = scale.get_units();
    
    // Small delay to prevent rapid readings
    delay(50);
    
    // Stop if we're close enough
    if (abs(currentWeight - targetWeight) < 0.1) {
      break;
    }
  }
  
  // Stop pump
  digitalWrite(PUMP_PIN, LOW);
  
  sendAck();
}

void startSterilization() {
  if (!isSterilizing) {
    digitalWrite(UV_LED_PIN, HIGH);
    isSterilizing = true;
    sterilizationStartTime = millis();
    sendAck();
  }
}

void stopSterilization() {
  digitalWrite(UV_LED_PIN, LOW);
  isSterilizing = false;
}

void homeAxes() {
  // Move all axes until limit switches are triggered
  while (!digitalRead(LIMIT_SWITCH_X) || 
         !digitalRead(LIMIT_SWITCH_Y) || 
         !digitalRead(LIMIT_SWITCH_Z)) {
           
    if (!digitalRead(LIMIT_SWITCH_X)) servoX.write(0);
    if (!digitalRead(LIMIT_SWITCH_Y)) servoY.write(0);
    if (!digitalRead(LIMIT_SWITCH_Z)) servoZ.write(0);
    
    delay(SERVO_SPEED_DELAY);
  }
  
  // Move slightly away from limit switches
  servoX.write(5);
  servoY.write(5);
  servoZ.write(5);
}

void checkLimitSwitches() {
  if (digitalRead(LIMIT_SWITCH_X) == LOW || 
      digitalRead(LIMIT_SWITCH_Y) == LOW || 
      digitalRead(LIMIT_SWITCH_Z) == LOW) {
    emergencyStop();
  }
}

void emergencyStop() {
  // Stop all motion
  servoX.detach();
  servoY.detach();
  servoZ.detach();
  digitalWrite(PUMP_PIN, LOW);
  digitalWrite(UV_LED_PIN, LOW);
  
  isRunning = false;
  isSterilizing = false;
  
  sendError("Emergency stop triggered");
}

void sendAck() {
  Serial.println("OK");
}

void sendError(const char* message) {
  StaticJsonDocument<100> response;
  response["error"] = message;
  serializeJson(response, Serial);
  Serial.println();
} 