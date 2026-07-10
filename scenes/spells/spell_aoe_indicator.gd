class_name SpellAoeIndicator
extends Node2D
## Délimitation visuelle du périmètre d'un sort : contour qui clignote
## pendant l'incantation, puis flash de remplissage à la libération.

var radius: float = 60.0
var color: Color = Color.WHITE

var _fill_alpha: float = 0.0

func setup(new_radius: float, new_color: Color) -> void:
	radius = new_radius
	color = new_color
	_fill_alpha = 0.0
	queue_redraw()

func flash() -> void:
	visible = true
	var tween := create_tween()
	tween.tween_method(_set_fill_alpha, 0.45, 0.0, 0.35)
	tween.tween_callback(func() -> void: visible = false)

func _set_fill_alpha(alpha: float) -> void:
	_fill_alpha = alpha
	queue_redraw()

func _draw() -> void:
	if _fill_alpha > 0.0:
		draw_circle(Vector2.ZERO, radius, Color(color, _fill_alpha))
	draw_arc(Vector2.ZERO, radius, 0.0, TAU, 48, color, 1.0)
