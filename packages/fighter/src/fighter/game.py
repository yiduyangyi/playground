"""
Fighter Plane Battle Game — Enhanced Edition
Visuals: parallax starfield, particle explosions, floating damage, screen shake,
         combo counter, icon-based HUD.
Gameplay: varied enemy movement patterns, boss phases with bullet patterns,
         weapon pickups, formation switching.
"""

import math
import random
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Optional

import pygame

# ── Init ──────────────────────────────────────────────────────────────────
pygame.init()

_font_cache = {}

def get_font(size: int) -> pygame.font.Font:
    if size in _font_cache:
        return _font_cache[size]
    font_names = ["Arial", "Helvetica", "Times New Roman", "Courier New"]
    font = pygame.font.SysFont(font_names, size)
    _font_cache[size] = font
    return font

# ── Constants ─────────────────────────────────────────────────────────────
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GAME_DURATION = 120  # seconds
PLAYER_Y = SCREEN_HEIGHT - 80

# Colors
BLACK       = (0, 0, 0)
WHITE       = (255, 255, 255)
RED         = (255, 0, 0)
GREEN       = (0, 255, 0)
BLUE        = (0, 0, 255)
YELLOW      = (255, 255, 0)
CYAN        = (0, 255, 255)
MAGENTA     = (255, 0, 255)
ORANGE      = (255, 165, 0)
PURPLE      = (128, 0, 128)
PINK        = (255, 192, 203)
LIME        = (50, 205, 50)
GOLD        = (255, 215, 0)
DARK_BG     = (8, 8, 24)

# ── Enums ─────────────────────────────────────────────────────────────────
class Difficulty(Enum):
    EASY = 1; MEDIUM = 2; HARD = 3; EXTREME = 4

class PowerUpType(Enum):
    POWER_BOOST = 1   # 攻击力提升
    HEALTH      = 2   # 生命恢复
    RAPID_FIRE  = 3   # 射速提升
    SHIELD      = 4   # 防护盾
    MULTI_SHOT  = 5   # 多发子弹
    BOMB        = 6   # 全屏炸弹（新）

class MovementPattern(Enum):
    LINEAR   = 1   # 直线下落
    SINE     = 2   # 正弦波
    ZIGZAG   = 3   # 折线
    HOMING   = 4   # 向玩家靠近
    CIRCLE   = 5   # 螺旋下落

class Formation(Enum):
    V_SHAPE     = 1  # V 型（前突）
    HORIZONTAL  = 2  # 一字横排
    VERTICAL    = 3  # 纵队

# ── Config ────────────────────────────────────────────────────────────────
@dataclass
class GameConfig:
    difficulty: Difficulty
    enemy_spawn_rate: float
    enemy_speed: float
    enemy_hp: int
    player_bullet_speed: float
    enemy_bullet_speed: float

    @classmethod
    def from_difficulty(cls, difficulty: Difficulty):
        if difficulty == Difficulty.EASY:
            return cls(difficulty, 3.5, 1.0, 1, 10, 3)
        elif difficulty == Difficulty.MEDIUM:
            return cls(difficulty, 2.0, 1.8, 1, 9, 4)
        elif difficulty == Difficulty.HARD:
            return cls(difficulty, 1.2, 2.5, 1, 9, 5)
        else:
            return cls(difficulty, 0.8, 3.5, 2, 8, 6)

# ── StarField ─────────────────────────────────────────────────────────────
class Star:
    def __init__(self, x: float, y: float, speed: float, size: int, brightness: int):
        self.x = x; self.y = y; self.speed = speed; self.size = size
        self.brightness = brightness
        self.twinkle = random.random() * math.pi * 2

    def update(self):
        self.y += self.speed
        self.twinkle += 0.05
        if self.y > SCREEN_HEIGHT:
            self.y = -5
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, screen):
        alpha = 0.5 + 0.5 * math.sin(self.twinkle)
        color = tuple(min(255, int(self.brightness * alpha)) for _ in range(3))
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)

class StarField:
    def __init__(self):
        self.layers = []
        # 3 layers: far (small, slow), mid, near (fewer, bigger, fast)
        configs = [
            (120, 0.3, 1, 100),   # far: many tiny slow dim stars
            (60, 0.8, 2, 160),    # mid
            (20, 1.8, 3, 200),    # near: few big fast bright
        ]
        for count, speed, size, brightness in configs:
            stars = []
            for _ in range(count):
                s = Star(
                    random.randint(0, SCREEN_WIDTH),
                    random.randint(0, SCREEN_HEIGHT),
                    speed + random.uniform(-0.2, 0.2),
                    random.randint(max(1, size - 1), size),
                    brightness + random.randint(-20, 20),
                )
                stars.append(s)
            self.layers.append(stars)

    def update(self):
        for layer in self.layers:
            for star in layer:
                star.update()

    def draw(self, screen):
        for layer in self.layers:
            for star in layer:
                star.draw(screen)

# ── Particle System ───────────────────────────────────────────────────────
class Particle:
    def __init__(self, x: float, y: float, vx: float, vy: float,
                 color: Tuple[int, int, int], life: int, size: int = 2):
        self.x = x; self.y = y; self.vx = vx; self.vy = vy
        self.color = color; self.life = life; self.max_life = life
        self.size = size

    def update(self) -> bool:
        """Returns True if still alive."""
        self.x += self.vx; self.y += self.vy
        self.vy += 0.05  # gravity
        self.life -= 1
        return self.life > 0

    def draw(self, screen):
        ratio = self.life / self.max_life
        alpha_color = tuple(max(0, min(255, int(c * ratio))) for c in self.color)
        size = max(1, int(self.size * ratio))
        pygame.draw.circle(screen, alpha_color, (int(self.x), int(self.y)), size)

