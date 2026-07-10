# Altered King

Platformer 2D pixel art sous Godot 4, au rythme lent et pesant inspiré de **Blasphemous**.

## Pitch

Un roi déchu se réincarne dans le corps d'un esclave au fond d'un donjon. Il n'a **aucune capacité d'attaque directe** — uniquement des sorts d'**altération d'état**. Il doit progresser par la ruse : empoisonner, paralyser, se cacher, et laisser les ennemis mourir ou s'entretuer.

Les lieux sont infestés de monstres et le jeu est pensé pour être difficile : la mort est fréquente et attendue.

## Mécaniques principales

- **Aucune attaque directe.** Toute létalité passe par les altérations d'état ou l'environnement.
- **Sorts de zone.** Poison et paralysie sont des sorts d'altération d'état lancés en zone d'effet autour du personnage : le périmètre clignote pendant l'incantation (fenêtre de vulnérabilité), puis tous les ennemis dans la zone subissent l'effet.
  - **Poison** : dégâts sur la durée. Seule source de dégâts en début de partie.
  - **Paralysie** : immobilise un ennemi quelques secondes, sans dégâts.
- **Furtivité.** Le joueur peut se cacher dans des cachettes (buissons/roseaux) pour devenir indétectable le temps qu'un ennemi empoisonné meure.
- **Rythme lent.** Déplacement et animations pesants façon Blasphemous — le joueur doit planifier, pas réagir.

## Contrôles

| Action | Touche |
|---|---|
| Se déplacer | Q / D ou flèches |
| Sauter | Espace |
| Sort de poison | X |
| Sort de paralysie | C |
| Entrer / sortir d'une cachette | E (ou flèche bas) |

## Lancer le jeu

Nécessite [Godot 4.x](https://godotengine.org/download).

```bash
godot --path .
```

Pour ouvrir l'éditeur :

```bash
godot -e --path .
```

## Structure du projet

```
project.godot
scenes/
  player/          # le mage : machine à états, animations, sorts
  enemies/         # ennemis (patrouille, poursuite, altérations)
  spells/          # indicateur de zone d'effet des sorts
  props/           # cachettes (buissons/roseaux), décor
  levels/          # scènes de niveau
  ui/              # HUD (PV, mana, sorts)
scripts/
  autoload/        # singletons : EventBus, GameManager
  components/      # composants réutilisables : santé, altérations, détection
  status_effects/  # définitions des sorts (poison.tres, paralysis.tres)
assets/
  sprites/         # pixel art (généré ou dérivé d'assets de référence)
tools/
  gen_sprites.py            # génère les sprites pixel art maison (PNG)
  build_gandalf_assets.py   # compose/découpe les assets issus du pack GandalfHardcore
```

## Outils de développement

- `python3 tools/gen_sprites.py` régénère les sprites pixel art maison (personnage, ennemis, tuiles) décrits sous forme de grilles de caractères dans le script.
- `python3 tools/build_gandalf_assets.py` recompose les assets dérivés du pack GandalfHardcore (`assets/sprites/references/`) : recoloration du personnage, découpe des tuiles de décor.
- `AK_SCREENSHOT=/chemin/capture.png godot --path .` lance le jeu, prend une capture d'écran après 1 seconde et quitte — utile pour vérifier un rendu sans jouer manuellement.
- `godot --headless --import` puis `godot --headless --quit-after 300` permet de vérifier que le projet se charge et s'exécute sans erreur, sans interface graphique.

Voir [CLAUDE.md](CLAUDE.md) pour les conventions de code et les piliers de design détaillés.

## Licences des assets

Certains assets sont dérivés du pack **GandalfHardcore** (`assets/sprites/references/Gandalf/`). Sa licence autorise l'usage dans des jeux commerciaux et non commerciaux, modifiés selon les besoins, mais interdit la revente, le repackaging ou la redistribution des assets bruts.
