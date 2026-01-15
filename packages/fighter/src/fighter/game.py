"""
Fighter Plane Battle Game
"""

import math
import random
from dataclasses import dataclass
from enum import Enum
from typing import List

import pygame

# 初始化Pygame
pygame.init()

# Get font for text rendering
_font_cache = {}


def get_font(size):
    """Get font for text rendering"""
    # Use cache to avoid repeated lookups
    if size in _font_cache:
        return _font_cache[size]

    # Use system fonts, pygame will automatically select the first available
    font_list = ["Arial", "Helvetica", "Times New Roman", "Courier New"]

    # Use SysFont with font list
    font = pygame.font.SysFont(font_list, size)
    _font_cache[size] = font
    return font


# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GAME_DURATION = 120  # 游戏时长（秒）- 2分钟
PLAYER_Y = SCREEN_HEIGHT - 80  # 玩家战斗机Y坐标

# 颜色定义（色彩丰富）
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)
LIME = (50, 205, 50)
GOLD = (255, 215, 0)


# 难度级别
class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


# 道具类型
class PowerUpType(Enum):
    POWER_BOOST = 1  # 攻击力提升（金色星形）
    HEALTH = 2  # 生命恢复（绿色十字）
    RAPID_FIRE = 3  # 射击速度提升（红色闪电）
    SHIELD = 4  # 防护盾（蓝色盾牌）
    MULTI_SHOT = 5  # 多发子弹（紫色星星）


@dataclass
class GameConfig:
    """游戏配置"""

    difficulty: Difficulty
    enemy_spawn_rate: float  # 敌机生成频率（秒）
    enemy_speed: float  # 敌机移动速度
    enemy_hp: int  # 敌机生命值
    player_bullet_speed: float  # 玩家炮弹速度
    enemy_bullet_speed: float  # 敌机炮弹速度（如果有）

    @classmethod
    def from_difficulty(cls, difficulty: Difficulty):
        """根据难度创建配置"""
        if difficulty == Difficulty.EASY:
            return cls(
                difficulty=difficulty,
                enemy_spawn_rate=3.5,  # Slower enemy spawn (was 2.0)
                enemy_speed=1.0,  # Slower enemy movement (was 1.5)
                enemy_hp=1,
                player_bullet_speed=10,  # Faster player bullets (was 8)
                enemy_bullet_speed=3,
            )
        elif difficulty == Difficulty.MEDIUM:
            return cls(
                difficulty=difficulty,
                enemy_spawn_rate=2.0,  # Slower spawn (was 1.2)
                enemy_speed=1.8,  # Slower movement (was 2.5)
                enemy_hp=1,
                player_bullet_speed=9,  # Faster bullets (was 8)
                enemy_bullet_speed=4,
            )
        else:  # HARD
            return cls(
                difficulty=difficulty,
                enemy_spawn_rate=1.2,  # Slower spawn (was 0.8)
                enemy_speed=2.5,  # Slower movement (was 3.5)
                enemy_hp=1,  # Lower HP (was 2)
                player_bullet_speed=9,  # Faster bullets (was 8)
                enemy_bullet_speed=5,
            )


class Bullet:
    """炮弹类"""

    def __init__(self, x: float, y: float, speed: float, is_player: bool):
        self.x = x
        self.y = y
        self.speed = speed
        self.is_player = is_player  # True为玩家炮弹，False为敌机炮弹
        self.width = 5
        self.height = 10

    def update(self):
        """更新炮弹位置"""
        if self.is_player:
            self.y -= self.speed
        else:
            self.y += self.speed

    def draw(self, screen):
        """绘制炮弹"""
        color = YELLOW if self.is_player else RED
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))

    def is_off_screen(self) -> bool:
        """判断炮弹是否超出屏幕"""
        return self.y < 0 or self.y > SCREEN_HEIGHT


