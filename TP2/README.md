# Travaux Pratiques IHM - SRI

Ce dépôt regroupe les projets réalisés lors des séances de Travaux Pratiques d'Interaction Homme-Machine (IHM). Le dépôt sera mis à jour au fur et à mesure de l'avancée du module.

## Contenu du dépôt

### TP2 : Moteur de Reconnaissance de Gestes ($N Multistroke)
Implémentation d'un moteur de reconnaissance de gestes 2D basé sur l'algorithme $N. Il permet d'apprendre et de reconnaître des symboles dessinés à la souris, même s'ils sont composés de plusieurs traits continus, et de diffuser les résultats sur un réseau local via le bus Ivy.

**Structure du TP :**
* `ndollar.py` : Le cœur algorithmique et mathématique (génération des permutations, calculs des distances). Totalement indépendant de l'interface graphique.
* `NDollarIvy.py` : L'interface visuelle gérée avec Pygame, la capture des événements souris, et la communication réseau (Ivy).
* `gestures.pickle` : Le fichier de sauvegarde (généré automatiquement) contenant la base de données des gestes appris.

## Utilisation (TP2)

Assurez-vous d'avoir installé les dépendances requises (`pygame`, `ivy-python`). 
Lancez l'interface avec la commande :

    python NDollarIvy.py

**Commandes dans l'application :**
1. Dessinez un geste dans la fenêtre (maintenez le clic gauche).
2. Touche **A** : Apprendre le geste. Le programme mettra l'interface en pause pour vous demander de taper le nom du geste dans votre terminal.
3. Touche **Espace** : Reconnaître le geste. Le système affichera le nom du geste reconnu et son score de confiance. Si le score est suffisant, un message est diffusé sur le bus Ivy.
4. Touche **Échap** : Quitter proprement l'application.

*Astuce d'apprentissage : Apprenez un même geste 3 ou 4 fois avec de légères variations naturelles pour améliorer la robustesse de la reconnaissance.*

---
*D'autres TPs seront ajoutés prochainement dans leurs dossiers respectifs.*