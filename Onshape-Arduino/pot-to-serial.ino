#include <Wire.h> 
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27,16,2);

int potval1 = 0;
int potval2 = 0;
int potval3 = 0;

void setup() {
  Serial.begin(115200);
  lcd.init();
  lcd.backlight();
}

void loop() {
  potval1 = analogRead(0);
  potval2 = analogRead(1);
  potval3 = analogRead(2);

  String lcd1 = "P1:" + String(potval1) + " | P2:" + String(potval2) + "  ";
  lcd.setCursor(0,0);
  lcd.print(lcd1);

  String lcd2 = "P3:" + String(potval3) + "  ";
  lcd.setCursor(0,1);
  lcd.print(lcd2);

  String s = String(potval1) + "|" + String(potval2) + "|" + String(potval3);
  Serial.println(s);
  delay(100);
}
