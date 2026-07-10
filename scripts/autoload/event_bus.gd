extends Node
## Bus de signaux globaux pour découpler les systèmes.

signal player_died
signal enemy_died(enemy: Node2D)
signal player_spotted(by_enemy: Node2D)
