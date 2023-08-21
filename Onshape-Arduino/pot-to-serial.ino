int potval1 = 0;
int potval2 = 0;
int potval3 = 0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  potval1 = analogRead(0);
  potval2 = analogRead(1);
  potval3 = analogRead(2);
  String s = String(potval1) + "|" + String(potval2) + "|" + String(potval3);
  Serial.println(s);
  delay(500);
}