class PowerUp:
    """道具类 - 多种类型的道具"""

    def __init__(self, x: float, y: float, powerup_type: PowerUpType):
        self.x = x
        self.y = y
        self.type = powerup_type
        self.width = 30
        self.height = 30
        self.speed = 2.0
        self.animation_time = 0

    def update(self):
        """更新道具位置"""
        self.y += self.speed
        self.animation_time += 1

    def draw(self, screen):
        """根据道具类型绘制不同的外观"""
        center_x = int(self.x + self.width // 2)
        center_y = int(self.y + self.height // 2)
        radius = self.width // 2
        flash = (self.animation_time // 5) % 2 == 0

        if self.type == PowerUpType.POWER_BOOST:
            # 金色星形 - 攻击力提升
            pygame.draw.circle(screen, GOLD, (center_x, center_y), radius)
            pygame.draw.circle(screen, YELLOW, (center_x, center_y), radius - 3)
            if flash:
                pygame.draw.circle(screen, ORANGE, (center_x, center_y), radius - 6)
            # 绘制星形
            star_points = []
            for i in range(5):
                angle = (i * 2 * math.pi / 5) - math.pi / 2
                outer_x = center_x + radius * 0.8 * math.cos(angle)
                outer_y = center_y + radius * 0.8 * math.sin(angle)
                star_points.append((int(outer_x), int(outer_y)))
                inner_angle = angle + math.pi / 5
                inner_x = center_x + radius * 0.4 * math.cos(inner_angle)
                inner_y = center_y + radius * 0.4 * math.sin(inner_angle)
                star_points.append((int(inner_x), int(inner_y)))
            if len(star_points) >= 3:
                pygame.draw.polygon(screen, WHITE, star_points[:5])

        elif self.type == PowerUpType.HEALTH:
            # 绿色十字 - 生命恢复
            pygame.draw.circle(screen, GREEN, (center_x, center_y), radius)
            pygame.draw.circle(screen, LIME, (center_x, center_y), radius - 3)
            # 绘制十字
            cross_size = radius - 4
            pygame.draw.rect(
                screen,
                WHITE,
                (
                    center_x - cross_size // 2,
                    center_y - cross_size,
                    cross_size,
                    cross_size * 2,
                ),
            )
            pygame.draw.rect(
                screen,
                WHITE,
                (
                    center_x - cross_size,
                    center_y - cross_size // 2,
                    cross_size * 2,
                    cross_size,
                ),
            )

        elif self.type == PowerUpType.RAPID_FIRE:
            # 红色闪电 - 射击速度提升
            pygame.draw.circle(screen, RED, (center_x, center_y), radius)
            pygame.draw.circle(screen, ORANGE, (center_x, center_y), radius - 3)
            # 绘制闪电
            lightning_points = [
                (center_x - 5, center_y - 8),
                (center_x + 2, center_y - 2),
                (center_x - 2, center_y),
                (center_x + 5, center_y + 8),
                (center_x - 2, center_y + 4),
                (center_x + 2, center_y + 2),
                (center_x - 5, center_y - 8),
            ]
            pygame.draw.polygon(screen, YELLOW, lightning_points)

        elif self.type == PowerUpType.SHIELD:
            # 蓝色盾牌 - 防护盾
            pygame.draw.circle(screen, BLUE, (center_x, center_y), radius)
            pygame.draw.circle(screen, CYAN, (center_x, center_y), radius - 3)
            # 绘制盾牌形状
            shield_points = [
                (center_x, center_y - radius + 2),
                (center_x - radius + 2, center_y - 2),
                (center_x - radius + 2, center_y + 4),
                (center_x, center_y + radius - 2),
                (center_x + radius - 2, center_y + 4),
                (center_x + radius - 2, center_y - 2),
            ]
            pygame.draw.polygon(screen, WHITE, shield_points)

        elif self.type == PowerUpType.MULTI_SHOT:
            # 紫色星星 - 多发子弹
            pygame.draw.circle(screen, PURPLE, (center_x, center_y), radius)
            pygame.draw.circle(screen, MAGENTA, (center_x, center_y), radius - 3)
            if flash:
                pygame.draw.circle(screen, PINK, (center_x, center_y), radius - 6)
            # 绘制多个小星星
            for i in range(3):
                offset_x = int(center_x + (i - 1) * 6)
                offset_y = center_y
                small_points = []
                for j in range(5):
                    angle = (j * 2 * math.pi / 5) - math.pi / 2
                    px = offset_x + 4 * math.cos(angle)
                    py = offset_y + 4 * math.sin(angle)
                    small_points.append((int(px), int(py)))
                if len(small_points) >= 3:
                    pygame.draw.polygon(screen, WHITE, small_points[:5])

    def get_rect(self) -> pygame.Rect:
        """获取碰撞矩形"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def is_off_screen(self) -> bool:
        """判断道具是否超出屏幕"""
        return self.y > SCREEN_HEIGHT


class Player:
    """玩家战斗机类"""

    def __init__(self, x: float):
        self.x = x
        self.y = PLAYER_Y
        self.width = 50
        self.height = 40
        self.speed = 7  # Faster player movement (was 5)
        self.shoot_cooldown = 0
        self.shoot_delay = 15  # 射击冷却时间（帧数）
        self.base_shoot_delay = 15  # 基础射击冷却时间
        self.hp = 3  # 玩家生命值
        self.max_hp = 3  # 最大生命值
        self.attack_power = 1  # 攻击力倍数（拾取道具后提升）
        self.rapid_fire_count = 0  # 快速射击道具数量
        self.shield_count = 0  # 防护盾数量
        self.multi_shot_count = 0  # 多发子弹道具数量
        self.animation_frame = 0  # 动画帧计数器
        self.tilt = 0  # 倾斜角度（用于移动动画）

    def update(self, keys):
        """更新玩家状态"""
        # 更新动画帧
        self.animation_frame += 1
        
        # 更新倾斜角度（用于移动动画）
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
            self.tilt = max(self.tilt - 2, -8)  # 向左倾斜
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
            self.tilt = min(self.tilt + 2, 8)  # 向右倾斜
        else:
            # 逐渐回正
            if self.tilt > 0:
                self.tilt = max(0, self.tilt - 1)
            elif self.tilt < 0:
                self.tilt = min(0, self.tilt + 1)

        # 限制在屏幕内
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))

        # 射击冷却
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def shoot(self) -> List[Bullet]:
        """发射炮弹，支持多发子弹"""
        bullets = []
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = self.shoot_delay

            # 计算射击延迟（快速射击效果）
            if self.rapid_fire_count > 0:
                self.shoot_delay = max(
                    8, self.base_shoot_delay - self.rapid_fire_count * 2
                )
            else:
                self.shoot_delay = self.base_shoot_delay

            # 基础射击
            bullets.append(
                Bullet(
                    self.x + self.width // 2 - 2.5,
                    self.y,
                    config.player_bullet_speed,
                    True,
                )
            )

            # 多发子弹效果
            if self.multi_shot_count > 0:
                # 两侧额外发射
                for offset in [-15, 15]:
                    bullets.append(
                        Bullet(
                            self.x + self.width // 2 - 2.5 + offset,
                            self.y,
                            config.player_bullet_speed,
                            True,
                        )
                    )
                # 如果有多发子弹2级以上，增加更多子弹
                if self.multi_shot_count >= 2:
                    for offset in [-30, 30]:
                        bullets.append(
                            Bullet(
                                self.x + self.width // 2 - 2.5 + offset,
                                self.y + 10,
                                config.player_bullet_speed * 0.9,
                                True,
                            )
                        )

        return bullets

    def draw(self, screen):
        """绘制玩家战斗机（改进的动画设计）"""
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # 引擎火焰效果（闪烁动画）
        flame_intensity = 5 + int(3 * math.sin(self.animation_frame * 0.3))
        flame_y = self.y + self.height
        
        # 绘制引擎火焰（从飞机尾部，多层渐变）
        for i in range(3):
            flame_height = (3 - i) * 4
            if i == 0:
                flame_color = (255, 200, 0)  # 黄色核心
            elif i == 1:
                flame_color = (255, 150, 0)  # 橙色
            else:
                flame_color = (255, 100, 0)  # 红色外围
            
            flame_points = [
                (center_x - 8 + self.tilt * 0.5, flame_y),
                (center_x - 5 + self.tilt * 0.3, flame_y + flame_height),
                (center_x + 5 - self.tilt * 0.3, flame_y + flame_height),
                (center_x + 8 - self.tilt * 0.5, flame_y),
            ]
            pygame.draw.polygon(screen, flame_color, flame_points)
        
        # 飞机主体（带阴影效果，更立体的设计）
        # 主体上部分（较亮）
        body_points = [
            (center_x + self.tilt * 0.3, self.y + 5),
            (self.x + 5, self.y + self.height - 8),
            (self.x + self.width - 5, self.y + self.height - 8),
        ]
        pygame.draw.polygon(screen, BLUE, body_points)
        
        # 主体下部分（较暗，增加立体感）
        body_bottom = [
            (self.x + 5, self.y + self.height - 8),
            (self.x + self.width - 5, self.y + self.height - 8),
            (center_x + self.tilt * 0.3, self.y + self.height),
        ]
        darker_blue = (max(0, BLUE[0] - 30), max(0, BLUE[1] - 30), max(0, BLUE[2] - 10))
        pygame.draw.polygon(screen, darker_blue, body_bottom)
        
        # 机翼（带倾斜效果）
        wing_y = self.y + self.height // 2
        # 左机翼
        left_wing = [
            (self.x, wing_y),
            (self.x - 12 - abs(self.tilt) * 0.5, wing_y + 8),
            (self.x - 8, wing_y + 12),
            (self.x, wing_y + 6),
        ]
        wing_color = (min(255, CYAN[0] + self.tilt * 2), CYAN[1], CYAN[2])
        pygame.draw.polygon(screen, wing_color, left_wing)
        
        # 右机翼
        right_wing = [
            (self.x + self.width, wing_y),
            (self.x + self.width + 12 + abs(self.tilt) * 0.5, wing_y + 8),
            (self.x + self.width + 8, wing_y + 12),
            (self.x + self.width, wing_y + 6),
        ]
        pygame.draw.polygon(screen, wing_color, right_wing)
        
        # 机翼装饰线
        pygame.draw.line(screen, (0, 200, 255), 
                        (self.x - 2, wing_y + 4), 
                        (self.x - 8, wing_y + 10), 2)
        pygame.draw.line(screen, (0, 200, 255), 
                        (self.x + self.width + 2, wing_y + 4), 
                        (self.x + self.width + 8, wing_y + 10), 2)
        
        # 驾驶舱（带高光效果）
        cockpit_x = int(center_x + self.tilt * 0.2)
        cockpit_y = self.y + 18
        pygame.draw.circle(screen, GOLD, (cockpit_x, cockpit_y), 9)
        pygame.draw.circle(screen, YELLOW, (cockpit_x, cockpit_y), 6)
        # 高光点
        pygame.draw.circle(screen, WHITE, (cockpit_x - 2, cockpit_y - 2), 2)
        
        # 飞机前端（更尖锐的设计）
        nose_points = [
            (center_x + self.tilt * 0.3, self.y + 5),
            (center_x + self.tilt * 0.5, self.y),
            (center_x - self.tilt * 0.5, self.y),
        ]
        pygame.draw.polygon(screen, (100, 150, 255), nose_points)

    def get_rect(self) -> pygame.Rect:
        """获取碰撞矩形"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class EnemyType(Enum):
    """敌机类型"""

    FAST = 1  # 快速型（红色）
    STRONG = 2  # 强韧型（橙色）
    BOSS = 3  # Boss型（紫色）


class Enemy:
    """敌机类"""

    def __init__(self, x: float, enemy_type: EnemyType, config: GameConfig):
        self.x = x
        self.y = -40
        self.type = enemy_type
        self.config = config

        # 根据类型设置属性
        if enemy_type == EnemyType.FAST:
            self.width = 40
            self.height = 35
            self.speed = config.enemy_speed * 1.5
            self.color = RED
            self.accent_color = PINK
            self.hp = config.enemy_hp
        elif enemy_type == EnemyType.STRONG:
            self.width = 50
            self.height = 45
            self.speed = config.enemy_speed * 0.8
            self.color = ORANGE
            self.accent_color = YELLOW
            self.hp = config.enemy_hp + 1
        else:  # BOSS
            self.width = 70
            self.height = 60
            self.speed = config.enemy_speed * 0.6
            self.color = PURPLE
            self.accent_color = MAGENTA
            self.hp = config.enemy_hp + 2

        self.max_hp = self.hp
        self.shoot_timer = 0.0  # 射击计时器
        self.shoot_interval = random.uniform(3.0, 5.0)  # 随机射击间隔（3-5秒）
        self.animation_frame = random.randint(0, 60)  # 随机动画帧（避免所有敌机同步）

    def update(self):
        """更新敌机位置和射击"""
        self.y += self.speed
        self.shoot_timer += 1 / FPS  # 更新射击计时器
        self.animation_frame += 1  # 更新动画帧

    def can_shoot(self) -> bool:
        """判断是否可以射击"""
        return self.shoot_timer >= self.shoot_interval

    def shoot(self) -> Bullet:
        """发射子弹"""
        if self.can_shoot():
            self.shoot_timer = 0.0  # 重置计时器
            self.shoot_interval = random.uniform(3.0, 5.0)  # 重新随机生成下次射击间隔
            return Bullet(
                self.x + self.width // 2 - 2.5,
                self.y + self.height,
                self.config.enemy_bullet_speed,
                False,  # 敌机子弹
            )
        return None

    def draw(self, screen):
        """绘制敌机（改进的动画设计）"""
        center_x = self.x + self.width // 2
        
        # 引擎火焰效果（敌机向下飞行，火焰在顶部）
        flame_intensity = 4 + int(2 * math.sin(self.animation_frame * 0.4))
        flame_y = self.y
        # 外层火焰
        flame_points_outer = [
            (center_x - 6, flame_y),
            (center_x - 4, flame_y - flame_intensity),
            (center_x, flame_y - flame_intensity - 2),
            (center_x + 4, flame_y - flame_intensity),
            (center_x + 6, flame_y),
        ]
        pygame.draw.polygon(screen, (255, 200, 0), flame_points_outer)
        # 内层火焰
        flame_points_inner = [
            (center_x - 4, flame_y),
            (center_x - 2, flame_y - flame_intensity + 1),
            (center_x, flame_y - flame_intensity),
            (center_x + 2, flame_y - flame_intensity + 1),
            (center_x + 4, flame_y),
        ]
        pygame.draw.polygon(screen, (255, 150, 0), flame_points_inner)
        
        # 敌机主体（更立体的设计）
        # 主体上部分
        body_top = [
            (self.x, self.y + self.height // 4),
            (center_x, self.y + self.height),
            (self.x + self.width, self.y + self.height // 4),
        ]
        pygame.draw.polygon(screen, self.color, body_top)
        
        # 主体下部分（较暗）
        body_bottom = [
            (self.x, self.y + self.height // 4),
            (center_x, self.y + self.height),
            (self.x + self.width, self.y + self.height // 4),
            (center_x, self.y),
        ]
        darker_color = (
            max(0, self.color[0] - 40),
            max(0, self.color[1] - 40),
            max(0, self.color[2] - 40),
        )
        pygame.draw.polygon(screen, darker_color, body_bottom)
        
        # 机翼（更详细的机翼设计）
        wing_y = self.y + self.height // 3
        # 左机翼
        left_wing = [
            (self.x, wing_y),
            (self.x - 12, self.y + 2),
            (self.x - 8, self.y),
            (self.x, self.y + 2),
        ]
        pygame.draw.polygon(screen, self.accent_color, left_wing)
        
        # 右机翼
        right_wing = [
            (self.x + self.width, wing_y),
            (self.x + self.width + 12, self.y + 2),
            (self.x + self.width + 8, self.y),
            (self.x + self.width, self.y + 2),
        ]
        pygame.draw.polygon(screen, self.accent_color, right_wing)
        
        # 机翼装饰线
        wing_line_color = (
            min(255, self.accent_color[0] + 50),
            min(255, self.accent_color[1] + 50),
            min(255, self.accent_color[2] + 50),
        )
        pygame.draw.line(screen, wing_line_color,
                        (self.x - 2, self.y + 1), 
                        (self.x - 8, self.y + 1), 2)
        pygame.draw.line(screen, wing_line_color,
                        (self.x + self.width + 2, self.y + 1), 
                        (self.x + self.width + 8, self.y + 1), 2)
        
        # 敌机前端（尖锐设计）
        nose_points = [
            (center_x, self.y),
            (center_x - 4, self.y + 8),
            (center_x + 4, self.y + 8),
        ]
        nose_color = (
            min(255, self.color[0] + 50), 
            min(255, self.color[1] + 50), 
            min(255, self.color[2] + 50)
        )
        pygame.draw.polygon(screen, nose_color, nose_points)

        # 如果有生命值，显示血条
        if self.hp < self.max_hp:
            bar_width = self.width
            bar_height = 5
            bar_x = self.x
            bar_y = self.y - 10

            # 背景（红色）
            pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
            # 当前生命值（绿色）
            hp_ratio = self.hp / self.max_hp
            pygame.draw.rect(
                screen, GREEN, (bar_x, bar_y, bar_width * hp_ratio, bar_height)
            )

    def get_rect(self) -> pygame.Rect:
        """获取碰撞矩形"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def is_past_player_line(self) -> bool:
        """判断是否越过玩家防线"""
        return self.y + self.height > PLAYER_Y

    def take_damage(self, damage: int = 1) -> bool:
        """受到伤害，返回是否被击毁"""
        self.hp -= damage
        return self.hp <= 0


class Game:
    """游戏主类"""

    def __init__(self, difficulty: Difficulty):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Fighter Battle")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.victory = False
        self.paused = False
        self.game_started = True
        self.pause_start_time = 0  # 暂停开始时间
        self.total_pause_time = 0  # 累计暂停时间

        global config
        config = GameConfig.from_difficulty(difficulty)

        # 创建三架飞机，并排显示
        plane_spacing = 70  # 三架飞机的间距
        center_x = SCREEN_WIDTH // 2
        self.players = [
            Player(center_x - plane_spacing - 25),  # 左飞机
            Player(center_x - 25),  # 中间飞机
            Player(center_x + plane_spacing - 25),  # 右飞机
        ]
        self.player = self.players[1]  # 主飞机（中间那架，用于UI显示和共享状态）
        self.enemies: List[Enemy] = []
        self.bullets: List[Bullet] = []
        self.powerups: List[PowerUp] = []

        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.enemy_spawn_timer = 0.0

        self.font_large = get_font(72)
        self.font_medium = get_font(48)
        self.font_small = get_font(36)

    def spawn_enemy(self):
        """生成敌机"""
        enemy_types = [EnemyType.FAST, EnemyType.STRONG]
        # 根据难度和游戏进度，增加BOSS出现的概率
        boss_probability = 0.15  # Default boss probability
        if config.difficulty == Difficulty.EASY:
            boss_probability = 0.05  # Lower boss probability in easy mode

        if random.random() < boss_probability:
            enemy_types.append(EnemyType.BOSS)

        enemy_type = random.choice(enemy_types)
        x = random.randint(0, SCREEN_WIDTH - 70)
        self.enemies.append(Enemy(x, enemy_type, config))

    def update(self, keys):
        """更新游戏状态"""
        if self.game_over:
            return

        # 暂停/继续功能
        # 注意：暂停逻辑在handle_events中处理

        if self.paused:
            return

        # 更新三架飞机（一起移动）
        # 计算主飞机的移动
        move_delta = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_delta = -self.players[0].speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_delta = self.players[0].speed

        # 更新三架飞机的位置，保持间距
        if move_delta != 0:
            new_x = self.players[0].x + move_delta
            # 限制在屏幕内
            plane_spacing = 70
            new_x = max(
                0, min(new_x, SCREEN_WIDTH - self.players[0].width - plane_spacing * 2)
            )
            # 更新三架飞机的位置
            self.players[0].x = new_x
            self.players[1].x = new_x + plane_spacing
            self.players[2].x = new_x + plane_spacing * 2

            # 确保所有飞机都在屏幕内
            if self.players[2].x + self.players[2].width > SCREEN_WIDTH:
                self.players[2].x = SCREEN_WIDTH - self.players[2].width
                self.players[1].x = self.players[2].x - plane_spacing
                self.players[0].x = self.players[1].x - plane_spacing

        # 更新射击冷却
        for player in self.players:
            if player.shoot_cooldown > 0:
                player.shoot_cooldown -= 1

        # 三架飞机都能射击
        if keys[pygame.K_SPACE]:
            for player in self.players:
                bullets = player.shoot()
                if bullets:
                    self.bullets.extend(bullets)

        # 生成敌机
        # 计算剩余时间
        if self.game_started and not self.paused:
            elapsed_time = (
                pygame.time.get_ticks() - self.start_time - self.total_pause_time
            ) / 1000.0
            remaining_time = max(0, GAME_DURATION - elapsed_time)
        else:
            if hasattr(self, "last_elapsed_time"):
                remaining_time = max(0, GAME_DURATION - self.last_elapsed_time)
            else:
                remaining_time = GAME_DURATION

        # 在最后10秒时，敌机生成频率提高（间隔缩短到原来的50%）
        spawn_rate = config.enemy_spawn_rate
        if remaining_time <= 10.0:
            spawn_rate = config.enemy_spawn_rate * 0.5  # 生成频率提高一倍

        self.enemy_spawn_timer += 1 / FPS
        if self.enemy_spawn_timer >= spawn_rate:
            self.enemy_spawn_timer = 0.0
            self.spawn_enemy()
            # 在最后10秒时，有30%概率额外生成一架敌机
            if remaining_time <= 10.0 and random.random() < 0.3:
                self.spawn_enemy()

        # 更新敌机
        for enemy in self.enemies[:]:
            enemy.update()
            # 敌机射击
            enemy_bullet = enemy.shoot()
            if enemy_bullet:
                self.bullets.append(enemy_bullet)
            # 检查是否越过防线
            if enemy.is_past_player_line():
                # 如果有防护盾，消耗一个防护盾并移除敌机（使用主飞机状态）
                if self.player.shield_count > 0:
                    self.player.shield_count -= 1
                    self.enemies.remove(enemy)
                else:
                    # 没有防护盾，游戏失败
                    self.game_over = True
                    self.victory = False
                    self.game_started = False  # 停止计时
                    break

        # 更新炮弹
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)

        # 更新道具
        for powerup in self.powerups[:]:
            powerup.update()
            if powerup.is_off_screen():
                self.powerups.remove(powerup)

        # 碰撞检测：玩家炮弹 vs 敌机
        for bullet in self.bullets[:]:
            if bullet.is_player:
                for enemy in self.enemies[:]:
                    if (
                        bullet.x < enemy.x + enemy.width
                        and bullet.x + bullet.width > enemy.x
                        and bullet.y < enemy.y + enemy.height
                        and bullet.y + bullet.height > enemy.y
                    ):
                        # 碰撞发生
                        self.bullets.remove(bullet)
                        # 根据玩家攻击力造成伤害
                        damage = self.player.attack_power
                        if enemy.take_damage(damage):
                            # 敌机被击毁，随机掉落道具（不同类型的道具）
                            if random.random() < 0.4:  # 40%概率掉落道具
                                # 随机选择道具类型
                                powerup_type = random.choice(list(PowerUpType))
                                powerup = PowerUp(
                                    enemy.x + enemy.width // 2 - 15,
                                    enemy.y + enemy.height,
                                    powerup_type,
                                )
                                self.powerups.append(powerup)
                            self.enemies.remove(enemy)
                            self.score += 10 * enemy.max_hp
                        break

        # 碰撞检测：敌机炮弹 vs 玩家飞机
        for bullet in self.bullets[:]:
            if not bullet.is_player:
                for player in self.players[:]:
                    player_rect = player.get_rect()
                    if (
                        bullet.x < player_rect.x + player_rect.width
                        and bullet.x + bullet.width > player_rect.x
                        and bullet.y < player_rect.y + player_rect.height
                        and bullet.y + bullet.height > player_rect.y
                    ):
                        # 碰撞发生，玩家受到伤害
                        self.bullets.remove(bullet)
                        player.hp -= 1
                        if player.hp <= 0:
                            # 如果主飞机被击毁，游戏失败
                            if player == self.player:
                                self.game_over = True
                                self.victory = False
                                self.game_started = False
                            else:
                                # 移除被击毁的飞机
                                self.players.remove(player)
                        break

        # 碰撞检测：玩家 vs 道具（三架飞机都可以拾取）
        for powerup in self.powerups[:]:
            picked_up = False
            for player in self.players:
                player_rect = player.get_rect()
                if player_rect.colliderect(powerup.get_rect()):
                    picked_up = True
                    break

            if picked_up:
                # 根据道具类型应用不同效果（共享到所有飞机）
                if powerup.type == PowerUpType.POWER_BOOST:
                    # 攻击力提升
                    for player in self.players:
                        player.attack_power += 1
                        if player.attack_power > 5:
                            player.attack_power = 5
                elif powerup.type == PowerUpType.HEALTH:
                    # 生命恢复（只恢复主飞机，或可以恢复所有？我觉得恢复主飞机就行）
                    self.player.hp = min(self.player.hp + 1, self.player.max_hp)
                elif powerup.type == PowerUpType.RAPID_FIRE:
                    # 快速射击
                    for player in self.players:
                        player.rapid_fire_count += 1
                        if player.rapid_fire_count > 3:
                            player.rapid_fire_count = 3
                elif powerup.type == PowerUpType.SHIELD:
                    # 防护盾
                    self.player.shield_count += 1
                    if self.player.shield_count > 3:
                        self.player.shield_count = 3
                elif powerup.type == PowerUpType.MULTI_SHOT:
                    # 多发子弹
                    for player in self.players:
                        player.multi_shot_count += 1
                        if player.multi_shot_count > 3:
                            player.multi_shot_count = 3

                self.powerups.remove(powerup)

        # 检查时间是否到达（只在游戏进行中计时）
        if self.game_started:
            elapsed_time = (
                pygame.time.get_ticks() - self.start_time - self.total_pause_time
            ) / 1000.0
            if elapsed_time >= GAME_DURATION:
                self.game_over = True
                self.victory = True
                self.game_started = False

    def draw(self):
        """绘制游戏画面"""
        # 背景（深色渐变效果）
        self.screen.fill((20, 20, 40))
        for i in range(SCREEN_HEIGHT):
            color_value = int(20 + (i / SCREEN_HEIGHT) * 20)
            pygame.draw.line(
                self.screen,
                (color_value, color_value, color_value + 20),
                (0, i),
                (SCREEN_WIDTH, i),
            )

        # 绘制三架飞机
        for player in self.players:
            player.draw(self.screen)

        # 绘制敌机
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # 绘制炮弹
        for bullet in self.bullets:
            bullet.draw(self.screen)

        # 绘制道具
        for powerup in self.powerups:
            powerup.draw(self.screen)

        # 绘制UI
        # 只在游戏进行中计时
        if self.game_started and not self.paused:
            elapsed_time = (
                pygame.time.get_ticks() - self.start_time - self.total_pause_time
            ) / 1000.0
        else:
            # 游戏结束或暂停时，使用最后的时间
            if hasattr(self, "last_elapsed_time"):
                elapsed_time = self.last_elapsed_time
            else:
                elapsed_time = (
                    pygame.time.get_ticks() - self.start_time - self.total_pause_time
                ) / 1000.0
                self.last_elapsed_time = elapsed_time

        remaining_time = max(0, GAME_DURATION - elapsed_time)

        # Score
        score_text = self.font_small.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Countdown
        time_text = self.font_small.render(f"Time: {remaining_time:.1f}s", True, WHITE)
        self.screen.blit(time_text, (10, 50))

        # Player HP
        hp_text = self.font_small.render(f"HP: {self.player.hp}", True, GREEN)
        self.screen.blit(hp_text, (SCREEN_WIDTH - 200, 10))

        # Attack Power (always show)
        power_text = self.font_small.render(
            f"Power: x{self.player.attack_power}", True, CYAN
        )
        self.screen.blit(power_text, (SCREEN_WIDTH - 200, 50))

        # Power-ups display (show all active power-ups)
        y_offset = 90
        # Power Boost (always show if > 1, but we show it as Power above)
        # Rapid Fire
        if self.player.rapid_fire_count > 0:
            rapid_text = self.font_small.render(
                f"Rapid: {self.player.rapid_fire_count}", True, RED
            )
            self.screen.blit(rapid_text, (SCREEN_WIDTH - 200, y_offset))
            y_offset += 30

        # Shield
        if self.player.shield_count > 0:
            shield_text = self.font_small.render(
                f"Shield: {self.player.shield_count}", True, BLUE
            )
            self.screen.blit(shield_text, (SCREEN_WIDTH - 200, y_offset))
            y_offset += 30

        # Multi Shot
        if self.player.multi_shot_count > 0:
            multi_text = self.font_small.render(
                f"Multi: {self.player.multi_shot_count}", True, PURPLE
            )
            self.screen.blit(multi_text, (SCREEN_WIDTH - 200, y_offset))
            y_offset += 30

        # Pause indicator
        if self.paused:
            pause_text = self.font_medium.render("PAUSED", True, YELLOW)
            pause_rect = pause_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            )
            self.screen.blit(pause_text, pause_rect)
            instruction_text = self.font_small.render("Press P to resume", True, WHITE)
            inst_rect = instruction_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            )
            self.screen.blit(instruction_text, inst_rect)

        # 游戏结束画面
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            if self.victory:
                text = self.font_large.render("VICTORY!", True, GREEN)
            else:
                text = self.font_large.render("DEFEAT!", True, RED)

            text_rect = text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            )
            self.screen.blit(text, text_rect)

            score_display = self.font_medium.render(
                f"Final Score: {self.score}", True, YELLOW
            )
            score_rect = score_display.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)
            )
            self.screen.blit(score_display, score_rect)

            restart_text = self.font_small.render(
                "Press R to restart, ESC to exit", True, WHITE
            )
            restart_rect = restart_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)
            )
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if self.game_over and event.key == pygame.K_r:
                    self.restart()
                # 暂停/继续功能
                if event.key == pygame.K_p and not self.game_over:
                    if self.paused:
                        # 恢复游戏
                        self.total_pause_time += (
                            pygame.time.get_ticks() - self.pause_start_time
                        )
                        self.paused = False
                    else:
                        # 暂停游戏
                        self.pause_start_time = pygame.time.get_ticks()
                        self.paused = True
                        # 保存当前时间
                        if self.game_started:
                            self.last_elapsed_time = (
                                pygame.time.get_ticks()
                                - self.start_time
                                - self.total_pause_time
                            ) / 1000.0

    def restart(self):
        """重新开始游戏"""
        self.game_over = False
        self.victory = False
        self.paused = False
        self.game_started = True
        self.pause_start_time = 0
        self.total_pause_time = 0
        # 创建三架飞机，并排显示
        plane_spacing = 70
        center_x = SCREEN_WIDTH // 2
        self.players = [
            Player(center_x - plane_spacing - 25),  # 左飞机
            Player(center_x - 25),  # 中间飞机
            Player(center_x + plane_spacing - 25),  # 右飞机
        ]
        self.player = self.players[1]  # 主飞机（中间那架）
        self.enemies = []
        self.bullets = []
        self.powerups = []
        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.enemy_spawn_timer = 0.0
        if hasattr(self, "last_elapsed_time"):
            delattr(self, "last_elapsed_time")

    def run(self):
        """运行游戏主循环"""
        while self.running:
            keys = pygame.key.get_pressed()
            self.handle_events()
            self.update(keys)
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


def show_menu(screen, clock):
    """Show main menu"""
    font_title = get_font(96)
    font_option = get_font(64)
    font_small = get_font(36)

    selected = 0  # 0: Easy, 1: Medium, 2: Hard

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % 3
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % 3
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
                    return difficulties[selected]

        # 绘制菜单
        screen.fill((10, 10, 30))

        # Title
        title = font_title.render("FIGHTER BATTLE", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title, title_rect)

        # Difficulty options
        difficulties = [
            ("Easy Mode", GREEN),
            ("Medium Mode", YELLOW),
            ("Hard Mode", RED),
        ]

        for i, (text, color) in enumerate(difficulties):
            if i == selected:
                text_surface = font_option.render(f"> {text} <", True, color)
            else:
                text_surface = font_option.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 250 + i * 80))
            screen.blit(text_surface, text_rect)

        # Instructions
        instruction = font_small.render(
            "Use UP/DOWN to select, ENTER to confirm", True, WHITE
        )
        inst_rect = instruction.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        )
        screen.blit(instruction, inst_rect)

        controls = font_small.render(
            "Controls: LEFT/RIGHT to move, SPACE to shoot", True, CYAN
        )
        ctrl_rect = controls.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(controls, ctrl_rect)

        pygame.display.flip()
        clock.tick(FPS)


def main():
    """Main function"""
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Fighter Battle")
    clock = pygame.time.Clock()

    while True:
        difficulty = show_menu(screen, clock)
        if difficulty is None:
            break

        game = Game(difficulty)
        game.run()

        # 游戏结束后返回菜单
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        clock = pygame.time.Clock()


if __name__ == "__main__":
    main()
