# Esp32_PWM_DRControl

Entradas:

TelaBot: {D16, PINO 6} = GPIO 16 = BOOLEAN
TelaPot:{D4, PINO 5} = GPIO 4 = ANALOG
UVLO: {D34, PINO 19} = GPIO 34 = ANALOG

Saídas:

Pre-Charge: {D13, PINO 28} = GPIO 13 = BOOLEAN
PWM: {D12, PINO 27} = GPIO 12 = PWM OUT

ALGORITMO: 

Ao Energizar o circuito, GPIO 13 (Pre-Charge) é igual 0 por 5 segundos, e após isso, é igual a 1, indefinidamente

Ao Energizar o circuito, se GPIO 35 (TelaBot) for 0, a saída PWM (GPIO 12) É 432Hz, e o duty cycle gradativamente aumenta, até alcançar o valor setado pelo potenciômetro TelaPot (GPIO 4)

Ao Energizar o circuito, se GPIO 35 (TelaBot) for 1, a saída PWM (GPIO 12) toca a intro musical, e após isso, o duty cycle gradativamente aumenta, até alcançar o valor setado pelo potenciômetro TelaPot (GPIO 4) na frequência 432hz
