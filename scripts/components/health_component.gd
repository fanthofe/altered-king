class_name HealthComponent
extends Node
## Points de vie génériques, réutilisés par le joueur et tous les ennemis.

signal damaged(amount: int)
signal died

@export var max_health: int = 8

var health: int

func _ready() -> void:
	health = max_health

func take_damage(amount: int) -> void:
	if health <= 0:
		return
	health = maxi(health - amount, 0)
	damaged.emit(amount)
	if health == 0:
		died.emit()
