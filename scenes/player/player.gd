class_name Player
extends CharacterBody2D
## Le roi déchu, réincarné dans le corps d'un esclave.
## Aucune attaque directe : uniquement des sorts d'altération d'état.

enum State { MOVE, CAST, HIDDEN, HURT, DEAD }

signal health_changed(current: int, maximum: int)
signal mana_changed(current: float, maximum: float)
signal hidden_changed(is_hidden: bool)
signal cast_started(effect: StatusEffect)

## Rythme volontairement lent, façon Blasphemous.
@export var walk_speed: float = 75.0
@export var jump_velocity: float = -370.0
@export var gravity: float = 1100.0
@export var max_health: int = 4
@export var max_mana: float = 10.0
@export var mana_regen: float = 0.6
## Temps d'incantation immobile : fenêtre de vulnérabilité assumée.
@export var cast_time: float = 0.6
@export var poison_effect: StatusEffect
@export var paralysis_effect: StatusEffect
@export var poison_cost: float = 4.0
@export var paralysis_cost: float = 3.0
@export var invincibility_time: float = 1.0

var state: State = State.MOVE
var health: int
var mana: float
var facing: int = 1
var is_hidden: bool = false
## Buisson dont la zone recouvre actuellement le joueur (posé par bush.gd).
var current_bush: Area2D = null

var _cast_timer: float = 0.0
var _pending_effect: StatusEffect = null
var _pending_cost: float = 0.0
var _hurt_timer: float = 0.0
var _invincible_timer: float = 0.0

@onready var _sprite: AnimatedSprite2D = $Sprite
@onready var _spell_area: Area2D = $SpellArea
@onready var _spell_shape: CollisionShape2D = $SpellArea/CollisionShape2D
@onready var _aoe_indicator: SpellAoeIndicator = $SpellAoeIndicator

func _ready() -> void:
	add_to_group("player")
	health = max_health
	mana = max_mana
	health_changed.emit(health, max_health)
	mana_changed.emit(mana, max_mana)

func _physics_process(delta: float) -> void:
	if state != State.DEAD:
		mana = minf(mana + mana_regen * delta, max_mana)
		mana_changed.emit(mana, max_mana)
	_update_invincibility(delta)

	match state:
		State.MOVE:
			_state_move(delta)
		State.CAST:
			_state_cast(delta)
		State.HIDDEN:
			_state_hidden()
		State.HURT:
			_state_hurt(delta)
		State.DEAD:
			velocity.x = 0.0
			velocity.y += gravity * delta
			move_and_slide()

func _state_move(delta: float) -> void:
	var axis: float = Input.get_axis("move_left", "move_right")
	velocity.x = axis * walk_speed
	if absf(axis) > 0.01:
		facing = 1 if axis > 0.0 else -1

	if not is_on_floor():
		velocity.y += gravity * delta
	elif Input.is_action_just_pressed("jump"):
		velocity.y = jump_velocity

	move_and_slide()

	_sprite.flip_h = facing < 0
	if not is_on_floor():
		_sprite.play("jump")
	elif absf(velocity.x) > 1.0:
		_sprite.play("walk")
	else:
		_sprite.play("idle")

	if is_on_floor():
		if Input.is_action_just_pressed("cast_poison"):
			_try_start_cast(poison_effect, poison_cost)
		elif Input.is_action_just_pressed("cast_paralysis"):
			_try_start_cast(paralysis_effect, paralysis_cost)
		elif Input.is_action_just_pressed("interact") and current_bush != null:
			_enter_hidden()

func _state_cast(delta: float) -> void:
	# Incanter fige le roi : c'est le prix de la magie.
	velocity.x = 0.0
	velocity.y += gravity * delta
	move_and_slide()
	# Le périmètre du sort clignote pendant toute l'incantation.
	_aoe_indicator.visible = fmod(_cast_timer, 0.16) > 0.08
	_cast_timer -= delta
	if _cast_timer <= 0.0:
		_release_spell()
		state = State.MOVE

func _state_hidden() -> void:
	velocity = Vector2.ZERO
	if Input.is_action_just_pressed("interact") \
			or Input.is_action_just_pressed("jump"):
		_exit_hidden()

func _state_hurt(delta: float) -> void:
	# Recul subi, aucun contrôle pendant un court instant.
	velocity.y += gravity * delta
	velocity.x = move_toward(velocity.x, 0.0, 300.0 * delta)
	move_and_slide()
	_hurt_timer -= delta
	if _hurt_timer <= 0.0:
		state = State.MOVE

func _try_start_cast(effect: StatusEffect, cost: float) -> void:
	if effect == null or mana < cost:
		return
	_pending_effect = effect
	_pending_cost = cost
	_cast_timer = cast_time
	_spell_shape.shape.radius = effect.area_radius
	_aoe_indicator.setup(effect.area_radius, effect.tint)
	_aoe_indicator.visible = true
	_sprite.play("cast")
	state = State.CAST
	cast_started.emit(effect)

func _release_spell() -> void:
	mana -= _pending_cost
	mana_changed.emit(mana, max_mana)
	_aoe_indicator.flash()
	# Le sort prend effet sur tous les ennemis dans le périmètre.
	for body: Node2D in _spell_area.get_overlapping_bodies():
		if body.is_in_group("enemies") and body.has_method("receive_status"):
			body.receive_status(_pending_effect)
	_pending_effect = null

func _cancel_cast() -> void:
	# Interrompu avant la fin : aucun mana dépensé, aucun effet.
	_pending_effect = null
	_aoe_indicator.visible = false

func _enter_hidden() -> void:
	state = State.HIDDEN
	is_hidden = true
	velocity = Vector2.ZERO
	# On se glisse au centre du buisson, silhouette estompée.
	global_position.x = current_bush.global_position.x
	_sprite.modulate.a = 0.35
	_sprite.play("idle")
	hidden_changed.emit(true)

func _exit_hidden() -> void:
	state = State.MOVE
	is_hidden = false
	_sprite.modulate.a = 1.0
	hidden_changed.emit(false)

func take_damage(amount: int, source_position: Vector2) -> void:
	if state == State.DEAD or _invincible_timer > 0.0:
		return
	if state == State.HIDDEN:
		_exit_hidden()
	elif state == State.CAST:
		_cancel_cast()
	health = maxi(health - amount, 0)
	health_changed.emit(health, max_health)
	if health == 0:
		_die()
		return
	state = State.HURT
	_sprite.play("idle")
	_hurt_timer = 0.25
	_invincible_timer = invincibility_time
	var knock_dir: float = signf(global_position.x - source_position.x)
	if knock_dir == 0.0:
		knock_dir = -facing
	velocity = Vector2(knock_dir * 120.0, -90.0)

func _die() -> void:
	state = State.DEAD
	modulate = Color(0.7, 0.45, 0.45)
	_sprite.play("death")
	EventBus.player_died.emit()

func _update_invincibility(delta: float) -> void:
	if _invincible_timer <= 0.0:
		return
	_invincible_timer -= delta
	# Clignotement pendant l'invincibilité post-coup.
	var blink: bool = fmod(_invincible_timer, 0.2) > 0.1
	_sprite.visible = not blink or state == State.DEAD
	if _invincible_timer <= 0.0:
		_sprite.visible = true
