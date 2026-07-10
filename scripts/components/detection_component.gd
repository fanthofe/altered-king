class_name DetectionComponent
extends Area2D
## Zone de vision d'un ennemi. Ignore le joueur quand il est caché :
## la furtivité est une mécanique centrale du jeu.

signal player_spotted(player: Node2D)
signal player_lost

var _player_in_range: Node2D = null
var _sees_player: bool = false
var _shape_offset_x: float

@onready var _shape: CollisionShape2D = $CollisionShape2D

func _ready() -> void:
	_shape_offset_x = _shape.position.x
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)

## Oriente le cône de vision dans la direction de marche (-1 ou 1).
func set_facing(dir: int) -> void:
	_shape.position.x = _shape_offset_x * dir

func _physics_process(_delta: float) -> void:
	var visible_now: bool = _player_in_range != null \
		and not _player_in_range.get("is_hidden")
	if visible_now and not _sees_player:
		_sees_player = true
		player_spotted.emit(_player_in_range)
	elif not visible_now and _sees_player:
		_sees_player = false
		player_lost.emit()

func _on_body_entered(body: Node2D) -> void:
	if body.is_in_group("player"):
		_player_in_range = body

func _on_body_exited(body: Node2D) -> void:
	if body == _player_in_range:
		_player_in_range = null
