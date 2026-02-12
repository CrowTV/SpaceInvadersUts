const int pinY = A1;    
const int pinBoton = 3;
const int pinPausa = 4;   // Botón de pausa

unsigned long tiempoAnteriorDisparo = 0;
const unsigned long intervaloDisparo = 250;

unsigned long tiempoAnteriorMovimiento = 0;
const unsigned long intervaloMovimiento = 40;

bool estadoPausa = false;      
bool ultimoEstadoPausa = HIGH; // Para detectar flanco

void setup() {
  Serial.begin(9600);
  pinMode(pinBoton, INPUT_PULLUP);
  pinMode(pinPausa, INPUT_PULLUP);
}

void loop() {
  unsigned long tiempoActual = millis();

  int valorY = analogRead(pinY);
  int estadoBoton = digitalRead(pinBoton);
  int botonPausa = digitalRead(pinPausa);

  // ==============================
  // 🔹 BOTÓN DE PAUSA (ANTI-REBOTE POR FLANCO)
  // ==============================
  if (botonPausa == LOW && ultimoEstadoPausa == HIGH) {
    estadoPausa = !estadoPausa;   // Cambia estado interno
    Serial.println("P");          // Enviar señal a Python
  }

  ultimoEstadoPausa = botonPausa;

  // Si está en pausa no enviamos movimiento ni disparo
  if (estadoPausa) return;

  // ==============================
  // 🔹 MOVIMIENTO
  // ==============================
  if (tiempoActual - tiempoAnteriorMovimiento >= intervaloMovimiento) {
    tiempoAnteriorMovimiento = tiempoActual;

    if (valorY < 250) {
      Serial.println("R");
    } 
    else if (valorY > 750) {
      Serial.println("L");
    }
  }

  // ==============================
  // 🔹 DISPARO
  // ==============================
  if (estadoBoton == LOW) {
    if (tiempoActual - tiempoAnteriorDisparo >= intervaloDisparo) {
      tiempoAnteriorDisparo = tiempoActual;
      Serial.println("F");
    }
  }
}

