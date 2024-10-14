#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Stepper.h>
#include <DNSServer.h>
#include <Preferences.h>
#include <WebServer.h>

// Preferences object to interface with ESP32s internal filesystem
Preferences preferences;

// Motor control pins
const int azimuthStepPin1 = 2;
const int azimuthStepPin2 = 3;
const int azimuthStepPin3 = 4;
const int azimuthStepPin4 = 5;
const int elevationStepPin1 = 6;
const int elevationStepPin2 = 7;
const int elevationStepPin3 = 8;
const int elevationStepPin4 = 9;

// Steps per revolution for your stepper motor
const int stepsPerRevolution = 200;

// Create instances for each stepper motor
Stepper azimuthMotor(stepsPerRevolution, azimuthStepPin1, azimuthStepPin3, azimuthStepPin2, azimuthStepPin4);
Stepper elevationMotor(stepsPerRevolution, elevationStepPin1, elevationStepPin3, elevationStepPin2, elevationStepPin4);

// WiFi and server configuration
const char* ap_ssid = "ESP32_AP";
const char* ap_password = "12345678";
char server_ip[32] = "";
int server_port = 5000;

int currentAzimuth = 0;
int currentElevation = 0;

DNSServer dnsServer;
WebServer server(80);

const char* htmlPage = "<html>\
                        <head>\
                        <title>ESP32 WiFi Configuration</title>\
                        <style>\
                        body { font-family: Arial; }\
                        h1 { color: #333; }\
                        </style>\
                        </head>\
                        <body>\
                        <h1>ESP32 WiFi Configuration</h1>\
                        <form action=\"/save\" method=\"post\">\
                        SSID: <input type=\"text\" name=\"ssid\"><br>\
                        Password: <input type=\"password\" name=\"password\"><br>\
                        Server IP: <input type=\"text\" name=\"server_ip\"><br>\
                        <input type=\"submit\" value=\"Save\">\
                        </form>\
                        </body>\
                        </html>";

void setup() {
  Serial.begin(115200);
  while (!Serial); // wait for serial port to connect. Needed for native USB

  preferences.begin("wifi-config", false);

  // Load configuration
  if (!loadConfiguration()) {
    Serial.println("Failed to load configuration");
    return;
  }
  Serial.println("Configuration loaded successfully");

  String ssid_str = preferences.getString("ssid", "");
  String password_str = preferences.getString("password", "");

  // Check if both SSID and password are stored
  if (ssid_str.length() > 0 && password_str.length() > 0) {
    // Try to connect to stored WiFi credentials
    WiFi.begin(ssid_str, password_str);
    if (WiFi.waitForConnectResult() == WL_CONNECTED) {
      Serial.println("Connected to WiFi");
      Serial.print("STA IP address: ");
      Serial.println(WiFi.localIP());
      // Set the speed for the motors
      azimuthMotor.setSpeed(60);  // Set speed in RPM
      elevationMotor.setSpeed(60);  // Set speed in RPM
      return; // Exit setup() if connected
    }
  }
  setupAP(); // if WiFI connection fails
}

void loop() {
  dnsServer.processNextRequest(); // only runs if failed to connect to WiFi
  server.handleClient(); // for motor control HTTP requests

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String serverUrl = "http://" + String(server_ip) + ":" + String(server_port) + "/get_current_position";
    http.begin(serverUrl);
    int httpCode = http.GET();
    Serial.print("HTTP response code: ");
    Serial.println(httpCode);
    if (httpCode > 0) {
      if (httpCode == HTTP_CODE_OK) {
        String values = http.getString();

        StaticJsonDocument<200> doc;
        DeserializationError error = deserializeJson(doc, values);

        if (!error) {
          int azimuth = doc["azimuth"];
          int elevation = doc["elevation"];

          Serial.print("Azimuth: ");
          Serial.println(azimuth);
          Serial.print("Elevation: ");
          Serial.println(elevation);

          // Move motors to the desired positions
          moveToPosition(azimuth, elevation);
        } else {
          Serial.print("deserializeJson() failed: ");
          Serial.println(error.c_str());
        }
      }
    } else {
      Serial.println("Error on HTTP request");
      setupAP(); // to reconfigure IP address
    }

    http.end();
  }

  delay(1000); // Fetch new position every second
}

void handleRoot() {
  server.send(200, "text/html", htmlPage);
}

void handleSave() {
  String ssid = server.arg("ssid");
  String password = server.arg("password");
  String server_ip = server.arg("server_ip");

  // Save credentials and server configuration to Preferences
  preferences.putString("ssid", ssid);
  preferences.putString("password", password);
  preferences.putString("server_ip", server_ip);

  // Respond to the client
  server.send(200, "text/html", "Credentials and Server Configuration Saved. Rebooting...");
  delay(1000);
  ESP.restart();
}

void handleReset() {
  resetPreferences();
  server.send(200, "text/html", "Preferences have been reset. Rebooting...");
  delay(1000);
  ESP.restart();
}

bool loadConfiguration() {
  String server_ip_str = preferences.getString("server_ip", "");

  // Use Strings directly
  server_ip_str.toCharArray(server_ip, sizeof(server_ip));

  return true;
}

void moveToPosition(int azimuth, int elevation) {
  // move "angle/200" steps
  int stepsToMoveAzimuth = (azimuth - currentAzimuth)/200;
  int stepsToMoveElevation = (elevation - currentElevation)/200;

  // Move the azimuth motor
  azimuthMotor.step(stepsToMoveAzimuth);

  // Move the elevation motor
  elevationMotor.step(stepsToMoveElevation);

  // Update current positions
  currentAzimuth = azimuth;
  currentElevation = elevation;
}

void resetPreferences() {
  preferences.begin("wifi-config", false);
  preferences.clear();
  preferences.end();
  Serial.println("Preferences have been reset.");
}

void setupAP() {
  Serial.println("Setting up Access Point..."); // WiFi was not connected
  WiFi.softAP(ap_ssid, ap_password);

  IPAddress AP_IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(AP_IP);

  // Setup DNS Server to redirect all traffic to the captive portal
  // No need to navigate to web address with APIP
  dnsServer.start(53, "*", WiFi.softAPIP());

  server.on("/", handleRoot);
  server.on("/save", handleSave);
  server.on("/reset", handleReset);
  server.begin();
  Serial.println("HTTP server started");
}