from machine import Pin, PWM, ADC
from time import ticks_ms, ticks_diff, sleep

# On initialise toutes les broches
buzzer = PWM(Pin(27)) # Buzzer sur la pin 27
ROTARY_ANGLE_SENSOR = ADC(2) # Capteur rotatif pour le volume
BOUTTON = Pin(16, Pin.IN, Pin.PULL_UP)  # Bouton  sur la pin 16
LED = Pin(18, Pin.OUT) # LED pour indication visuelle
LED.value(1) # LED allumée au démarrage

# Mélodie 1
notes_a = [523, 587, 659, 698, 784, 880, 988, 1047]
durations_a = [0.3, 0.3, 0.3, 0.3, 0.4, 0.4, 0.4, 0.6]

# Mélodie 2
notes_b = [440, 440, 440, 349, 440, 349, 440, 349, 440, 440, 440, 349] 
durations_b = [0.5, 0.5, 0.5, 0.35, 0.5, 0.35, 0.5, 0.35, 0.5, 0.5, 0.5, 0.35]

# Initialisation des paramètres
current_melody = 'B' # Mélodie actuelle
last_button_state = 1  # État précédent du bouton
note_index_a = 0 # Index de la note pour la mélodie A
note_index_b = 0 # Index de la note pour la mélodie B

# Boucle principal
while True:
    # Lecture du bouton
    button_state = BOUTTON.value()
    print(button_state)
    
    # On vérifie que on a bien laché le boutton
    if last_button_state == 1 and button_state == 0:
        if current_melody == 'B':
            current_melody = 'A'
        else:
            current_melody = 'B'

        
        # Repartir au début de la musique
        if current_melody == 'A':
            note_index_a = 0
        else:
            note_index_b = 0
            
    # Mettre à jour l'état précédent du bouton
    last_button_state = button_state

    # On sélectionne la mélodie
    if current_melody == 'A':
        notes = notes_a
        durations = durations_a
        note_index = note_index_a
    else:
        notes = notes_b
        durations = durations_b
        note_index = note_index_b

    # Jouer la note courante
    freq = notes[note_index % len(notes)]
    dur = durations[note_index % len(durations)]
    buzzer.freq(freq)
    start = ticks_ms() # Début du chronomètre
    LED.value(1)    # Allumer la LED pendant la note

    # On fait une boucle qui tourne le temps de la durée de la note à la place d'un sleep pour plus de fluidité. Lors de cette boucle, On utilise un cronomètre.
    while ticks_diff(ticks_ms(), start) < dur * 1000:
        
        # Interruption si le bouton est pressé
        if  BOUTTON.value()== 1:
            break 
        volume = ROTARY_ANGLE_SENSOR.read_u16()
        
        # Lecture du volume via le capteur rotatif
        volume = min(max(volume, 0), 45000)  # Limitation pour éviter la saturation
        duty = int((volume / 45000) * 3000)  # Conversion en duty cycle pour le buzzer
        buzzer.duty_u16(duty)
        sleep(0.01)
        
    # On coupe la note de musique que l'on est en train de jouer
    buzzer.duty_u16(0)
    LED.value(0) # Éteindre la LED
    sleep(0.05)  # Petit délai avant la prochaine note

    # On change de note de musique
    if current_melody == 'A':
        note_index_a += 1
    else:
        note_index_b += 1
