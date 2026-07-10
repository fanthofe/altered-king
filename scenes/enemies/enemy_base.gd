class_name EnemyBase
extends CharacterBody2D
## Geôlier de base : patrouille, repère le joueur, le poursuit et frappe
## au contact. Meurt uniquement par altération (poison) ou l'environnement.

enum State { PATROL, CHASE, SEARCH, WAIT }

## Les geôliers traînent leur carcasse : jamais plus vite que le mage.
@export var patrol_speed: float = 28.0
@export var chase_speed: float = 58.0
@export var gravity: float = 900.0
@export var contact_damage: int = 1
@export var attack_cooldown: float = 1.0
## Temps passé à fouiller la dernière position connue avant d'abandonner.
@export var search_wait_time: float = 2.5

var state: State = State.PATROL
var dir: int = -1
var last_known_pos: Vector2

var _target: Node2D = null
var _attack_timer: float = 0.0
var _wait_timer: float = 0.0
var _base_modulate: Color

@onready var health: HealthComponent = $HealthComponent
@onready var status: StatusReceiverComponent = $StatusReceiverComponent
@onready var detection: DetectionComponent = $DetectionComponent
@onready var _sprite: AnimatedSprite2D = $Sprite
@onready var _hitbox: Area2D = $Hitbox
@onready var _floor_probe: RayCast2D = $FloorProbe
@onready var _probe_offset_x: float = _floor_probe.position.x

func _ready() -> void:
	add_to_group("enemies")
	_base_modulate = modulate
	health.died.connect(_die)
	status.status_applied.connect(func(_e: StatusEffect) -> void: _update_tint())
	status.status_expired.connect(func(_e: StatusEffect) -> void: _update_tint())
	detection.player_spotted.connect(_on_player_spotted)
	detection.player_lost.connect(_on_player_lost)
	_apply_facing()

func receive_status(effect: StatusEffect) -> void:
	status.apply(effect)

func _physics_process(delta: float) -> void:
	velocity.y += gravity * delta
	_attack_timer = maxf(_attack_timer - delta, 0.0)

	if status.is_immobilized():
		# Paralysé : cloué sur place, mais la gravité s'applique toujours.
		velocity.x = 0.0
		_sprite.play("idle")
		move_and_slide()
		return

	match state:
		State.PATROL:
			_state_patrol()
		State.CHASE:
			_state_chase()
		State.SEARCH:
			_state_search()
		State.WAIT:
			_state_wait(delta)

	move_and_slide()
	_sprite.play("walk" if absf(velocity.x) > 1.0 else "idle")
	_try_attack()

func _state_patrol() -> void:
	if _blocked_ahead():
		dir = -dir
		_apply_facing()
	velocity.x = dir * patrol_speed

func _state_chase() -> void:
	if _target == null:
		state = State.PATROL
		return
	last_known_pos = _target.global_position
	var to_target: float = signf(last_known_pos.x - global_position.x)
	if to_target != 0.0 and to_target != float(dir):
		dir = int(to_target)
		_apply_facing()
	# Ne se jette pas dans le vide : le baiter au bord d'un gouffre est voulu.
	velocity.x = 0.0 if _blocked_ahead() else dir * chase_speed

func _state_search() -> void:
	var to_pos: float = last_known_pos.x - global_position.x
	if absf(to_pos) < 6.0 or _blocked_ahead():
		velocity.x = 0.0
		_wait_timer = search_wait_time
		state = State.WAIT
		return
	var new_dir: int = 1 if to_pos > 0.0 else -1
	if new_dir != dir:
		dir = new_dir
		_apply_facing()
	velocity.x = dir * chase_speed

func _state_wait(delta: float) -> void:
	velocity.x = 0.0
	_wait_timer -= delta
	if _wait_timer <= 0.0:
		state = State.PATROL

func _try_attack() -> void:
	if _attack_timer > 0.0:
		return
	for body: Node2D in _hitbox.get_overlapping_bodies():
		if body.is_in_group("player") and not body.get("is_hidden"):
			body.take_damage(contact_damage, global_position)
			_attack_timer = attack_cooldown
			return

func _blocked_ahead() -> bool:
	return is_on_wall() or (is_on_floor() and not _floor_probe.is_colliding())

func _apply_facing() -> void:
	_floor_probe.position.x = _probe_offset_x * dir
	_sprite.flip_h = dir < 0
	detection.set_facing(dir)

func _on_player_spotted(player: Node2D) -> void:
	_target = player
	state = State.CHASE
	EventBus.player_spotted.emit(self)

func _on_player_lost() -> void:
	_target = null
	if state == State.CHASE:
		state = State.SEARCH

func _update_tint() -> void:
	# La paralysie prime visuellement sur le poison.
	if status.is_active(&"paralysis"):
		modulate = Color(0.55, 0.65, 1.0)
	elif status.is_active(&"poison"):
		modulate = Color(0.45, 0.85, 0.35)
	else:
		modulate = _base_modulate

func _die() -> void:
	EventBus.enemy_died.emit(self)
	queue_free()
