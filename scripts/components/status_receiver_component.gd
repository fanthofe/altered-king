class_name StatusReceiverComponent
extends Node
## Reçoit et fait vivre les altérations d'état (poison, paralysie, …).
## Attend un nœud frère "HealthComponent" pour appliquer les ticks de dégâts.

signal status_applied(effect: StatusEffect)
signal status_expired(effect: StatusEffect)

## id -> { "effect": StatusEffect, "time_left": float, "tick": float }
var _active: Dictionary = {}
## id -> temps d'immunité restant
var _immunities: Dictionary = {}

@onready var _health: HealthComponent = get_parent().get_node("HealthComponent")

func apply(effect: StatusEffect) -> bool:
	if _immunities.has(effect.id):
		return false
	if _active.has(effect.id):
		# Réapplication : on rafraîchit simplement la durée.
		_active[effect.id]["time_left"] = effect.duration
		return true
	_active[effect.id] = {
		"effect": effect,
		"time_left": effect.duration,
		"tick": effect.tick_interval,
	}
	status_applied.emit(effect)
	return true

func is_active(id: StringName) -> bool:
	return _active.has(id)

func is_immobilized() -> bool:
	for entry: Dictionary in _active.values():
		if entry["effect"].immobilizes:
			return true
	return false

func _physics_process(delta: float) -> void:
	for id: StringName in _immunities.keys():
		_immunities[id] -= delta
		if _immunities[id] <= 0.0:
			_immunities.erase(id)

	for id: StringName in _active.keys():
		var entry: Dictionary = _active[id]
		var effect: StatusEffect = entry["effect"]
		entry["time_left"] -= delta

		if effect.tick_interval > 0.0:
			entry["tick"] -= delta
			if entry["tick"] <= 0.0:
				entry["tick"] += effect.tick_interval
				_health.take_damage(effect.tick_damage)

		if entry["time_left"] <= 0.0:
			_active.erase(id)
			if effect.reapply_cooldown > 0.0:
				_immunities[id] = effect.reapply_cooldown
			status_expired.emit(effect)
