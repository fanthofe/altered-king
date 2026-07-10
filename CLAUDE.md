# CLAUDE.md

Ce fichier guide Claude Code lors du travail sur ce projet.

## Le projet

**Altered King** — un platformer 2D pixel art sous Godot 4, au rythme lent et pesant inspiré de **Blasphemous** : déplacements délibérés, animations avec du poids, pas de course rapide ni de dash spammable.

### Pitch

Un roi déchu se réincarne dans le corps d'un esclave au fond d'un donjon. Il n'a **aucune capacité d'attaque directe** — uniquement des sorts d'**altération d'état**. Il doit progresser par la ruse : empoisonner, paralyser, se cacher, et laisser les ennemis mourir ou s'entretuer.

### Piliers de design (ne jamais dévier)

1. **Pas d'attaque directe.** Le joueur ne peut jamais infliger de dégâts bruts. Toute létalité passe par les altérations d'état ou l'environnement. Ne jamais ajouter d'épée, de projectile de dégâts, etc.
2. **Rythme lent.** Vitesse de marche basse, saut lourd, animations avec anticipation et récupération. Le joueur doit *planifier*, pas réagir.
3. **Difficulté élevée.** Les zones sont **infestées de monstres**. Peu de points de soin, dégâts ennemis importants, checkpoints espacés. La mort est fréquente et attendue.
4. **La furtivité est une mécanique centrale**, pas une option.

## Mécaniques de jeu

### Sorts de départ

- **Poison** : dégâts sur la durée (DoT). Seule source de dégâts du joueur en début de partie.
- **Paralysie** : immobilise un ennemi quelques secondes. N'inflige aucun dégât. Sert à fuir, passer, ou combiner (paralyser près d'un piège, d'un autre ennemi agressif, etc.).

**Les sorts sont des zones d'effet, jamais des projectiles.** À l'incantation, la délimitation du périmètre clignote autour du roi (contour de la teinte du sort) ; à la fin du temps d'incantation, tous les ennemis dans le périmètre subissent l'altération. Le roi est immobile pendant l'incantation (fenêtre de vulnérabilité) et doit donc s'approcher au contact du danger pour agir. Le rayon (`area_radius`) est une propriété de chaque `StatusEffect`.

