extends CanvasLayer
## HUD minimaliste : cœurs de vie, jauge de mana, état caché.

const HEART_SIZE := Vector2(10, 10)
const MANA_BAR_WIDTH := 80.0

var _player: Player = null

@onready var _hearts_box: HBoxContainer = $Margin/VBox/Hearts
@onready var _mana_fill: ColorRect = $Margin/VBox/ManaBar/Fill
@onready var _hidden_label: Label = $HiddenLabel

func _ready() -> void:
	_player = get_tree().get_first_node_in_group("player")
	if _player == null:
		return
	_player.health_changed.connect(_on_health_changed)
	_player.mana_changed.connect(_on_mana_changed)
	_player.hidden_changed.connect(_on_hidden_changed)
	_on_health_changed(_player.health, _player.max_health)
	_on_mana_changed(_player.mana, _player.max_mana)
	_hidden_label.visible = false

func _on_health_changed(current: int, maximum: int) -> void:
	while _hearts_box.get_child_count() < maximum:
		var heart := ColorRect.new()
		heart.custom_minimum_size = HEART_SIZE
		_hearts_box.add_child(heart)
	for i in _hearts_box.get_child_count():
		var heart: ColorRect = _hearts_box.get_child(i)
		heart.color = Color(0.75, 0.15, 0.2) if i < current \
			else Color(0.25, 0.1, 0.12)

func _on_mana_changed(current: float, maximum: float) -> void:
	_mana_fill.size.x = MANA_BAR_WIDTH * (current / maximum)

func _on_hidden_changed(is_hidden: bool) -> void:
	_hidden_label.visible = is_hidden
