# EXERCICE 5 : CONSTRUCTION D'UNE HORLOGE AVEC UN RASPBERRY PI PICO W ET UN SERVO MOTEUR

## Objectif

Dans cet exercice, vous allez réaliser une horloge en utilisant un Raspberry Pi Pico W et un servo moteur. L'heure sera récupérée à partir d'internet, et l'angle du servo moteur variera en fonction de l'heure pour indiquer la position des aiguilles.

## Matériel

1. Raspberry Pi Pico W
2. Servo moteur

## Étapes à suivre

### 1. Connexion à Internet

- Branchez votre Raspberry Pi Pico W au réseau Wi-Fi en utilisant la bibliothèque MicroPython network.
- Utilisez une API (comme ntptime ou une autre API de temps) pour récupérer l'heure actuelle à partir d'internet.

### 2. Calcul de l'angle du servo

- Vous allez contrôler un servo moteur dont l'angle peut varier entre 0° et 180°.
- Sur une feuille de papier, dessinez un cadran d'horloge de 12 heures. Assurez-vous que :
  - L'heure 12 correspond à un angle de 0°.
  - L'heure 6 correspond à un angle de 90°.
  - Déterminez l'angle correspondant à chaque heure complète (par exemple, 1h, 2h, etc.) sur ce cadran.

### 3. Contrôle du servo

- Utilisez la bibliothèque machine pour contrôler le servo à partir du Raspberry Pi Pico W.
- En fonction de l'heure récupérée, calculez l'angle correspondant du servo.
- Le servo doit pointer à l'angle correct en fonction de l'heure actuelle.

## Bonus

### 1. Fuseau horaire

- Ajoutez un bouton poussoir connecté à votre Raspberry Pi Pico W.
- Lorsque le bouton est pressé une fois, l'horloge change de fuseau horaire (exemple : UTC, UTC+1, UTC-5, etc.).
- Programmez le changement de fuseau horaire en récupérant l'heure en fonction du décalage sélectionné.

### 2. Format 24 heures

- Si le bouton est pressé deux fois rapidement (double clic), l'horloge passe en mode 24 heures.
- Dans ce mode, l'angle du servo couvrira 180° pour une journée complète, où :
  - L'heure 0 (minuit) correspond à 0°.
  - L'heure 12 correspond à 90°.
  - L'heure 24 (minuit suivant) correspond à 180°.
