import sys
import re
import pygame
from ivy.std_api import IvyInit, IvyStart, IvyStop, IvyBindMsg, IvySendMsg

# --- Configuration graphique du Moteur de Fusion (Log) ---
LARGEUR, HAUTEUR = 500, 320
BLANC = (255, 255, 255)
NOIR = (30, 30, 30)
ROUGE = (200, 50, 50)
VERT = (50, 200, 50)
ORANGE = (230, 150, 30)

# Durée maximale d'attente entre deux modalités (en millisecondes)
TIMEOUT_MS = 2500

# --- Structure de données de fusion ---
etat_fusion = {
    "action": None,
    "forme": None,
    "couleur": "defaut",
    "position_x": None,
    "position_y": None,
    "attente_clic": False,
    "timestamp": 0
}

def reinitialiser_fusion():
    """Remet à zéro l'état après exécution ou expiration du délai."""
    global etat_fusion
    etat_fusion = {
        "action": None,
        "forme": None,
        "couleur": "defaut",
        "position_x": None,
        "position_y": None,
        "attente_clic": False,
        "timestamp": 0
    }

def update_timer():
    """Démarre le timer dès la première modalité reçue."""
    global etat_fusion
    if etat_fusion["timestamp"] == 0:
        etat_fusion["timestamp"] = pygame.time.get_ticks()

def verifier_et_executer(force_exec=False):
    """
    Vérifie si les conditions d'exécution sont réunies.
    force_exec=True est appelé quand le timeout expire (paramètres optionnels validés par défaut).
    """
    global etat_fusion

    # 1. Action CREER
    if etat_fusion["action"] == "CREER" and etat_fusion["forme"]:
        # Cas complet avec position explicite
        if etat_fusion["position_x"] is not None:
            x, y = etat_fusion["position_x"], etat_fusion["position_y"]
            msg = f"Palette:Creer {etat_fusion['forme']} {x} {y} {etat_fusion['couleur']}"
            IvySendMsg(msg)
            print(f"\n[FUSION REUSSIE] -> {msg}")
            reinitialiser_fusion()
        # Cas où la position est omise (timeout écoulé sans clic demandé)
        elif force_exec and not etat_fusion["attente_clic"]:
            x, y = 250, 250  # Position centrale par défaut
            msg = f"Palette:Creer {etat_fusion['forme']} {x} {y} {etat_fusion['couleur']}"
            IvySendMsg(msg)
            print(f"\n[FUSION REUSSIE (Position par défaut)] -> {msg}")
            reinitialiser_fusion()

    # 2. Action DEPLACER
    elif etat_fusion["action"] == "DEPLACER" and etat_fusion["position_x"] is not None:
        msg = f"Palette:Deplacer {etat_fusion['position_x']} {etat_fusion['position_y']}"
        IvySendMsg(msg)
        print(f"\n[FUSION REUSSIE] -> {msg}")
        reinitialiser_fusion()

# --- Callbacks Ivy ---
def on_parole(agent, *args):
    """Reçoit la commande reconnue par sra5."""
    global etat_fusion
    texte = args[0].lower().strip()
    print(f"[Modalité Parole] Reçu : {texte}")
    update_timer()

    # Détection de l'action
    if any(k in texte for k in ["creer", "créer", "crée", "dessine", "dessiner"]):
        etat_fusion["action"] = "CREER"
    elif any(k in texte for k in ["deplacer", "déplacer", "déplace", "bouge", "mets"]):
        etat_fusion["action"] = "DEPLACER"

    # Détection de la forme
    for f in ["rectangle", "cercle", "triangle", "losange", "rond", "ellipse"]:
        if f in texte:
            etat_fusion["forme"] = "cercle" if f in ["rond", "ellipse"] else f

    # Détection de la couleur
    for c in ["rouge", "vert", "bleu"]:
        if c in texte:
            etat_fusion["couleur"] = c

    # Intention de pointage explicite
    if any(p in texte for p in ["ici", "là", "cet endroit"]):
        etat_fusion["attente_clic"] = True

    verifier_et_executer()

def on_geste(agent, *args):
    """Reçoit la forme reconnue par OneDollarIvy."""
    global etat_fusion
    forme = args[0].lower().strip()
    print(f"[Modalité Geste] Forme reçue : {forme}")
    update_timer()

    etat_fusion["forme"] = forme
    verifier_et_executer()

def on_clic(agent, *args):
    """Reçoit les coordonnées du clic sur la palette."""
    global etat_fusion
    x, y = int(args[0]), int(args[1])
    print(f"[Modalité Pointage] Clic en X:{x} Y:{y}")

    # Accepte le clic si on attendait un pointage ou si une action est en cours
    if etat_fusion["attente_clic"] or etat_fusion["action"] is not None:
        etat_fusion["position_x"] = x
        etat_fusion["position_y"] = y
        update_timer()
        verifier_et_executer()

# --- Initialisation Ivy ---
IvyInit("MoteurFusion", "Prêt", 0)
IvyStart("127.255.255.255:2010")

IvyBindMsg(on_parole, "^sra5 Parsed='(.*?)'")
IvyBindMsg(on_geste, r"^1_Recognizer gesture=(.*)")
IvyBindMsg(on_clic, r"^Palette Clic x=(\d+) y=(\d+)")

# --- Initialisation Pygame ---
pygame.init()
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Moteur de Fusion Multimodale")
police = pygame.font.SysFont("Arial", 18)
horloge = pygame.time.Clock()

def dessiner_interface():
    fenetre.fill(NOIR)
    titre = police.render("--- ÉTAT DE LA FUSION ---", True, BLANC)
    fenetre.blit(titre, (140, 15))

    y_offset = 55
    elements = [
        ("ACTION", etat_fusion["action"]),
        ("FORME", etat_fusion["forme"]),
        ("COULEUR", etat_fusion["couleur"]),
        ("POS X", etat_fusion["position_x"]),
        ("POS Y", etat_fusion["position_y"]),
        ("ATTENTE CLIC", etat_fusion["attente_clic"])
    ]

    for label, val in elements:
        col = VERT if val not in [None, False] else ROUGE
        if label == "COULEUR" and val == "defaut":
            col = BLANC
        txt = police.render(f"{label} : {val}", True, col)
        fenetre.blit(txt, (40, y_offset))
        y_offset += 30

    # Affichage de la jauge temporelle
    if etat_fusion["timestamp"] > 0:
        ecoule = pygame.time.get_ticks() - etat_fusion["timestamp"]
        restant = max(0, TIMEOUT_MS - ecoule)
        txt_timer = police.render(f"Timeout : {restant} ms", True, ORANGE)
        fenetre.blit(txt_timer, (40, y_offset + 10))

# --- Boucle principale ---
try:
    en_cours = True
    while en_cours:
        maintenant = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False

        # Gestion du timeout multimodal
        if etat_fusion["timestamp"] > 0:
            if maintenant - etat_fusion["timestamp"] > TIMEOUT_MS:
                print("[TIMEOUT] Fin de la fenêtre temporelle.")
                # Tente une exécution avec valeurs par défaut avant reset
                verifier_et_executer(force_exec=True)
                reinitialiser_fusion()

        dessiner_interface()
        pygame.display.flip()
        horloge.tick(30)
finally:
    IvyStop()
    pygame.quit()
    sys.exit()