Les sorts futurs restent des altérations : confusion (les ennemis s'attaquent entre eux), sommeil, ralentissement, etc.

### Furtivité

- Le joueur peut **se cacher dans des buissons** (et plus tard d'autres cachettes : tonneaux, alcôves).
- Caché, il est indétectable par les ennemis (sauf si vu en train d'entrer, ou détection spéciale de certains ennemis).
- Boucle de jeu type : empoisonner → se cacher dans un buisson → attendre que le DoT tue l'ennemi → avancer.
- Les ennemis ont des états de détection : patrouille → suspicion → poursuite → recherche → retour patrouille.

### Combat / survie

- Le joueur a peu de PV, une jauge de mana pour les sorts.
- Le mana se régénère lentement (ou via des ressources rares — à décider en jouant).
- Les ennemis sont nombreux, souvent en groupes. Foncer dans le tas = mort quasi garantie.

## Stack technique

- **Moteur** : Godot 4.x (GDScript).
- **Rendu** : pixel art. Dans `project.godot` : `rendering/textures/canvas_textures/default_texture_filter = 0` (Nearest), résolution de base basse (ex. 640×360) avec upscale entier, `stretch mode = viewport`.
- **Physique** : `CharacterBody2D` pour le joueur et les ennemis, `move_and_slide()`. Gravité forte pour un saut lourd.

## Structure du projet

```
project.godot
scenes/
  player/          # player.tscn + player.gd (machine à états)
  enemies/         # une sous-scène par type d'ennemi, base commune enemy_base
  spells/          # effets d'altération (poison, paralysie…)
  props/           # buissons/cachettes, pièges, portes
  levels/          # une scène par salle/zone du donjon
  ui/              # HUD (PV, mana, sorts), menus
scripts/
  autoload/        # singletons : game_manager, event_bus, save_manager
  components/      # nœuds réutilisables : health, status_receiver, detection
assets/
  sprites/         # pixel art, un dossier par entité
  sprites/references/  # images d'inspiration (scene.jpg : DA des extérieurs forestiers)
  audio/
  fonts/
```

## Conventions de code

- **GDScript** avec typage statique partout (`var speed: float = 40.0`, `func take_status(effect: StatusEffect) -> void`).
- Fichiers et dossiers en `snake_case`, nœuds/classes en `PascalCase`, signaux au passé (`died`, `status_applied`, `player_spotted`).
- **Machines à états** explicites (enum ou nœuds State) pour le joueur et les ennemis — pas de forêt de booléens.
- **Composition par composants** : `HealthComponent`, `StatusReceiverComponent` (gère poison/paralysie/etc.), `DetectionComponent` (cônes de vision, gestion des cachettes). Tout ennemi les réutilise.
- Les altérations d'état sont des **Resources** (`StatusEffect` de base, `PoisonEffect`, `ParalysisEffect` en héritent) : durée, tick, stackable ou non. Ajouter un sort = ajouter une Resource, pas modifier les ennemis.
- Communication découplée via un autoload `EventBus` (signaux globaux : mort d'ennemi, alerte, checkpoint).
- Toutes les valeurs d'équilibrage (vitesse, PV, dégâts du poison, durées) en `@export` pour itérer dans l'éditeur.

## Équilibrage — points de repère initiaux

À ajuster en testant, mais partir de :

- Vitesse de marche joueur : lente (75 px/s pour un gabarit de 14×40 ; gravité 1100, saut -370 ≈ 60 px de détente).
- Vitesse des ennemis : lente aussi, c'est tout le rythme du jeu (28 px/s en patrouille, 58 px/s en poursuite — toujours sous la vitesse du joueur, la menace vient du nombre, pas de la vitesse).
- Rayons des sorts : poison 70 px, paralysie 88 px (propriété `area_radius` des `.tres`).
- Poison : tue un ennemi de base en ~8-10 s. L'attente fait partie du gameplay.
- Paralysie : ~3-4 s, avec cooldown supérieur à sa durée (impossible de paralyser en boucle un même ennemi).
- Joueur : 3-5 points de vie. Un ennemi de base inflige 1 dégât.

## Direction artistique

- Les visuels du joueur et des extérieurs viennent du pack **GandalfHardcore** (`assets/sprites/references/Gandalf/`, licence : usage en jeu autorisé, redistribution interdite). `tools/build_gandalf_assets.py` compose et découpe tout vers `assets/sprites/gandalf/` — ne jamais référencer directement le dossier references/ dans les scènes.
- **Le héros est un mage en robe marron** (chemise/pantalon du pack recolorés par rampe de luminance) : ~17×44 px à l'écran, animations idle (5), walk (4), jump (1), cast (3, bras levé), death (10, finit au sol).
- Scène type forêt : ciel + nuages + 4 couches de pins (bg_pines_4 → 1, du plus clair au plus sombre), grands feuillus (tree_1/2), sol herbeux (`floor.png`, bord solide à y=6 de la texture), plateformes herbeuses (`platform.png`), cachettes = grands roseaux (`hide_grass.png`), buissons/rochers/touffes en décor.
- Les geôliers (pixel art maison `tools/gen_sprites.py`) sont affichés à l'échelle ×2 pour correspondre au gabarit du mage.
- Les niveaux utilisent le script générique `scenes/levels/room.gd` (limites caméra, purge, capture debug).

## Commandes utiles

```bash
# Lancer le jeu (adapter le chemin du binaire Godot si besoin)
godot --path . 

# Lancer une scène précise
godot --path . scenes/levels/dungeon_cell_01.tscn

# Mode headless pour vérifier que les scripts se chargent sans erreur
godot --path . --headless --quit
```

## Rappels pour Claude

- Toujours répondre et commenter le code **en français**.
- Ne jamais proposer de mécanique qui contredit les piliers (attaque directe, gameplay rapide, facilité).
- Privilégier de petites scènes testables individuellement plutôt qu'un niveau monolithique.
- Les sprites pixel art sont générés par `tools/gen_sprites.py` (grilles de caractères → PNG dans `assets/sprites/`). Pour modifier un sprite : éditer le script, relancer `python3 tools/gen_sprites.py`, puis `godot --headless --import`.
- Pour vérifier le rendu sans jouer : `AK_SCREENSHOT=/chemin/capture.png godot --path .` prend une capture après 1 s et quitte.
