#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1

// Default Pico I2C0 Pins (Adjust if you wired it differently)
#define PIN_SDA 4
#define PIN_SCL 5

// Initialize the display using the dedicated I2C wire instance
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

void setup() {
  Serial.begin(115200);

  Wire.setSDA(PIN_SDA);
  Wire.setSCL(PIN_SCL);
  Wire.begin();

  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    while (true);
  }

  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0,0);
  display.println("GIT\nTRACKER\nREADY");
	display.setTextSize(1);
  display.setCursor(0, 48);
  display.println("start python script");
  display.println("on your pc");
  display.display();
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.startsWith("ERR:")) {
      display.clearDisplay();
      display.setCursor(0, 0);
      display.setTextSize(1);
      display.println("STATUS ERROR:");
      display.setCursor(0, 20);
      display.println(input.substring(4));
      display.display();
      return;
    }

    const int firstComma = input.indexOf(',');
    const int secondComma = input.indexOf(',', firstComma + 1);
    const int thirdComma = input.indexOf(',', secondComma + 1);

    if (firstComma == -1 || secondComma == -1 || thirdComma == -1) return;

    const String branch = input.substring(0, firstComma);
    const String staged = input.substring(firstComma + 1, secondComma);
    const String unstaged = input.substring(secondComma + 1, thirdComma);
    const String untracked = input.substring(thirdComma + 1);

    display.clearDisplay();

    display.setTextSize(1);
    display.setCursor(0, 0);
    display.print("branch:");

    display.setTextSize(2);
    display.setCursor(0, 12);
    display.print(branch);

    display.drawFastHLine(0, 32, 128, SSD1306_WHITE);

    display.setTextSize(1);
    display.setCursor(0, 42);
    display.print("+ staged:   "); display.println(staged);
    display.setCursor(0, 54);
    display.print("~ modified: "); display.println(unstaged);

    if (untracked.toInt() > 0) {
      display.setCursor(94, 42);
      display.print("? new");
      display.setCursor(100, 54);
      display.print(untracked);
    }

    display.display();
  }
}
