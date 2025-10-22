from machine import Pin, PWM, ADC, I2C
from time import ticks_ms, ticks_diff, sleep
from ldc1602 import LCD1602
from dht20 import DHT20
import time

# Matériel

buzzer = PWM(Pin(20))       # Buzzer contrôlé en PWM
pot = ADC(2)                # Potentiomètre pour définir la consigne de température
led = PWM(Pin(18))          # LED d'état
led.freq(1000)              # Fréquence PWM pour la LED

# I2C pour LCD et capteur DHT20 (bus séparés)
i2c_lcd = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)  # Bus I2C pour le LCD
i2c_dht = I2C(1, scl=Pin(7), sda=Pin(6), freq=400000)  # Bus I2C pour le DHT20

# Initialisation des périphériques
lcd = LCD1602(i2c_lcd, 2, 16)  # LCD 16x2
lcd.display()
dht20 = DHT20(i2c_dht)         # Capteur de température et humidité

# Variables globales 

pos_alarm = 0                    # Position actuelle du mot "ALARM" pour le défilement
last_temp_measure = time.ticks_ms()  # Timestamp de la dernière mesure de température
led_state = False                     # État actuel de la LED (ON/OFF)
last_blink_Alarm = time.ticks_ms()    # Timestamp du dernier changement de clignotement de l'alarm
last_blink_LED= time.ticks_ms()                    # Timestamp du dernier changement de clignotement LED
last_alarm_scroll = time.ticks_ms()   # Timestamp du dernier défilement de "ALARM"
last_dimmer = time.ticks_ms()         # Timestamp du dernier update du dimmer
dimmer_step = 1000                     # Incrément de luminosité pour le fondu de la LED
brightness = 0                         # Niveau actuel de luminosité de la LED
mode_transition = 0                    # Pour gérer l'effacement du LCD en mode alarme
LED_OFF = 0                            # Initialisation des changements des clignottements de la LED
LED_BLINK = 1
LED_DIMMER = 2
pos_alarm = 0
alarm_visible = True
last_scroll = time.ticks_ms()
prev_pos_alarm = 0

# Fonctions

def lire_consigne():
    # Lit la valeur du potentiomètre et la convertit en consigne de température (15 à 35 °C)
    val = pot.read_u16()  # Valeur brute entre 0 et 65535
    consigne = 15 + (val / 65535) * (35 - 15)
    return round(consigne, 1)

def mesurer_temperature():
    # Retourne la température actuelle mesurée par le DHT20
    return round(dht20.dht20_temperature(), 1)


# Variables globales
pos_alarm = 0
prev_pos_alarm = 0
alarm_visible = True
last_blink_Alarm = time.ticks_ms()
last_scroll = time.ticks_ms()

pos_alarm = 0
alarm_visible = True
last_blink_Alarm = time.ticks_ms()
last_scroll = time.ticks_ms()

def afficher_lcd(consigne, temp, alarm=False):
    global pos_alarm, prev_pos_alarm, last_scroll, mode_transition

    # Ligne 0 : consigne
    lcd.setCursor(0, 0)
    lcd.print("Set: " + str(consigne) + " C")

    if alarm:
        now = time.ticks_ms()
        if mode_transition == 0:
            lcd.clear()
            mode_transition += 1
            pos_alarm = 0
            prev_pos_alarm = 0
            last_scroll = now
        # Défilement toutes les 1000 ms
        if time.ticks_diff(now, last_scroll) >= 1000:
            prev_pos_alarm = pos_alarm
            pos_alarm = (pos_alarm + 1) % (16 - len("ALARM") + 1)
            last_scroll = now

        # Clignotement basé sur le temps (500 ms ON / 500 ms OFF)
        if (now // 500) % 2 == 0:
            lcd.setCursor(prev_pos_alarm, 1)
            lcd.print("     ")  # efface mot précédent
            lcd.setCursor(pos_alarm, 1)
            lcd.print("ALARM")
        else:
            lcd.setCursor(pos_alarm, 1)
            lcd.print("     ")  # efface mot actuel
    else:
        # Pas d'alarme : afficher température
        lcd.setCursor(0, 1)
        lcd.print("Ambient: " + str(temp) + " C")
        pos_alarm = 0
        prev_pos_alarm = 0
        mode_transition = 0


def alarme_active():
    # Active le buzzer avec une tonalité définie
    buzzer.freq(1000)
    buzzer.duty_u16(30000)

def alarme_desactive():
    # Désactive le buzzer
    buzzer.duty_u16(0)

def clignoter_led(periode_s):
    # Fait clignoter la LED avec une période donnée (en secondes)
    global last_blink_LED, led_state
    now = time.ticks_ms()
    if time.ticks_diff(now, last_blink_LED) >= int((periode_s * 1000) / 2):
        # Inverse l'état de la LED pour le clignotement
        led_state = not led_state
        led.duty_u16(65535 if led_state else 0)
        last_blink_LED = now

def dimmer():
    # Fait un fondu progressif de la LED en augmentant ou diminuant sa luminosité
    global brightness, dimmer_step, last_dimmer
    now = time.ticks_ms()
    if time.ticks_diff(now, last_dimmer) >= 20:
        led.duty_u16(brightness)
        # Incrémente ou décrémente la luminosité
        brightness += dimmer_step
        # Inverse la direction du fondu si on atteint les limites
        if brightness <= 0 or brightness >= 65535:
            dimmer_step = -dimmer_step
        last_dimmer = now

# fonction pour que le clignotement de la Led ne pose pas de problème
def update_led():
    global led_mode
    if led_mode == LED_OFF:
        led.duty_u16(0)
    elif led_mode == LED_BLINK:
        clignoter_led(2)
    elif led_mode == LED_DIMMER:
        dimmer()


# Boucle principale


temperature = mesurer_temperature()

while True:
    consigne = lire_consigne()

    now = time.ticks_ms()
    # Mesure la température toutes les secondes
    if time.ticks_diff(now, last_temp_measure) > 1000:
        temperature = mesurer_temperature()
        last_temp_measure = now
        
        
    # Température dépassant de plus de 3 °C la consigne
    if temperature > consigne + 3:
        afficher_lcd(consigne, temperature, alarm=True)
        alarme_active()
        led_mode = LED_DIMMER
    # Température légèrement au-dessus de la consigne
    elif temperature > consigne:
        afficher_lcd(consigne, temperature, alarm=False)
        alarme_desactive()
        led_mode = LED_BLINK
    # Température en dessous de la consigne
    else:
        afficher_lcd(consigne, temperature, alarm=False)
        alarme_desactive()
        led.duty_u16(0)
        led_mode = LED_OFF
        
    update_led()

