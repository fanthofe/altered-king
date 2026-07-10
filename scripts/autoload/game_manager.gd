extends Node
## Gestion globale : mort du joueur, rechargement de la salle.

@export var respawn_delay: float = 1.4

func _ready() -> void:
	EventBus.player_died.connect(_on_player_died)

func _on_player_died() -> void:
	await get_tree().create_timer(respawn_delay).timeout
	get_tree().reload_current_scene()
