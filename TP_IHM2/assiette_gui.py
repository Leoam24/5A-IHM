import sys
import re
import pygame
from ivy.std_api import IvyInit, IvyStart, IvyStop, IvyBindMsg, IvySendMsg

# --- Configuration graphique ---
LARGEUR, HAUTEUR = 600, 500
BLANC = (255, 255, 255)
NOIR = (30, 30, 30)
GRIS_CLAIR = (220, 220, 220)
BLEU = (70, 130, 180)
ORANGE = (230, 120, 34)

POSITIONS = {
    "GAUCHE": (100, 120),
    "DROITE": (500, 120),

    "HAUT": (300, 180),
    "BAS_GAUCHE": (200, 340),
    "BAS_DROITE": (400, 340),
    "BAS": (300, 340),        
    "CENTRE": (300, 260)       
}

commande = {
    'BOISSON': [],  
    'DESSERT': []
}

etat_courant = "ATTENTE_ORDRE"
en_attente_item = None
en_attente_type = None

def parler(texte):
    IvySendMsg(f"ppilot5 Say={texte}")

def commander(agent, *args):
    global etat_courant, en_attente_item, en_attente_type

    brut = args[0]
    print(f"\n[Ivy] Message brut reçu : {brut}")

    conf_match = re.search(r"Confidence=([\d,\.]+)", brut)
    confiance = float(conf_match.group(1).replace(",", ".")) if conf_match else 0.0
    if confiance < 0.60:
        print("Confiance trop basse, ordre ignoré.")
        return

    # Extraction des balises
    action_match = re.search(r"action=(\w+)", brut)
    type_match   = re.search(r"type=(\w+)", brut)
    item_match   = re.search(r"item=(\w+)", brut)
    pos_match    = re.search(r"pos=(\w+)", brut)

    action = action_match.group(1) if action_match else None
    type_alim = type_match.group(1) if type_match else None
    item = item_match.group(1) if item_match else None
    pos = pos_match.group(1) if pos_match else None

    print(f"Action: {action} | Type: {type_alim} | Objet: {item} | Position: {pos}")

    if etat_courant == "ATTENTE_POSITION":
        if pos:
            valider_ajout(en_attente_type, en_attente_item, pos)
            # Réinitialisation de l'état
            etat_courant = "ATTENTE_ORDRE"
            en_attente_item = None
            en_attente_type = None
        else:
            parler("Veuillez préciser une position, par exemple à gauche ou en haut.")
        return

    # CAS B : État normal 
    if action == "AJOUTER" and item:
        if type_alim == "BOISSON" and len(commande['BOISSON']) >= 2:
            parler("Impossible, vous avez déjà deux boissons.")
            return
        if type_alim == "DESSERT" and len(commande['DESSERT']) >= 3:
            parler("Impossible, vous avez déjà trois desserts.")
            return

        if pos is None:
            etat_courant = "ATTENTE_POSITION"
            en_attente_item = item
            en_attente_type = type_alim
            parler(f"Où voulez-vous placer {item} ?")
        else:
            valider_ajout(type_alim, item, pos)

    elif action == "RETIRER" and item:
        retirer_aliment(item)

def valider_ajout(type_alim, item, pos):
    """Vérifie si la place est libre avant d'ajouter."""
    # Vérification d'occupation du slot
    for cat in ['BOISSON', 'DESSERT']:
        for el in commande[cat]:
            if el["position"] == pos:
                parler(f"La position {pos} est déjà occupée par {el['nom']}.")
                return

    element = {"nom": item, "position": pos}
    commande[type_alim].append(element)
    print(f"[PLATEAU ACTUEL] {commande}")
    parler(f"{item} ajouté en position {pos}.")

def retirer_aliment(item):
    """Supprime un aliment du plateau."""
    trouve = False
    for categorie in ['BOISSON', 'DESSERT']:
        for el in list(commande[categorie]):
            if el["nom"] == item:
                commande[categorie].remove(el)
                trouve = True
                parler(f"{item} a été retiré.")
                break
    if not trouve:
        parler(f"Il n'y a pas de {item} sur votre plateau.")

# --- Initialisation Ivy ---
IvyInit("AssietteGUI", "GUI prete", 0)
IvyStart("127.255.255.255:2010")
IvyBindMsg(commander, "^sra5 Parsed=(.*)")

# --- Initialisation Pygame ---
pygame.init()
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Assiette Gourmande - Retour Visuel")
police = pygame.font.SysFont("Arial", 16, bold=True)
horloge = pygame.time.Clock()

def dessiner_plateau():
    fenetre.fill(BLANC)

    pygame.draw.circle(fenetre, GRIS_CLAIR, (300, 280), 170)
    
    pygame.draw.polygon(fenetre, (200, 200, 200), [(300, 180), (200, 340), (400, 340)], 2)

    for nom_pos, coord in POSITIONS.items():
        if nom_pos in ["GAUCHE", "DROITE", "HAUT", "BAS_GAUCHE", "BAS_DROITE"]:
            pygame.draw.circle(fenetre, (180, 180, 180), coord, 35, 1)

    for boisson in commande['BOISSON']:
        coord = POSITIONS.get(boisson["position"], (100, 120))
        pygame.draw.circle(fenetre, BLEU, coord, 32)
        txt = police.render(boisson["nom"][:6], True, BLANC)
        fenetre.blit(txt, txt.get_rect(center=coord))

    for dessert in commande['DESSERT']:
        coord = POSITIONS.get(dessert["position"], (300, 180))
        pygame.draw.circle(fenetre, ORANGE, coord, 32)
        txt = police.render(dessert["nom"][:6], True, BLANC)
        fenetre.blit(txt, txt.get_rect(center=coord))

    info_txt = police.render(
        f"Boissons: {len(commande['BOISSON'])}/2  |  Desserts: {len(commande['DESSERT'])}/3", 
        True, NOIR
    )
    fenetre.blit(info_txt, (20, 20))

# --- Boucle principale ---
try:
    en_cours = True
    while en_cours:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False

        dessiner_plateau()
        pygame.display.flip()
        horloge.tick(30)
finally:
    IvyStop()
    pygame.quit()
    sys.exit()