# Exercice 3 – Contrôle de Température (MicroPython)

## Objectif
Créer un thermostat intelligent avec le Raspberry Pi Pico W et divers capteurs.

##  Matériel
- Raspberry Pi Pico W  
- Capteur température/humidité  
- Potentiomètre  
- LED  
- Écran LCD  
- Buzzer  
- Câbles

## Fonctionnement
- Lecture de la température (1x/sec)
-  Potentiomètre = température de consigne (15°C → 35°C)
- LCD affiche :
  - `Set:` température cible
  - `Ambient:` température ambiante
- Si température > consigne :
  - LED clignote (0,5 Hz)
- Si température > consigne + 3°C :
  - LED clignote plus vite
  - Buzzer active
  - "ALARM" affiché

## Bonus
- Dimmer LED progressif  
- "ALARM" clignotant ou défilant