class ParticleSystem:
    def __init__(self):
        self.particles: List[Particle] = []

    def emit(self, x: float, y: float, count: int,
             colors: List[Tuple[int, int, int]], speed: float = 4.0,
             life: int = 30):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            spd = random.uniform(speed * 0.3, speed)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            color = random.choice(colors)
            p = Particle(x, y, vx, vy, color, random.randint(life // 2, life),
                         random.randint(1, 4))
            self.particles.append(p)

    def emit_directed(self, x: float, y: float, count: int,
                      colors: List[Tuple[int, int, int]],
                      direction: float, spread: float,
                      speed: float = 4.0, life: int = 30):
        """direction in radians, spread in radians (half-angle)."""
        for _ in range(count):
            angle = direction + random.uniform(-spread, spread)
            spd = random.uniform(speed * 0.4, speed)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            color = random.choice(colors)
            p = Particle(x, y, vx, vy, color, random.randint(life // 2, life),
                         random.randint(1, 3))
            self.particles.append(p)

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)

# ── Floating Text ─────────────────────────────────────────────────────────
class FloatingText:
    def __init__(self, x: float, y: float, text: str, color: Tuple[int, int, int],
                 life: int = 40, size: int = 24, rise: float = -2.0):
        self.x = x; self.y = y; self.text = text; self.color = color
        self.life = life; self.max_life = life; self.rise = rise
        self.font = get_font(size)

    def update(self) -> bool:
        self.y += self.rise
        self.life -= 1
        return self.life > 0

    def draw(self, screen):
        ratio = self.life / self.max_life
        alpha = int(255 * ratio)
        surf = self.font.render(self.text, True, self.color)
        surf.set_alpha(alpha)
        rect = surf.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(surf, rect)

# ── Screen Shake ──────────────────────────────────────────────────────────
class ScreenShake:
    def __init__(self):
        self.intensity = 0
        self.duration = 0
        self.offset_x = 0
        self.offset_y = 0

    def trigger(self, intensity: int, duration: int):
        self.intensity = intensity
        self.duration = duration

    def update(self):
        if self.duration > 0:
            self.offset_x = random.randint(-self.intensity, self.intensity)
            self.offset_y = random.randint(-self.intensity, self.intensity)
            self.duration -= 1
        else:
            self.offset_x = 0
            self.offset_y = 0

    def apply(self, x: float, y: float) -> Tuple[float, float]:
        return x + self.offset_x, y + self.offset_y

# ── Bullet ────────────────────────────────────────────────────────────────
class Bullet:
    def __init__(self, x: float, y: float, speed: float, is_player: bool,
                 angle: float = -math.pi / 2, radius: int = 4, color=None):
        self.x = x; self.y = y; self.speed = speed
        self.is_player = is_player
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.radius = radius
        self.color = color or (YELLOW if is_player else RED)

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # glow
        glow = tuple(max(0, c // 2) for c in self.color)
        pygame.draw.circle(screen, glow, (int(self.x), int(self.y)), self.radius + 2, 1)

    def is_off_screen(self) -> bool:
        return (self.x < -20 or self.x > SCREEN_WIDTH + 20 or
                self.y < -20 or self.y > SCREEN_HEIGHT + 20)

# ── PowerUp ───────────────────────────────────────────────────────────────
class PowerUp:
    def __init__(self, x: float, y: float, powerup_type: PowerUpType):
        self.x = x; self.y = y
        self.type = powerup_type
        self.width = 30; self.height = 30
        self.speed = 2.0
        self.animation_time = 0

    def update(self):
        self.y += self.speed
        self.animation_time += 1

    def draw(self, screen):
        cx = int(self.x + self.width // 2)
        cy = int(self.y + self.height // 2)
        r = self.width // 2
        flash = (self.animation_time // 5) % 2 == 0

        if self.type == PowerUpType.POWER_BOOST:
            pygame.draw.circle(screen, GOLD, (cx, cy), r)
            pygame.draw.circle(screen, YELLOW, (cx, cy), r - 3)
            if flash:
                pygame.draw.circle(screen, ORANGE, (cx, cy), r - 6)
            pts = []
            for i in range(5):
                a = (i * 2 * math.pi / 5) - math.pi / 2
                pts.append((int(cx + r * 0.8 * math.cos(a)), int(cy + r * 0.8 * math.sin(a))))
                a2 = a + math.pi / 5
                pts.append((int(cx + r * 0.4 * math.cos(a2)), int(cy + r * 0.4 * math.sin(a2))))
            if len(pts) >= 3: pygame.draw.polygon(screen, WHITE, pts[:5])

        elif self.type == PowerUpType.HEALTH:
            pygame.draw.circle(screen, GREEN, (cx, cy), r)
            pygame.draw.circle(screen, LIME, (cx, cy), r - 3)
            s = r - 4
            pygame.draw.rect(screen, WHITE, (cx - s // 2, cy - s, s, s * 2))
            pygame.draw.rect(screen, WHITE, (cx - s, cy - s // 2, s * 2, s))

        elif self.type == PowerUpType.RAPID_FIRE:
            pygame.draw.circle(screen, RED, (cx, cy), r)
            pygame.draw.circle(screen, ORANGE, (cx, cy), r - 3)
            pts = [(cx - 5, cy - 8), (cx + 2, cy - 2), (cx - 2, cy),
                   (cx + 5, cy + 8), (cx - 2, cy + 4), (cx + 2, cy + 2), (cx - 5, cy - 8)]
            pygame.draw.polygon(screen, YELLOW, pts)

        elif self.type == PowerUpType.SHIELD:
            pygame.draw.circle(screen, BLUE, (cx, cy), r)
            pygame.draw.circle(screen, CYAN, (cx, cy), r - 3)
            pts = [(cx, cy - r + 2), (cx - r + 2, cy - 2), (cx - r + 2, cy + 4),
                   (cx, cy + r - 2), (cx + r - 2, cy + 4), (cx + r - 2, cy - 2)]
            pygame.draw.polygon(screen, WHITE, pts)

        elif self.type == PowerUpType.MULTI_SHOT:
            pygame.draw.circle(screen, PURPLE, (cx, cy), r)
            pygame.draw.circle(screen, MAGENTA, (cx, cy), r - 3)
            if flash:
                pygame.draw.circle(screen, PINK, (cx, cy), r - 6)
            for i in range(3):
                ox = int(cx + (i - 1) * 6)
                small = []
                for j in range(5):
                    a = (j * 2 * math.pi / 5) - math.pi / 2
                    small.append((int(ox + 4 * math.cos(a)), int(cy + 4 * math.sin(a))))
                if len(small) >= 3: pygame.draw.polygon(screen, WHITE, small[:5])

        elif self.type == PowerUpType.BOMB:
            # Bomb pickup — black circle with B
            pygame.draw.circle(screen, (80, 80, 80), (cx, cy), r)
            pygame.draw.circle(screen, (60, 60, 60), (cx, cy), r - 3)
            if flash:
                pygame.draw.circle(screen, (200, 50, 50), (cx, cy), r - 6)
            bomb_font = get_font(20)
            b_surf = bomb_font.render("B", True, RED)
            b_rect = b_surf.get_rect(center=(cx, cy))
            screen.blit(b_surf, b_rect)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def is_off_screen(self) -> bool:
        return self.y > SCREEN_HEIGHT

# ── Player ────────────────────────────────────────────────────────────────
class Player:
    def __init__(self, x: float):
        self.x = x; self.y = PLAYER_Y
        self.width = 50; self.height = 40
        self.speed = 7
        self.shoot_cooldown = 0
        self.shoot_delay = 15
        self.base_shoot_delay = 15
        self.hp = 3; self.max_hp = 3
        self.attack_power = 1
        self.rapid_fire_count = 0
        self.shield_count = 0
        self.multi_shot_count = 0
        self.bomb_count = 0        # bomb stock
        self.animation_frame = 0
        self.tilt = 0
        self.invincible = 0        # invincibility frames after hit
        self.weapon_type = "normal"  # normal / spread / laser / homing

    def update(self, keys):
        self.animation_frame += 1
        if self.invincible > 0:
            self.invincible -= 1

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
            self.tilt = max(self.tilt - 2, -8)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
            self.tilt = min(self.tilt + 2, 8)
        else:
            self.tilt += -1 if self.tilt > 0 else 1 if self.tilt < 0 else 0

        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def shoot(self, config: GameConfig) -> List[Bullet]:
        bullets = []
        if self.shoot_cooldown > 0:
            return bullets

        cd = self.shoot_delay
        if self.rapid_fire_count > 0:
            cd = max(5, self.base_shoot_delay - self.rapid_fire_count * 3)
        self.shoot_cooldown = cd

        cx = self.x + self.width // 2
        top_y = self.y

        if self.weapon_type == "normal":
            bullets.append(Bullet(cx, top_y, config.player_bullet_speed, True))
            if self.multi_shot_count > 0:
                for off in [-12, 12]:
                    bullets.append(Bullet(cx + off, top_y, config.player_bullet_speed, True))
            if self.multi_shot_count >= 2:
                for off in [-24, 24]:
                    bullets.append(Bullet(cx + off, top_y + 8,
                                          config.player_bullet_speed * 0.9, True))

        elif self.weapon_type == "spread":
            for angle_deg in [-30, -15, 0, 15, 30]:
                a = math.radians(angle_deg - 90)
                bullets.append(Bullet(cx, top_y, config.player_bullet_speed * 0.8,
                                      True, a, 3, CYAN))
        elif self.weapon_type == "laser":
            # Thick laser beam — handled as a special "bullet" with large rect
            b = Bullet(cx, top_y, config.player_bullet_speed * 1.3, True,
                       -math.pi / 2, 6, (100, 200, 255))
            b.vy = -config.player_bullet_speed * 1.3
            b.vx = 0
            b.radius = 6
            b.is_laser = True
            bullets.append(b)
        elif self.weapon_type == "homing":
            # Homing bullet — slower, tracking handled in update
            b = Bullet(cx, top_y, config.player_bullet_speed * 0.6, True,
                       -math.pi / 2, 5, MAGENTA)
            b.is_homing = True
            b.homing_strength = 0.08
            bullets.append(b)

        return bullets

    def draw(self, screen):
        # Invincibility blink
        if self.invincible > 0 and self.invincible % 4 < 2:
            return

        cx = self.x + self.width // 2
        cy = self.y + self.height // 2

        # Engine flame
        flame_intensity = 5 + int(3 * math.sin(self.animation_frame * 0.3))
        flame_y = self.y + self.height
        flame_colors = [(255, 200, 0), (255, 150, 0), (255, 100, 0)]
        for i, fc in enumerate(flame_colors):
            fh = (3 - i) * 4
            pts = [
                (cx - 8 + self.tilt * 0.5, flame_y),
                (cx - 5 + self.tilt * 0.3, flame_y + fh),
                (cx + 5 - self.tilt * 0.3, flame_y + fh),
                (cx + 8 - self.tilt * 0.5, flame_y),
            ]
            pygame.draw.polygon(screen, fc, pts)

        # Body
        body = [
            (cx + self.tilt * 0.3, self.y + 5),
            (self.x + 5, self.y + self.height - 8),
            (self.x + self.width - 5, self.y + self.height - 8),
        ]
        pygame.draw.polygon(screen, BLUE, body)
        darker_blue = (max(0, BLUE[0] - 30), max(0, BLUE[1] - 30), max(0, BLUE[2] - 10))
        body_bottom = [
            (self.x + 5, self.y + self.height - 8),
            (self.x + self.width - 5, self.y + self.height - 8),
            (cx + self.tilt * 0.3, self.y + self.height),
        ]
        pygame.draw.polygon(screen, darker_blue, body_bottom)

        # Wings
        wing_y = self.y + self.height // 2
        wc = (min(255, CYAN[0] + self.tilt * 2), CYAN[1], CYAN[2])
        pygame.draw.polygon(screen, wc, [
            (self.x, wing_y),
            (self.x - 12 - abs(self.tilt) * 0.5, wing_y + 8),
            (self.x - 8, wing_y + 12),
            (self.x, wing_y + 6),
        ])
        pygame.draw.polygon(screen, wc, [
            (self.x + self.width, wing_y),
            (self.x + self.width + 12 + abs(self.tilt) * 0.5, wing_y + 8),
            (self.x + self.width + 8, wing_y + 12),
            (self.x + self.width, wing_y + 6),
        ])

        # Cockpit
        cockpit_x = int(cx + self.tilt * 0.2)
        cockpit_y = self.y + 18
        pygame.draw.circle(screen, GOLD, (cockpit_x, cockpit_y), 9)
        pygame.draw.circle(screen, YELLOW, (cockpit_x, cockpit_y), 6)
        pygame.draw.circle(screen, WHITE, (cockpit_x - 2, cockpit_y - 2), 2)

        # Nose
        nose = [
            (cx + self.tilt * 0.3, self.y + 5),
            (cx + self.tilt * 0.5, self.y),
            (cx - self.tilt * 0.5, self.y),
        ]
        pygame.draw.polygon(screen, (100, 150, 255), nose)

        # Shield aura
        if self.shield_count > 0:
            shield_alpha = 60 + int(20 * math.sin(self.animation_frame * 0.1))
            shield_surf = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (*BLUE, shield_alpha),
                               (shield_surf.get_width() // 2, shield_surf.get_height() // 2),
                               self.width // 2 + 5, 2)
            screen.blit(shield_surf, (self.x - 10, self.y - 10))

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

# ── Enemy ─────────────────────────────────────────────────────────────────
class EnemyType(Enum):
    FAST = 1; STRONG = 2; BOSS = 3

class Enemy:
    def __init__(self, x: float, enemy_type: EnemyType, config: GameConfig):
        self.x = x; self.y = -50
        self.type = enemy_type; self.config = config
        self.movement = MovementPattern.LINEAR
        self.spawn_time = 0.0

        if enemy_type == EnemyType.FAST:
            self.width = 40; self.height = 35
            self.speed = config.enemy_speed * 1.5
            self.color = RED; self.accent_color = PINK
            self.hp = config.enemy_hp
            self.movement = random.choice([MovementPattern.LINEAR, MovementPattern.SINE,
                                            MovementPattern.ZIGZAG])
        elif enemy_type == EnemyType.STRONG:
            self.width = 50; self.height = 45
            self.speed = config.enemy_speed * 0.8
            self.color = ORANGE; self.accent_color = YELLOW
            self.hp = config.enemy_hp + 1
            self.movement = random.choice([MovementPattern.LINEAR, MovementPattern.SINE,
                                            MovementPattern.HOMING])
        else:  # BOSS
            self.width = 80; self.height = 70
            self.speed = config.enemy_speed * 0.5
            self.color = PURPLE; self.accent_color = MAGENTA
            self.hp = config.enemy_hp + 3
            self.movement = MovementPattern.SINE

        self.max_hp = self.hp
        self.shoot_timer = 0.0
        self.shoot_interval = random.uniform(3.0, 5.0) if config.difficulty != Difficulty.EXTREME else random.uniform(1.5, 3.0)
        self.animation_frame = random.randint(0, 60)
        self._sine_offset = random.uniform(0, math.pi * 2)
        self._zigzag_dir = 1
        self._zigzag_timer = 0.0
        self._circle_angle = 0.0
        self._boss_phase = 0
        self._phase_timer = 0.0

    @property
    def center_x(self): return self.x + self.width // 2
    @property
    def center_y(self): return self.y + self.height // 2

    def update(self):
        dt = 1.0 / FPS
        self.animation_frame += 1
        self.shoot_timer += dt
        self._phase_timer += dt

        if self.type == EnemyType.BOSS:
            # Boss moves horizontally in a sine wave
            sine = math.sin(self._sine_offset + self.animation_frame * 0.03) * 100
            self.x += sine * 0.02
            self.y += self.speed * 0.3
            # Keep on screen
            self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
            if self.y > 150:  # Boss parks in upper area
                self.y = min(self.y, 150)

            # Phase switching
            if self._phase_timer > 12.0:
                self._boss_phase = (self._boss_phase + 1) % 3
                self._phase_timer = 0.0
        else:
            self.y += self.speed

            # Movement patterns
            if self.movement == MovementPattern.SINE:
                sine_amp = 80
                sine_freq = 0.03
                self.x += math.sin(self._sine_offset + self.animation_frame * sine_freq) * 2.0
            elif self.movement == MovementPattern.ZIGZAG:
                self._zigzag_timer += dt
                if self._zigzag_timer > 0.8:
                    self._zigzag_timer = 0.0
                    self._zigzag_dir *= -1
                self.x += self._zigzag_dir * self.speed * 1.5
            elif self.movement == MovementPattern.HOMING:
                # Drift toward center of screen slowly
                target_x = SCREEN_WIDTH // 2
                dx = target_x - self.center_x
                self.x += max(-2, min(2, dx * 0.01))

            self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))

    def can_shoot(self) -> bool:
        return self.shoot_timer >= self.shoot_interval

    def shoot(self) -> List[Bullet]:
        bullets = []
        if not self.can_shoot():
            return bullets

        self.shoot_timer = 0.0
        self.shoot_interval = random.uniform(2.0, 4.5)

        cx = self.center_x; by = self.y + self.height

        if self.type == EnemyType.BOSS:
            if self._boss_phase == 0:
                # Fan pattern: 5 bullets spread
                for deg in [-30, -15, 0, 15, 30]:
                    a = math.radians(90 + deg)
                    bullets.append(Bullet(cx, by, self.config.enemy_bullet_speed,
                                          False, a, 4, PURPLE))
            elif self._boss_phase == 1:
                # Circle burst: 12 bullets
                for i in range(12):
                    a = i * math.pi * 2 / 12
                    bullets.append(Bullet(cx, self.center_y, self.config.enemy_bullet_speed * 0.6,
                                          False, a, 3, MAGENTA))
            else:
                # Aimed shot: 3 bullets toward bottom
                for deg in [-10, 0, 10]:
                    a = math.radians(90 + deg)
                    bullets.append(Bullet(cx, by, self.config.enemy_bullet_speed * 1.2,
                                          False, a, 5, RED))
        else:
            bullets.append(Bullet(cx, by,
                                  self.config.enemy_bullet_speed, False,
                                  math.pi / 2, 4, RED))
        return bullets

    def draw(self, screen):
        cx = self.center_x

        # Flame
        intensity = 4 + int(2 * math.sin(self.animation_frame * 0.4))
        flame_y = self.y
        pygame.draw.polygon(screen, (255, 200, 0), [
            (cx - 6, flame_y), (cx - 4, flame_y - intensity),
            (cx, flame_y - intensity - 2), (cx + 4, flame_y - intensity),
            (cx + 6, flame_y)])
        pygame.draw.polygon(screen, (255, 150, 0), [
            (cx - 4, flame_y), (cx - 2, flame_y - intensity + 1),
            (cx, flame_y - intensity), (cx + 2, flame_y - intensity + 1),
            (cx + 4, flame_y)])

        # Body
        body_top = [(self.x, self.y + self.height // 4),
                    (cx, self.y + self.height), (self.x + self.width, self.y + self.height // 4)]
        pygame.draw.polygon(screen, self.color, body_top)

        darker = (max(0, self.color[0] - 40), max(0, self.color[1] - 40), max(0, self.color[2] - 40))
        body_bottom = [(self.x, self.y + self.height // 4), (cx, self.y + self.height),
                       (self.x + self.width, self.y + self.height // 4), (cx, self.y)]
        pygame.draw.polygon(screen, darker, body_bottom)

        # Wings
        wing_y = self.y + self.height // 3
        pygame.draw.polygon(screen, self.accent_color,
                            [(self.x, wing_y), (self.x - 12, self.y + 2),
                             (self.x - 8, self.y), (self.x, self.y + 2)])
        pygame.draw.polygon(screen, self.accent_color,
                            [(self.x + self.width, wing_y), (self.x + self.width + 12, self.y + 2),
                             (self.x + self.width + 8, self.y), (self.x + self.width, self.y + 2)])

        # Nose
        nose_color = tuple(min(255, c + 50) for c in self.color)
        pygame.draw.polygon(screen, nose_color, [
            (cx, self.y), (cx - 4, self.y + 8), (cx + 4, self.y + 8)])

        # Boss crown
        if self.type == EnemyType.BOSS:
            crown_y = self.y - 15
            pts = [(cx, crown_y - 10), (cx - 12, crown_y + 5), (cx - 6, crown_y),
                   (cx - 2, crown_y + 5), (cx + 2, crown_y), (cx + 6, crown_y + 5),
                   (cx + 12, crown_y), (cx, crown_y - 10)]
            pygame.draw.polygon(screen, GOLD, pts, 3)

        # HP bar for multi-HP or BOSS
        if self.hp < self.max_hp:
            bw = self.width; bh = 5
            bx = self.x; by_bar = self.y - 12
            pygame.draw.rect(screen, RED, (bx, by_bar, bw, bh))
            ratio = self.hp / self.max_hp
            bar_color = GREEN if ratio > 0.5 else RED
            pygame.draw.rect(screen, bar_color, (bx, by_bar, bw * ratio, bh))

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def is_past_player_line(self) -> bool:
        return self.y + self.height > PLAYER_Y

    def take_damage(self, damage: int = 1) -> bool:
        self.hp -= damage
        return self.hp <= 0

# ── Game ──────────────────────────────────────────────────────────────────
config: GameConfig = None  # global, set in Game.__init__

class Game:
    def __init__(self, difficulty: Difficulty):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Fighter Battle — Enhanced")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.victory = False
        self.paused = False
        self.game_started = True
        self.pause_start_time = 0
        self.total_pause_time = 0

        global config
        config = GameConfig.from_difficulty(difficulty)

        # Game objects
        plane_spacing = 70
        center_x = SCREEN_WIDTH // 2
        self.players = [
            Player(center_x - plane_spacing - 25),
            Player(center_x - 25),
            Player(center_x + plane_spacing - 25),
        ]
        self.player = self.players[1]
        self.formation = Formation.V_SHAPE
        self.enemies: List[Enemy] = []
        self.bullets: List[Bullet] = []
        self.powerups: List[PowerUp] = []

        # Visual systems
        self.starfield = StarField()
        self.particles = ParticleSystem()
        self.floating_texts: List[FloatingText] = []
        self.shake = ScreenShake()

        # Scoring
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.combo_timer = 0
        self.combo_timeout = 60  # frames before combo resets

        self.start_time = pygame.time.get_ticks()
        self.enemy_spawn_timer = 0.0
        self.last_elapsed_time = 0.0

        # Boss wave tracking
        self.boss_spawned = False
        self.boss_kills = 0

        # Fonts
        self.font_large = get_font(72)
        self.font_medium = get_font(48)
        self.font_small = get_font(36)
        self.font_tiny = get_font(18)

    # ── Spawning ──────────────────────────────────────────────────────
    def spawn_enemy(self):
        enemy_types = [EnemyType.FAST, EnemyType.STRONG]
        boss_prob = 0.05
        if config.difficulty == Difficulty.EXTREME:
            boss_prob = 0.18
        elif config.difficulty == Difficulty.HARD:
            boss_prob = 0.10

        if random.random() < boss_prob:
            enemy_types.append(EnemyType.BOSS)

        # Spawn at random x, but occasionally in formation
        etype = random.choice(enemy_types)
        if etype == EnemyType.BOSS and self.boss_spawned:
            etype = EnemyType.STRONG  # only one boss at a time

        if etype == EnemyType.BOSS:
            self.boss_spawned = True
            self.shake.trigger(8, 15)
            self.floating_texts.append(
                FloatingText(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                             "⚠ BOSS INCOMING ⚠", RED, 60, 48, -1.5))

        if random.random() < 0.3:
            # Formation spawn: 3 enemies in V
            base_x = random.randint(50, SCREEN_WIDTH - 150)
            for off_x in [-60, 0, 60]:
                e = Enemy(base_x + off_x, etype if etype != EnemyType.BOSS else EnemyType.STRONG, config)
                self.enemies.append(e)
        else:
            x = random.randint(10, SCREEN_WIDTH - 80)
            self.enemies.append(Enemy(x, etype, config))

    def drop_powerup(self, x: float, y: float):
        """Drop a random power-up at location."""
        weights = [15, 15, 15, 10, 15, 10]  # POWER_BOOST, HEALTH, RAPID_FIRE, SHIELD, MULTI_SHOT, BOMB
        ptype = random.choices(list(PowerUpType), weights=weights, k=1)[0]
        self.powerups.append(PowerUp(x, y, ptype))

    def bomb(self):
        """Clear screen — destroy all enemies with bomb."""
        if self.player.bomb_count <= 0:
            return
        self.player.bomb_count -= 1
        self.shake.trigger(12, 20)
        # Flash
        self.floating_texts.append(
            FloatingText(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                         "💣", RED, 30, 72, -1.0))
        for enemy in self.enemies:
            self.particles.emit(enemy.center_x, enemy.center_y, 20,
                                [YELLOW, ORANGE, RED, WHITE], 6.0, 25)
            self.score += 10 * enemy.max_hp
            self.combo += 1
            self.combo_timer = self.combo_timeout
            self.floating_texts.append(
                FloatingText(enemy.center_x, enemy.y, "+10", YELLOW, 25))
        self.enemies.clear()
        # Also clear enemy bullets
        self.bullets = [b for b in self.bullets if b.is_player]

    # ── Homing update ─────────────────────────────────────────────────
    def _update_homing(self, bullet: Bullet):
        """Steer homing bullet toward nearest enemy."""
        if not self.enemies:
            return
        nearest = min(self.enemies, key=lambda e:
            math.hypot(e.center_x - bullet.x, e.center_y - bullet.y))
        dx = nearest.center_x - bullet.x
        dy = nearest.center_y - bullet.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            desired_vx = dx / dist * abs(bullet.vy)
            desired_vy = dy / dist * abs(bullet.vy) if dy > 0 else -abs(bullet.vy)
            bullet.vx += (desired_vx - bullet.vx) * bullet.homing_strength
            bullet.vy += (desired_vy - bullet.vy) * bullet.homing_strength

    # ── Update ────────────────────────────────────────────────────────
    def update(self, keys):
        if self.game_over:
            return
        if self.paused:
            return

        # Systems
        self.starfield.update()
        self.particles.update()
        self.shake.update()
        self.floating_texts = [t for t in self.floating_texts if t.update()]

        # Combo decay
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0

        # ── Formation update ──────────────────────────────────────────
        move_delta = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_delta = -self.players[0].speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_delta = self.players[0].speed

        if move_delta != 0 or True:  # always update formation
            base_x = self.players[1].x
            plane_spacing = 70
            if move_delta != 0:
                base_x += move_delta
                base_x = max(0, min(base_x, SCREEN_WIDTH - 70 * 2 - self.players[0].width))

            if self.formation == Formation.V_SHAPE:
                self.players[0].x = base_x - plane_spacing
                self.players[0].y = PLAYER_Y + 20
                self.players[1].x = base_x
                self.players[1].y = PLAYER_Y
                self.players[2].x = base_x + plane_spacing
                self.players[2].y = PLAYER_Y + 20
            elif self.formation == Formation.HORIZONTAL:
                for i, p in enumerate(self.players):
                    p.x = base_x + (i - 1) * plane_spacing
                    p.y = PLAYER_Y
            elif self.formation == Formation.VERTICAL:
                self.players[0].x = base_x
                self.players[0].y = PLAYER_Y - 30
                self.players[1].x = base_x
                self.players[1].y = PLAYER_Y
                self.players[2].x = base_x
                self.players[2].y = PLAYER_Y + 30

            # Clamp
            for p in self.players:
                p.x = max(0, min(p.x, SCREEN_WIDTH - p.width))

        # ── Player updates ────────────────────────────────────────────
        for p in self.players:
            p.update(keys)
            if keys[pygame.K_SPACE]:
                bullets = p.shoot(config)
                if bullets:
                    self.bullets.extend(bullets)

        # ── Timing ────────────────────────────────────────────────────
        if self.game_started:
            elapsed = (pygame.time.get_ticks() - self.start_time - self.total_pause_time) / 1000.0
            remaining = max(0, GAME_DURATION - elapsed)
        else:
            remaining = max(0, GAME_DURATION - self.last_elapsed_time)

        # ── Spawning ──────────────────────────────────────────────────
        spawn_rate = config.enemy_spawn_rate
        if remaining <= 10.0:
            spawn_rate *= 0.5  # double frequency
        self.enemy_spawn_timer += 1 / FPS
        if self.enemy_spawn_timer >= spawn_rate:
            self.enemy_spawn_timer = 0.0
            self.spawn_enemy()
            if remaining <= 10.0 and random.random() < 0.3:
                self.spawn_enemy()

        # ── Enemy updates ────────────────────────────────────────────
        for enemy in self.enemies[:]:
            enemy.update()
            for b in enemy.shoot():
                self.bullets.append(b)
            if enemy.is_past_player_line():
                if self.player.shield_count > 0:
                    self.player.shield_count -= 1
                    self.particles.emit(enemy.center_x, enemy.y, 12,
                                        [BLUE, CYAN, WHITE], 3.0, 20)
                    self.floating_texts.append(
                        FloatingText(enemy.center_x, enemy.y, "SHIELD!", BLUE, 30))
                    self.enemies.remove(enemy)
                else:
                    self.game_over = True
                    self.victory = False
                    self.game_started = False
                    self.particles.emit(enemy.center_x, PLAYER_Y, 30,
                                        [RED, ORANGE, YELLOW], 5.0, 40)
                    self.shake.trigger(10, 20)
                    break

        # ── Bullet updates ────────────────────────────────────────────
        for bullet in self.bullets[:]:
            bullet.update()
            if hasattr(bullet, 'is_homing') and bullet.is_homing:
                self._update_homing(bullet)
            if bullet.is_off_screen():
                self.bullets.remove(bullet)

        # ── PowerUp updates ───────────────────────────────────────────
        for powerup in self.powerups[:]:
            powerup.update()
            if powerup.is_off_screen():
                self.powerups.remove(powerup)

        # ── Collision: player bullets vs enemies ──────────────────────
        for bullet in self.bullets[:]:
            if not bullet.is_player:
                continue
            for enemy in self.enemies[:]:
                enemy_rect = enemy.get_rect()
                if (bullet.x < enemy_rect.x + enemy_rect.width and
                    bullet.x + bullet.radius > enemy_rect.x and
                    bullet.y < enemy_rect.y + enemy_rect.height and
                    bullet.y + bullet.radius > enemy_rect.y):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    dmg = self.player.attack_power
                    killed = enemy.take_damage(dmg)

                    # Floating damage
                    self.floating_texts.append(
                        FloatingText(enemy.center_x + random.randint(-10, 10),
                                     enemy.y, str(dmg), YELLOW, 25, 20, -1.5))

                    if killed:
                        # Explosion particles
                        explosion_colors = [RED, ORANGE, YELLOW, WHITE]
                        if enemy.type == EnemyType.BOSS:
                            explosion_colors.extend([PURPLE, MAGENTA, GOLD])
                        self.particles.emit(enemy.center_x, enemy.center_y,
                                            15 if enemy.type != EnemyType.BOSS else 40,
                                            explosion_colors,
                                            5.0 if enemy.type != EnemyType.BOSS else 8.0,
                                            30 if enemy.type != EnemyType.BOSS else 50)
                        if enemy.type == EnemyType.BOSS:
                            self.shake.trigger(6, 12)
                            self.boss_spawned = False
                            self.boss_kills += 1
                            self.floating_texts.append(
                                FloatingText(enemy.center_x, enemy.y,
                                             f"BOSS +{10 * enemy.max_hp}",
                                             GOLD, 50, 32, -1.5))

                        # Score & combo
                        points = 10 * enemy.max_hp
                        self.score += points
                        self.combo += 1
                        self.max_combo = max(self.max_combo, self.combo)
                        self.combo_timer = self.combo_timeout

                        if self.combo >= 10:
                            combo_txt = f"{self.combo}x COMBO!"
                            color = RED if self.combo >= 30 else (ORANGE if self.combo >= 20 else YELLOW)
                            sz = 36 if self.combo < 20 else 48
                            self.floating_texts.append(
                                FloatingText(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120,
                                             combo_txt, color, 40, sz, -1.0))

                        # Drop powerup
                        if random.random() < 0.4:
                            self.drop_powerup(enemy.center_x, enemy.y + enemy.height)

                        self.enemies.remove(enemy)
                    break

        # ── Collision: enemy bullets vs players ───────────────────────
        for bullet in self.bullets[:]:
            if bullet.is_player:
                continue
            for player in self.players[:]:
                if player.invincible > 0:
                    continue
                pr = player.get_rect()
                if (bullet.x < pr.x + pr.width and bullet.x + bullet.radius > pr.x and
                    bullet.y < pr.y + pr.height and bullet.y + bullet.radius > pr.y):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    player.hp -= 1
                    player.invincible = 30  # 0.5 sec invincibility
                    self.shake.trigger(4, 8)
                    self.particles.emit(player.x + player.width // 2,
                                        player.y + player.height // 2,
                                        8, [BLUE, CYAN, WHITE], 3.0, 20)
                    self.floating_texts.append(
                        FloatingText(player.x + player.width // 2, player.y,
                                     "-1❤", RED, 30, 24, -2.0))
                    if player.hp <= 0:
                        # Big explosion
                        self.particles.emit(player.x + player.width // 2,
                                            player.y + player.height // 2,
                                            30, [BLUE, CYAN, YELLOW, WHITE], 6.0, 40)
                        if player == self.player:
                            # Main player dead → game over
                            self.game_over = True
                            self.victory = False
                            self.game_started = False
                            self.shake.trigger(15, 25)
                        else:
                            self.players.remove(player)
                    break

        # ── Collision: players vs powerups ────────────────────────────
        for powerup in self.powerups[:]:
            picked = False
            for player in self.players:
                if player.get_rect().colliderect(powerup.get_rect()):
                    picked = True
                    break
            if picked:
                self.particles.emit(powerup.x + 15, powerup.y + 15, 8,
                                    [WHITE, GOLD, CYAN], 2.0, 15)
                self.floating_texts.append(
                    FloatingText(powerup.x + 15, powerup.y,
                                 powerup.type.name, GOLD, 20, 16, -1.5))
                if powerup.type == PowerUpType.POWER_BOOST:
                    for pl in self.players:
                        pl.attack_power = min(5, pl.attack_power + 1)
                elif powerup.type == PowerUpType.HEALTH:
                    self.player.hp = min(self.player.max_hp, self.player.hp + 1)
                elif powerup.type == PowerUpType.RAPID_FIRE:
                    for pl in self.players:
                        pl.rapid_fire_count = min(3, pl.rapid_fire_count + 1)
                elif powerup.type == PowerUpType.SHIELD:
                    self.player.shield_count = min(3, self.player.shield_count + 1)
                elif powerup.type == PowerUpType.MULTI_SHOT:
                    for pl in self.players:
                        pl.multi_shot_count = min(3, pl.multi_shot_count + 1)
                elif powerup.type == PowerUpType.BOMB:
                    self.player.bomb_count = min(3, self.player.bomb_count + 1)
                self.powerups.remove(powerup)

        # ── Time check ────────────────────────────────────────────────
        if self.game_started:
            elapsed = (pygame.time.get_ticks() - self.start_time - self.total_pause_time) / 1000.0
            self.last_elapsed_time = elapsed
            if elapsed >= GAME_DURATION:
                self.game_over = True
                self.victory = True
                self.game_started = False

    # ── Draw ──────────────────────────────────────────────────────────
    def draw(self):
        self.screen.fill(DARK_BG)

        # Starfield
        self.starfield.draw(self.screen)

        # Apply shake offset
        ox, oy = self.shake.offset_x, self.shake.offset_y

        # Create a surface for game objects with shake applied
        # We'll just apply shake when blitting key objects
        def shake_rect(rect):
            return pygame.Rect(rect.x + ox, rect.y + oy, rect.width, rect.height)

        # Players (with shake)
        for player in self.players:
            orig_x, orig_y = player.x, player.y
            player.x += ox; player.y += oy
            player.draw(self.screen)
            player.x, player.y = orig_x, orig_y

        # Enemies (with shake)
        for enemy in self.enemies:
            orig_x, orig_y = enemy.x, enemy.y
            enemy.x += ox; enemy.y += oy
            enemy.draw(self.screen)
            enemy.x, enemy.y = orig_x, orig_y

        # Bullets (with shake)
        for bullet in self.bullets:
            bullet.x += ox; bullet.y += oy
            bullet.draw(self.screen)
            bullet.x -= ox; bullet.y -= oy

        # Powerups (with shake)
        for powerup in self.powerups:
            powerup.x += ox; powerup.y += oy
            powerup.draw(self.screen)
            powerup.x -= ox; powerup.y -= oy

        # Particles (no shake — pure visual)
        self.particles.draw(self.screen)

        # Floating texts (no shake)
        for ft in self.floating_texts:
            ft.draw(self.screen)

        # ── HUD ───────────────────────────────────────────────────────
        if self.game_started:
            elapsed = (pygame.time.get_ticks() - self.start_time - self.total_pause_time) / 1000.0
        else:
            elapsed = self.last_elapsed_time
        remaining = max(0, GAME_DURATION - elapsed)

        # Top-left: Score & Time
        score_surf = self.font_small.render(f"SCORE {self.score}", True, WHITE)
        self.screen.blit(score_surf, (10, 10))

        time_color = WHITE if remaining > 10 else (RED if int(remaining * 4) % 2 == 0 else WHITE)
        time_surf = self.font_small.render(f"TIME {remaining:.1f}s", True, time_color)
        self.screen.blit(time_surf, (10, 50))

        # Combo display
        if self.combo >= 3 and self.combo_timer > 0:
            combo_color = RED if self.combo >= 30 else (ORANGE if self.combo >= 20 else YELLOW)
            combo_surf = self.font_medium.render(f"{self.combo}x", True, combo_color)
            combo_rect = combo_surf.get_rect(center=(SCREEN_WIDTH // 2, 45))
            self.screen.blit(combo_surf, combo_rect)

        # Top-right: HP, Power, active effects
        right_x = SCREEN_WIDTH - 220
        # HP with hearts
        hearts = "❤" * self.player.hp + "♡" * (self.player.max_hp - self.player.hp)
        hp_surf = self.font_small.render(f"{hearts}", True, GREEN)
        self.screen.blit(hp_surf, (right_x, 10))

        # Power
        pw_surf = self.font_small.render(f"POW x{self.player.attack_power}", True, CYAN)
        self.screen.blit(pw_surf, (right_x, 50))

        # Weapon type
        wp_surf = self.font_small.render(f"WPN {self.player.weapon_type.upper()}", True, GOLD)
        self.screen.blit(wp_surf, (right_x, 90))

        # Formation
        form_names = {Formation.V_SHAPE: "V", Formation.HORIZONTAL: "===", Formation.VERTICAL: "|||"}
        fm_surf = self.font_tiny.render(f"FORM {form_names[self.formation]} (F)", True, WHITE)
        self.screen.blit(fm_surf, (right_x, 130))

        y_off = 160
        if self.player.rapid_fire_count > 0:
            s = self.font_tiny.render(f"╡ RAPID {self.player.rapid_fire_count}", True, RED)
            self.screen.blit(s, (right_x, y_off)); y_off += 22
        if self.player.shield_count > 0:
            s = self.font_tiny.render(f"🛡 SHIELD {self.player.shield_count}", True, BLUE)
            self.screen.blit(s, (right_x, y_off)); y_off += 22
        if self.player.multi_shot_count > 0:
            s = self.font_tiny.render(f"✦ MULTI {self.player.multi_shot_count}", True, PURPLE)
            self.screen.blit(s, (right_x, y_off)); y_off += 22
        if self.player.bomb_count > 0:
            s = self.font_tiny.render(f"💣 BOMB {self.player.bomb_count} (B)", True, RED)
            self.screen.blit(s, (right_x, y_off)); y_off += 22

        # Bottom: controls reminder
        ctrl_surf = self.font_tiny.render(
            "← → move | SPACE shoot | F formation | B bomb | P pause | ESC quit", True, (100, 100, 120))
        ctrl_rect = ctrl_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 12))
        self.screen.blit(ctrl_surf, ctrl_rect)

        # ── Pause overlay ─────────────────────────────────────────────
        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            pause_surf = self.font_medium.render("PAUSED", True, YELLOW)
            pr = pause_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(pause_surf, pr)
            inst_surf = self.font_small.render("Press P to resume", True, WHITE)
            ir = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(inst_surf, ir)

        # ── Game Over overlay ─────────────────────────────────────────
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            if self.victory:
                title_surf = self.font_large.render("VICTORY!", True, GREEN)
            else:
                title_surf = self.font_large.render("DEFEAT!", True, RED)
            tr = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 70))
            self.screen.blit(title_surf, tr)

            final_score = self.font_medium.render(f"Score: {self.score}", True, YELLOW)
            sr = final_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(final_score, sr)

            combo_str = f"Max Combo: {self.max_combo}x"
            combo_s = self.font_small.render(combo_str, True, CYAN)
            cr = combo_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(combo_s, cr)

            restart_surf = self.font_small.render("Press R to restart, ESC to exit", True, WHITE)
            rr = restart_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
            self.screen.blit(restart_surf, rr)

        pygame.display.flip()

    # ── Events ────────────────────────────────────────────────────────
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if self.game_over and event.key == pygame.K_r:
                    self.restart()
                if event.key == pygame.K_p and not self.game_over:
                    if self.paused:
                        self.total_pause_time += pygame.time.get_ticks() - self.pause_start_time
                        self.paused = False
                    else:
                        self.pause_start_time = pygame.time.get_ticks()
                        self.paused = True
                        if self.game_started:
                            self.last_elapsed_time = (
                                pygame.time.get_ticks() - self.start_time - self.total_pause_time) / 1000.0
                if event.key == pygame.K_f and not self.game_over and not self.paused:
                    # Cycle formation
                    forms = list(Formation)
                    idx = forms.index(self.formation)
                    self.formation = forms[(idx + 1) % len(forms)]
                    self.floating_texts.append(
                        FloatingText(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50,
                                     f"Formation: {self.formation.name}", CYAN, 30, 20))
                if event.key == pygame.K_b and not self.game_over and not self.paused:
                    self.bomb()

    # ── Restart ───────────────────────────────────────────────────────
    def restart(self):
        self.game_over = False; self.victory = False
        self.paused = False; self.game_started = True
        self.pause_start_time = 0; self.total_pause_time = 0
        self.boss_spawned = False; self.boss_kills = 0
        plane_spacing = 70; center_x = SCREEN_WIDTH // 2
        self.players = [
            Player(center_x - plane_spacing - 25),
            Player(center_x - 25),
            Player(center_x + plane_spacing - 25),
        ]
        self.player = self.players[1]
        self.formation = Formation.V_SHAPE
        self.enemies = []; self.bullets = []; self.powerups = []
        self.particles = ParticleSystem()
        self.floating_texts = []
        self.shake = ScreenShake()
        self.score = 0; self.combo = 0; self.max_combo = 0; self.combo_timer = 0
        self.start_time = pygame.time.get_ticks()
        self.enemy_spawn_timer = 0.0
        if hasattr(self, "last_elapsed_time"):
            del self.last_elapsed_time

    # ── Main Loop ─────────────────────────────────────────────────────
    def run(self):
        while self.running:
            keys = pygame.key.get_pressed()
            self.handle_events()
            self.update(keys)
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

# ═══════════════════════════════════════════════════════════════════════════
# Menu
# ═══════════════════════════════════════════════════════════════════════════
def show_menu(screen, clock) -> Optional[Difficulty]:
    font_title = get_font(96)
    font_option = get_font(64)
    font_small = get_font(36)
    font_tiny = get_font(20)

    selected = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % 4
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % 4
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return list(Difficulty)[selected]

        screen.fill((10, 10, 30))

        title = font_title.render("FIGHTER BATTLE", True, GOLD)
        tr = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title, tr)

        subtitle = font_small.render("ENHANCED EDITION", True, CYAN)
        sr = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 140))
        screen.blit(subtitle, sr)

        difficulties = [
            ("Easy Mode", GREEN, "For beginners — slow enemies, fewer bullets"),
            ("Medium Mode", YELLOW, "A fair challenge"),
            ("Hard Mode", RED, "Fast enemies, tight patterns"),
            ("Extreme Mode", MAGENTA, "No mercy — good luck!"),
        ]

        for i, (text, color, desc) in enumerate(difficulties):
            if i == selected:
                t = font_option.render(f"> {text} <", True, color)
            else:
                t = font_option.render(text, True, WHITE)
            tr2 = t.get_rect(center=(SCREEN_WIDTH // 2, 230 + i * 75))
            screen.blit(t, tr2)
            # Description
            if i == selected:
                ds = font_tiny.render(desc, True, color)
                dr = ds.get_rect(center=(SCREEN_WIDTH // 2, 230 + i * 75 + 35))
                screen.blit(ds, dr)

        inst = font_small.render("UP/DOWN select  |  ENTER confirm", True, WHITE)
        ir = inst.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        screen.blit(inst, ir)

        ctrl = font_small.render(
            "F: formation  |  B: bomb  |  P: pause  |  SPACE: shoot", True, CYAN)
        cr = ctrl.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        screen.blit(ctrl, cr)

        pygame.display.flip()
        clock.tick(FPS)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Fighter Battle — Enhanced")
    clock = pygame.time.Clock()

    while True:
        difficulty = show_menu(screen, clock)
        if difficulty is None:
            break
        game = Game(difficulty)
        game.run()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        clock = pygame.time.Clock()

if __name__ == "__main__":
    main()
