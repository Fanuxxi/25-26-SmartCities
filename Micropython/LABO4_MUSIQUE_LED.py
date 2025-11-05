from machine import ADC
from ws2812 import WS2812
from time import ticks_ms, ticks_diff, sleep
import urandom

# Initialisation du micro et de la LED
BROCHE_LED = 18                # Broche pour la LED RGB
NOMBRE_LEDS = 1                # Nombre de LEDs
led = WS2812(BROCHE_LED, NOMBRE_LEDS)
micro = ADC(1)                 # Microphone sur entrée analogique

# Paramètres pour la détection
TAILLE_FENETRE_COURTE = 5      # Fenêtre courte pour analyse rapide
TAILLE_FENETRE_LONGUE = 50     # Fenêtre longue pour moyenne globale
SEUIL = 1.15                   # Facteur pour détecter un pic sonore
INTERVALLE_MIN = 120           # Intervalle minimum entre deux battements (ms)
DECALAGE_MICRO = 50            # Filtrage du bruit
DELAI_ECHANTILLON = 0.005      # Délai entre deux lectures

# Couleurs disponibles pour la LED
COULEURS = [
    (255, 0, 0), (255, 128, 0), (255, 255, 0),
    (0, 255, 0), (0, 255, 255), (0, 128, 255),
    (128, 0, 255), (255, 0, 255), (255, 255, 255)
]

# Variables pour la détection et le calcul BPM
fenetre_courte = []            # Dernières valeurs pour analyse rapide
fenetre_longue = []            # Valeurs pour moyenne globale
dernier_battement = 0          # Temps du dernier battement
tampon_bpm = []                # Liste pour filtrer le BPM
tampon_bpm_minute = []         # Liste pour moyenne par minute
ECHANTILLONS_BPM_MAX = 5       # Nombre max d'échantillons BPM
derniere_verif_minute = ticks_ms()

print(">>> Détection de rythme prête...")

def lire_valeur_micro():
    # Lit la valeur du micro et ignore le bruit faible
    val = micro.read_u16() // 256
    return val if val > DECALAGE_MICRO else 0

def maj_fenetres(val):
    # Ajoute la valeur aux deux fenêtres et supprime les plus anciennes
    fenetre_courte.append(val)
    fenetre_longue.append(val)
    if len(fenetre_courte) > TAILLE_FENETRE_COURTE:
        fenetre_courte.pop(0)
    if len(fenetre_longue) > TAILLE_FENETRE_LONGUE:
        fenetre_longue.pop(0)

def moyenne(fenetre):
    return sum(fenetre) / len(fenetre) if fenetre else 0

def variance(fenetre):
    # Calcule la variance pour détecter les pics
    m = moyenne(fenetre)
    return sum((x - m) ** 2 for x in fenetre) / len(fenetre) if fenetre else 0

def couleur_aleatoire():
    # Choisit une couleur au hasard
    return COULEURS[urandom.getrandbits(3) % len(COULEURS)]

while True:
    niveau_son = lire_valeur_micro()

    if niveau_son:
        maj_fenetres(niveau_son)
        moy_courte = moyenne(fenetre_courte)
        moy_longue = moyenne(fenetre_longue)
        var_courte = variance(fenetre_courte)
        maintenant = ticks_ms()

        # Détection d'un battement
        if moy_courte > moy_longue * SEUIL and var_courte > 50 and (maintenant - dernier_battement) > INTERVALLE_MIN:
            intervalle_ms = ticks_diff(maintenant, dernier_battement)
            dernier_battement = maintenant

            # Calcul du BPM si intervalle plausible
            if 300 < intervalle_ms < 2000:
                bpm = 60000 / intervalle_ms
                tampon_bpm.append(bpm)
                if len(tampon_bpm) > ECHANTILLONS_BPM_MAX:
                    tampon_bpm.pop(0)
                bpm_filtre = sum(tampon_bpm) / len(tampon_bpm)
                tampon_bpm_minute.append(bpm_filtre)
                print(f"BPM filtré: {bpm_filtre:.1f}")

            # Changement de couleur sur le battement
            couleur = couleur_aleatoire()
            led.pixels_fill(couleur)
            led.pixels_show()
            print("Beat détecté ! niveau:", int(niveau_son), "couleur:", couleur)

        # Mise à jour chaque minute
        if ticks_diff(maintenant, derniere_verif_minute) >= 60000:
            if tampon_bpm_minute:
                bpm_moyen_minute = sum(tampon_bpm_minute) / len(tampon_bpm_minute)
                print(f"Moyenne BPM sur la dernière minute : {bpm_moyen_minute:.1f}")
                try:
                    with open("bpm_log.txt", "a") as f:
                        f.write(f"{bpm_moyen_minute:.1f}\n")
                    print("BPM moyen écrit dans bpm_log.txt")
                except Exception as e:
                    print("Erreur lors de l'écriture :", e)
                tampon_bpm_minute.clear()

            derniere_verif_minute = maintenant

    sleep(DELAI_ECHANTILLON)