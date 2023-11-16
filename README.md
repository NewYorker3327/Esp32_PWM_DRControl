# Esp32_PWM_DRControl

## Conexões:

### Entradas:

Visor: {..., PINO 21(sda) e 22(scl)}

PWM: {D12, PINO 27} = GPIO 12 = PWM OUT

TelaPot: {..., PINO 32}

Sensor 1: {..., PINO 5}

Sensor 2: {..., PINO 16}

### Saídas:

Pre-Charge: {D13, PINO 28} = GPIO 13 = BOOLEAN



## ALGORITMO: 

Ao Energizar o circuito, GPIO 13 (Pre-Charge) é igual 0 por 5 segundos, e após isso, é igual a 1, indefinidamente

Ao Energizar o circuito, se GPIO 35 (TelaBot) for 0, a saída PWM (GPIO 12) É 432Hz, e o duty cycle gradativamente aumenta, até alcançar o valor setado pelo potenciômetro TelaPot (GPIO 4)

Ao Energizar o circuito, se GPIO 35 (TelaBot) for 1, a saída PWM (GPIO 12) toca a intro musical, e após isso, o duty cycle gradativamente aumenta, até alcançar o valor setado pelo potenciômetro TelaPot (GPIO 4) na frequência 432hz

## Dependências do MAIN:

### Normais:
```
machine
dht
_thread
time
math
network
socket
esp32
gc
```

### Em código:
```
i2c_lcd
ds18x20
onewir
outros
wifi
login_wifi
```

## Requisitos:

• MICROPYTHON;

• Minimo de 64KB (32KB do programa e 32KB do boot e logs) de memória flash;

• Conexão a WIFI.
