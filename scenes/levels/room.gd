class_name Room
extends Node2D
## Salle générique : limites de caméra, détection de purge, capture debug.
## Boucle attendue partout : empoisonner -> se cacher -> attendre -> avancer.

@export var room_width: int = 1152
@export var room_height: int = 360

@onready var _camera: Camera2D = $Player/Camera2D
@onready var _purged_label: Label = $HUD/PurgedLabel

func _ready() -> void:
	_camera.limit_left = 0
	_camera.limit_top = 0
	_camera.limit_right = room_width
	_camera.limit_bottom = room_height
	EventBus.enemy_died.connect(_on_enemy_died)
	if OS.get_environment("AK_SCREENSHOT") != "":
		_take_debug_screenshot(OS.get_environment("AK_SCREENSHOT"))

func _on_enemy_died(_enemy: Node2D) -> void:
	# On attend une frame que l'ennemi mort quitte l'arbre de scène.
	await get_tree().process_frame
	if get_tree().get_nodes_in_group("enemies").is_empty():
		_purged_label.visible = true

func _take_debug_screenshot(path: String) -> void:
	await get_tree().create_timer(1.0).timeout
	get_viewport().get_texture().get_image().save_png(path)
	get_tree().quit()
