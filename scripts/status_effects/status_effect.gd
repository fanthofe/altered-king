class_name StatusEffect
extends Resource
## Une altération d'état : la seule forme de "puissance" du roi déchu.
## Ajouter un sort = créer une nouvelle Resource, jamais modifier les ennemis.

@export var id: StringName = &"status"
@export var display_name: String = "Altération"
## Durée totale de l'effet, en secondes.
@export var duration: float = 5.0
## Intervalle entre deux ticks de dégâts. 0 = aucun tick.
@export var tick_interval: float = 0.0
@export var tick_damage: int = 0
## Empêche la cible de bouger et d'agir.
@export var immobilizes: bool = false
## Teinte appliquée à la cible pendant l'effet.
@export var tint: Color = Color.WHITE
## Immunité de la cible à cet effet après expiration (anti-spam).
@export var reapply_cooldown: float = 0.0
## Rayon de la zone d'effet autour du lanceur, en pixels.
@export var area_radius: float = 60.0
