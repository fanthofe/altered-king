class_name Bush
extends Area2D
## Cachette : le joueur qui s'y glisse devient invisible aux ennemis.

func _ready() -> void:
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)

func _on_body_entered(body: Node2D) -> void:
	if body.is_in_group("player"):
		body.current_bush = self

func _on_body_exited(body: Node2D) -> void:
	if body.is_in_group("player") and body.current_bush == self:
		body.current_bush = null
