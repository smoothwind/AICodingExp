"""
增强版俄罗斯方块游戏
包含音效、特殊效果、高分榜等高级功能
"""

import pygame
import random
import sys
import json
import os
from datetime import datetime
from enum import Enum

# 初始化Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# 游戏常量
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30
BOARD_X = 50
BOARD_Y = 50

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
GOLD = (255, 215, 0)

# 特效颜色
GHOST_COLOR = (100, 100, 100, 128)
FLASH_COLOR = (255, 255, 255)

# 俄罗斯方块形状定义
SHAPES = [
    # I型
    [[1, 1, 1, 1]],

    # O型
    [[1, 1],
     [1, 1]],

    # T型
    [[0, 1, 0],
     [1, 1, 1]],

    # S型
    [[0, 1, 1],
     [1, 1, 0]],

    # Z型
    [[1, 1, 0],
     [0, 1, 1]],

    # J型
    [[1, 0, 0],
     [1, 1, 1]],

    # L型
    [[0, 0, 1],
     [1, 1, 1]]
]

COLORS = [CYAN, YELLOW, PURPLE, GREEN, RED, BLUE, ORANGE]

class GameMode(Enum):
    """游戏模式"""
    CLASSIC = "经典模式"
    SPRINT = "冲刺模式(40行)"
    MARATHON = "马拉松模式"

class GameState(Enum):
    """游戏状态"""
    MENU = "菜单"
    PLAYING = "游戏中"
    PAUSED = "暂停"
    GAME_OVER = "游戏结束"
    HIGH_SCORES = "高分榜"

class Particle:
    """粒子效果类"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.color = color
        self.life = 1.0
        self.gravity = 0.2

    def update(self, dt):
        self.x += self.vx * dt / 16
        self.y += self.vy * dt / 16
        self.vy += self.gravity * dt / 16
        self.life -= dt / 500

    def draw(self, screen):
        if self.life > 0:
            alpha = int(self.life * 255)
            color = (*self.color[:3], alpha) if len(self.color) == 3 else self.color
            size = int(3 * self.life)
            pygame.draw.circle(screen, color[:3], (int(self.x), int(self.y)), max(1, size))

class EnhancedTetrisPiece:
    """增强版俄罗斯方块类"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.shape_index = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_index]
        self.color = COLORS[self.shape_index]
        self.rotation = 0
        self.lock_delay = 0
        self.max_lock_delay = 500  # 毫秒

    def get_rotated_shape(self):
        """获取旋转后的形状"""
        if self.shape_index == 1:  # O型不需要旋转
            return self.shape

        rotated = []
        for i in range(len(self.shape[0])):
            row = []
            for j in range(len(self.shape) - 1, -1, -1):
                row.append(self.shape[j][i])
            rotated.append(row)

        return rotated

    def get_kick_data(self, rotation_state):
        """获取墙踢数据"""
        # 简化的墙踢数据
        kicks = {
            0: [(0, 0), (-1, 0), (1, 0), (0, -1)],
            1: [(0, 0), (1, 0), (-1, 0), (0, 1)],
            2: [(0, 0), (1, 0), (-1, 0), (0, -1)],
            3: [(0, 0), (-1, 0), (1, 0), (0, 1)]
        }
        return kicks.get(rotation_state, [(0, 0)])

class SoundManager:
    """音效管理器"""
    def __init__(self):
        self.sounds = {}
        self.enabled = True
        self.create_sounds()

    def create_sounds(self):
        """创建音效"""
        try:
            # 创建简单的音效
            sample_rate = 22050
            duration = 0.1

            # 移动音效
            self.sounds['move'] = self.create_beep(440, duration)
            # 旋转音效
            self.sounds['rotate'] = self.create_beep(660, duration)
            # 落地音效
            self.sounds['lock'] = self.create_beep(220, duration * 2)
            # 消除行音效
            self.sounds['clear'] = self.create_beep(880, duration * 3)
            # 游戏结束音效
            self.sounds['game_over'] = self.create_beep(110, duration * 4)
        except:
            self.enabled = False

    def create_beep(self, frequency, duration):
        """创建蜂鸣声"""
        sample_rate = 22050
        samples = int(sample_rate * duration)
        waves = []
        for i in range(samples):
            value = int(32767 * (i % 100) / 100.0)
            waves.append([value, value])
        return pygame.sndarray.make_sound(waves)

    def play(self, sound_name):
        """播放音效"""
        if self.enabled and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                pass

class HighScoreManager:
    """高分榜管理器"""
    def __init__(self):
        self.filename = "tetris_highscores.json"
        self.scores = self.load_scores()

    def load_scores(self):
        """加载高分榜"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_scores(self):
        """保存高分榜"""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.scores, f, indent=2)
        except:
            pass

    def add_score(self, name, score, mode, lines_cleared, level):
        """添加高分"""
        entry = {
            'name': name,
            'score': score,
            'mode': mode.value,
            'lines_cleared': lines_cleared,
            'level': level,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        self.scores.append(entry)
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        self.scores = self.scores[:10]  # 只保留前10名
        self.save_scores()

    def get_top_scores(self, mode=None, limit=10):
        """获取高分榜"""
        scores = self.scores
        if mode:
            scores = [s for s in scores if s['mode'] == mode.value]
        return scores[:limit]

class EnhancedTetrisGame:
    """增强版俄罗斯方块游戏"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("增强版俄罗斯方块")
        self.clock = pygame.time.Clock()

        # 字体
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 48)
        self.font_huge = pygame.font.Font(None, 72)

        # 游戏组件
        self.sound_manager = SoundManager()
        self.high_score_manager = HighScoreManager()

        # 游戏状态
        self.reset_game()
        self.state = GameState.MENU
        self.game_mode = GameMode.CLASSIC
        self.particles = []
        self.flash_lines = []
        self.flash_timer = 0

        # 菜单选项
        self.menu_options = [
            "经典模式",
            "冲刺模式 (40行)",
            "马拉松模式",
            "高分榜",
            "退出游戏"
        ]
        self.selected_menu = 0

    def reset_game(self):
        """重置游戏"""
        self.board = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.hold_piece = None
        self.can_hold = True

        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.combo = 0
        self.back_to_back = 0

        self.game_time = 0
        self.fall_time = 0
        self.fall_speed = 1000  # 毫秒

        self.game_over = False
        self.paused = False
        self.particles = []

    def new_piece(self):
        """创建新的俄罗斯方块"""
        piece = EnhancedTetrisPiece(GRID_WIDTH // 2 - 1, 0)
        return piece

    def is_valid_position(self, piece, dx=0, dy=0, rotation=None):
        """检查方块位置是否有效"""
        shape = rotation if rotation else piece.shape

        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece.x + x + dx
                    new_y = piece.y + y + dy

                    # 检查边界
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return False

                    # 检查碰撞
                    if new_y >= 0 and self.board[new_y][new_x] != BLACK:
                        return False

        return True

    def lock_piece(self, piece):
        """锁定方块到游戏板"""
        shape = piece.shape
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell and piece.y + y >= 0:
                    self.board[piece.y + y][piece.x + x] = piece.color

    def clear_lines(self):
        """清除完整的行"""
        lines_to_clear = []

        for y in range(GRID_HEIGHT):
            if all(cell != BLACK for cell in self.board[y]):
                lines_to_clear.append(y)

        if lines_to_clear:
            # 添加闪烁效果
            self.flash_lines = lines_to_clear.copy()
            self.flash_timer = 300  # 闪烁300毫秒

            # 创建粒子效果
            for y in lines_to_clear:
                for x in range(GRID_WIDTH):
                    cell_x = BOARD_X + x * CELL_SIZE + CELL_SIZE // 2
                    cell_y = BOARD_Y + y * CELL_SIZE + CELL_SIZE // 2
                    for _ in range(5):
                        self.particles.append(Particle(cell_x, cell_y, self.board[y][x]))

            # 消除行
            for y in lines_to_clear:
                del self.board[y]
                self.board.insert(0, [BLACK for _ in range(GRID_WIDTH)])

            lines_cleared = len(lines_to_clear)
            self.lines_cleared += lines_cleared

            # 计算分数
            self.calculate_score(lines_cleared)

            # 播放音效
            self.sound_manager.play('clear')

            return lines_cleared

        return 0

    def calculate_score(self, lines_cleared):
        """计算分数"""
        base_scores = [0, 100, 300, 500, 800]
        score_multiplier = self.level

        # 连击奖励
        if lines_cleared >= 4:  # Tetris
            self.back_to_back += 1
            if self.back_to_back > 1:
                score_multiplier *= 1.5
        else:
            self.back_to_back = 0

        # 连续消除奖励
        if lines_cleared > 0:
            self.combo += 1
            combo_bonus = min(50 * self.combo, 200)
        else:
            self.combo = 0
            combo_bonus = 0

        # 计算总分
        points = base_scores[lines_cleared] * score_multiplier + combo_bonus
        self.score += int(points)

        # 更新等级
        if self.game_mode == GameMode.CLASSIC:
            self.level = self.lines_cleared // 10 + 1
        elif self.game_mode == GameMode.SPRINT:
            self.level = 1
            self.fall_speed = 500  # 冲刺模式固定速度
        elif self.game_mode == GameMode.MARATHON:
            self.level = min(15, self.lines_cleared // 15 + 1)

        # 更新下落速度
        if self.game_mode == GameMode.CLASSIC or self.game_mode == GameMode.MARATHON:
            self.fall_speed = max(50, 1000 - (self.level - 1) * 60)

    def move_piece(self, dx, dy):
        """移动方块"""
        if self.is_valid_position(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy

            if dy > 0:
                self.current_piece.lock_delay = 0
            else:
                self.sound_manager.play('move')

            return True
        elif dy > 0:
            # 尝试锁定
            self.current_piece.lock_delay += self.clock.get_time()
            if self.current_piece.lock_delay >= self.current_piece.max_lock_delay:
                self.lock_current_piece()
                return False

        return False

    def rotate_piece(self):
        """旋转方块"""
        rotated_shape = self.current_piece.get_rotated_shape()

        # 尝试旋转
        if self.is_valid_position(self.current_piece, rotation=rotated_shape):
            self.current_piece.shape = rotated_shape
            self.sound_manager.play('rotate')
            return True

        # 尝试墙踢
        kick_data = self.current_piece.get_kick_data(self.current_piece.rotation)
        for dx, dy in kick_data:
            if self.is_valid_position(self.current_piece, dx, dy, rotated_shape):
                self.current_piece.x += dx
                self.current_piece.y += dy
                self.current_piece.shape = rotated_shape
                self.sound_manager.play('rotate')
                return True

        return False

    def hold_piece(self):
        """保留方块"""
        if self.can_hold:
            if self.hold_piece is None:
                self.hold_piece = EnhancedTetrisPiece(GRID_WIDTH // 2 - 1, 0)
                self.hold_piece.shape_index = self.current_piece.shape_index
                self.hold_piece.shape = self.current_piece.shape
                self.hold_piece.color = self.current_piece.color
                self.current_piece = self.next_piece
                self.next_piece = self.new_piece()
            else:
                # 交换当前方块和保留方块
                temp_index = self.current_piece.shape_index
                temp_shape = self.current_piece.shape
                temp_color = self.current_piece.color

                self.current_piece.shape_index = self.hold_piece.shape_index
                self.current_piece.shape = self.hold_piece.shape
                self.current_piece.color = self.hold_piece.color

                self.hold_piece.shape_index = temp_index
                self.hold_piece.shape = temp_shape
                self.hold_piece.color = temp_color

            self.can_hold = False
            return True

        return False

    def hard_drop(self):
        """硬降落"""
        drop_distance = 0
        while self.is_valid_position(self.current_piece, dy=1):
            self.current_piece.y += 1
            drop_distance += 1

        self.score += drop_distance * 2
        self.lock_current_piece()
        self.sound_manager.play('lock')

    def lock_current_piece(self):
        """锁定当前方块"""
        self.lock_piece(self.current_piece)
        lines_cleared = self.clear_lines()

        # 检查游戏模式结束条件
        if self.game_mode == GameMode.SPRINT and self.lines_cleared >= 40:
            self.game_over = True
            self.on_game_complete()
        elif not self.is_valid_position(self.next_piece):
            self.game_over = True
            self.on_game_over()
        else:
            self.current_piece = self.next_piece
            self.next_piece = self.new_piece()
            self.can_hold = True

    def on_game_complete(self):
        """游戏完成"""
        self.sound_manager.play('game_over')

    def on_game_over(self):
        """游戏结束"""
        self.sound_manager.play('game_over')

        # 保存高分
        if self.score > 0:
            name = f"Player{random.randint(1000, 9999)}"
            self.high_score_manager.add_score(
                name, self.score, self.game_mode,
                self.lines_cleared, self.level
            )

    def get_ghost_position(self):
        """获取幽灵方块位置"""
        ghost_y = self.current_piece.y
        while self.is_valid_position(self.current_piece, dy=ghost_y - self.current_piece.y + 1):
            ghost_y += 1
        return ghost_y

    def update(self, dt):
        """更新游戏状态"""
        if self.state == GameState.PLAYING and not self.paused:
            self.game_time += dt
            self.fall_time += dt

            # 更新粒子
            self.particles = [p for p in self.particles if p.life > 0]
            for particle in self.particles:
                particle.update(dt)

            # 更新闪烁效果
            if self.flash_timer > 0:
                self.flash_timer -= dt
                if self.flash_timer <= 0:
                    self.flash_lines = []

            # 自动下落
            if self.fall_time >= self.fall_speed:
                self.fall_time = 0
                if not self.move_piece(0, 1):
                    self.lock_current_piece()

    def draw_board(self):
        """绘制游戏板"""
        # 绘制背景
        board_rect = pygame.Rect(BOARD_X - 2, BOARD_Y - 2,
                                 GRID_WIDTH * CELL_SIZE + 4,
                                 GRID_HEIGHT * CELL_SIZE + 4)
        pygame.draw.rect(self.screen, WHITE, board_rect, 2)

        # 绘制网格和已锁定的方块
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell_x = BOARD_X + x * CELL_SIZE
                cell_y = BOARD_Y + y * CELL_SIZE

                # 闪烁效果
                if y in self.flash_lines and self.flash_timer > 0:
                    if self.flash_timer % 100 < 50:  # 闪烁间隔
                        color = FLASH_COLOR
                    else:
                        color = self.board[y][x] if self.board[y][x] != BLACK else BLACK
                else:
                    color = self.board[y][x]

                # 绘制方块
                if color != BLACK:
                    pygame.draw.rect(self.screen, color,
                                   (cell_x, cell_y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, WHITE,
                                   (cell_x, cell_y, CELL_SIZE, CELL_SIZE), 1)
                else:
                    # 绘制网格线
                    pygame.draw.rect(self.screen, DARK_GRAY,
                                   (cell_x, cell_y, CELL_SIZE, CELL_SIZE), 1)

    def draw_ghost_piece(self):
        """绘制幽灵方块"""
        ghost_y = self.get_ghost_position()
        shape = self.current_piece.shape

        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    cell_x = BOARD_X + (self.current_piece.x + x) * CELL_SIZE
                    cell_y = BOARD_Y + (ghost_y + y) * CELL_SIZE

                    # 绘制半透明幽灵方块
                    ghost_surface = pygame.Surface((CELL_SIZE, CELL_SIZE))
                    ghost_surface.set_alpha(128)
                    ghost_surface.fill(GRAY)
                    self.screen.blit(ghost_surface, (cell_x, cell_y))
                    pygame.draw.rect(self.screen, DARK_GRAY,
                                   (cell_x, cell_y, CELL_SIZE, CELL_SIZE), 1)

    def draw_piece(self, piece, ghost=False):
        """绘制方块"""
        shape = piece.shape
        color = piece.color

        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    cell_x = BOARD_X + (piece.x + x) * CELL_SIZE
                    cell_y = BOARD_Y + (piece.y + y) * CELL_SIZE

                    if ghost:
                        # 绘制半透明版本
                        piece_surface = pygame.Surface((CELL_SIZE, CELL_SIZE))
                        piece_surface.set_alpha(100)
                        piece_surface.fill(color)
                        self.screen.blit(piece_surface, (cell_x, cell_y))
                    else:
                        # 绘制正常方块
                        pygame.draw.rect(self.screen, color,
                                       (cell_x, cell_y, CELL_SIZE, CELL_SIZE))

                        # 绘制高光效果
                        highlight_rect = pygame.Rect(cell_x + 2, cell_y + 2,
                                                   CELL_SIZE - 4, 4)
                        highlight_color = tuple(min(255, c + 50) for c in color)
                        pygame.draw.rect(self.screen, highlight_color, highlight_rect)

                        pygame.draw.rect(self.screen, WHITE,
                                       (cell_x, cell_y, CELL_SIZE, CELL_SIZE), 1)

    def draw_next_piece(self):
        """绘制下一个方块预览"""
        next_x = BOARD_X + GRID_WIDTH * CELL_SIZE + 50
        next_y = BOARD_Y + 50

        # 绘制预览框
        preview_rect = pygame.Rect(next_x - 2, next_y - 2, 4 * CELL_SIZE, 4 * CELL_SIZE)
        pygame.draw.rect(self.screen, WHITE, preview_rect, 2)

        # 绘制"NEXT"文字
        next_text = self.font_medium.render("NEXT", True, WHITE)
        text_rect = next_text.get_rect(centerx=next_x + 2 * CELL_SIZE, y=next_y - 30)
        self.screen.blit(next_text, text_rect)

        # 绘制下一个方块
        shape = self.next_piece.shape
        offset_x = (4 - len(shape[0])) // 2
        offset_y = (4 - len(shape)) // 2

        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    cell_x = next_x + (offset_x + x) * CELL_SIZE
                    cell_y = next_y + (offset_y + y) * CELL_SIZE
                    pygame.draw.rect(self.screen, self.next_piece.color,
                                   (cell_x, cell_y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, WHITE,
                                   (cell_x, cell_y, CELL_SIZE, CELL_SIZE), 1)

    def draw_hold_piece(self):
        """绘制保留方块"""
        hold_x = BOARD_X + GRID_WIDTH * CELL_SIZE + 50
        hold_y = BOARD_Y + 250

        # 绘制保留框
        hold_rect = pygame.Rect(hold_x - 2, hold_y - 2, 4 * CELL_SIZE, 4 * CELL_SIZE)
        color = WHITE if self.can_hold else GRAY
        pygame.draw.rect(self.screen, color, hold_rect, 2)

        # 绘制"HOLD"文字
        hold_text = self.font_medium.render("HOLD", True, color)
        text_rect = hold_text.get_rect(centerx=hold_x + 2 * CELL_SIZE, y=hold_y - 30)
        self.screen.blit(hold_text, text_rect)

        # 绘制保留方块
        if self.hold_piece:
            shape = self.hold_piece.shape
            offset_x = (4 - len(shape[0])) // 2
            offset_y = (4 - len(shape)) // 2

            for y, row in enumerate(shape):
                for x, cell in enumerate(row):
                    if cell:
                        cell_x = hold_x + (offset_x + x) * CELL_SIZE
                        cell_y = hold_y + (offset_y + y) * CELL_SIZE
                        pygame.draw.rect(self.screen, self.hold_piece.color,
                                       (cell_x, cell_y, CELL_SIZE, CELL_SIZE))
                        pygame.draw.rect(self.screen, GRAY,
                                       (cell_x, cell_y, CELL_SIZE, CELL_SIZE), 1)

    def draw_stats(self):
        """绘制游戏统计"""
        stats_x = BOARD_X + GRID_WIDTH * CELL_SIZE + 50
        stats_y = BOARD_Y + 450

        # 标题
        stats_title = self.font_medium.render("STATISTICS", True, WHITE)
        self.screen.blit(stats_title, (stats_x, stats_y))

        # 统计信息
        stats = [
            f"SCORE: {self.score:,}",
            f"LINES: {self.lines_cleared}",
            f"LEVEL: {self.level}",
            f"TIME: {self.game_time // 1000 // 60:02d}:{self.game_time // 1000 % 60:02d}"
        ]

        if self.combo > 1:
            stats.append(f"COMBO: x{self.combo}")
        if self.back_to_back > 1:
            stats.append(f"BACK-TO-BACK: x{self.back_to_back}")

        for i, stat in enumerate(stats):
            stat_text = self.font_small.render(stat, True, WHITE)
            self.screen.blit(stat_text, (stats_x, stats_y + 40 + i * 25))

    def draw_controls(self):
        """绘制控制说明"""
        controls_x = BOARD_X + GRID_WIDTH * CELL_SIZE + 250
        controls_y = BOARD_Y + 50

        # 标题
        controls_title = self.font_medium.render("CONTROLS", True, WHITE)
        self.screen.blit(controls_title, (controls_x, controls_y))

        # 控制说明
        controls = [
            "← → : Move",
            "↓ : Soft Drop",
            "↑ : Rotate",
            "Space: Hard Drop",
            "C : Hold",
            "P : Pause",
            "R : Restart",
            "ESC : Menu"
        ]

        for i, control in enumerate(controls):
            control_text = self.font_small.render(control, True, LIGHT_GRAY)
            self.screen.blit(control_text, (controls_x, controls_y + 40 + i * 25))

    def draw_menu(self):
        """绘制主菜单"""
        # 背景
        self.screen.fill(BLACK)

        # 标题
        title_text = self.font_huge.render("TETRIS", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)

        subtitle_text = self.font_medium.render("Enhanced Edition", True, GOLD)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(subtitle_text, subtitle_rect)

        # 菜单选项
        for i, option in enumerate(self.menu_options):
            color = GOLD if i == self.selected_menu else WHITE
            option_text = self.font_large.render(option, True, color)
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, 320 + i * 60))
            self.screen.blit(option_text, option_rect)

        # 说明
        info_text = self.font_small.render("Use ↑↓ to select, ENTER to confirm", True, LIGHT_GRAY)
        info_rect = info_text.get_rect(center=(SCREEN_WIDTH // 2, 550))
        self.screen.blit(info_text, info_rect)

    def draw_high_scores(self):
        """绘制高分榜"""
        self.screen.fill(BLACK)

        # 标题
        title_text = self.font_huge.render("HIGH SCORES", True, GOLD)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)

        # 获取高分
        scores = self.high_score_manager.get_top_scores(limit=10)

        # 表头
        headers = ["Rank", "Name", "Score", "Mode", "Lines", "Date"]
        header_x = [150, 250, 400, 500, 600, 700]

        for header, x in zip(headers, header_x):
            header_text = self.font_small.render(header, True, LIGHT_GRAY)
            self.screen.blit(header_text, (x, 150))

        # 分数列表
        for i, score_data in enumerate(scores):
            y = 180 + i * 30
            color = GOLD if i < 3 else WHITE

            rank_text = self.font_small.render(f"#{i+1}", True, color)
            self.screen.blit(rank_text, (header_x[0], y))

            name_text = self.font_small.render(score_data['name'], True, color)
            self.screen.blit(name_text, (header_x[1], y))

            score_text = self.font_small.render(f"{score_data['score']:,}", True, color)
            self.screen.blit(score_text, (header_x[2], y))

            mode_text = self.font_small.render(score_data['mode'][:8], True, color)
            self.screen.blit(mode_text, (header_x[3], y))

            lines_text = self.font_small.render(str(score_data['lines_cleared']), True, color)
            self.screen.blit(lines_text, (header_x[4], y))

            date_text = self.font_small.render(score_data['date'][:8], True, color)
            self.screen.blit(date_text, (header_x[5], y))

        # 返回提示
        back_text = self.font_small.render("Press ESC to return to menu", True, LIGHT_GRAY)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, 550))
        self.screen.blit(back_text, back_rect)

    def draw_game_over(self):
        """绘制游戏结束画面"""
        # 半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # 游戏结束文字
        game_over_text = self.font_huge.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(game_over_text, text_rect)

        # 最终分数
        score_text = self.font_large.render(f"Final Score: {self.score:,}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 280))
        self.screen.blit(score_text, score_rect)

        # 统计信息
        stats = [
            f"Lines Cleared: {self.lines_cleared}",
            f"Level Reached: {self.level}",
            f"Time Played: {self.game_time // 1000 // 60:02d}:{self.game_time // 1000 % 60:02d}"
        ]

        for i, stat in enumerate(stats):
            stat_text = self.font_medium.render(stat, True, LIGHT_GRAY)
            stat_rect = stat_text.get_rect(center=(SCREEN_WIDTH // 2, 340 + i * 40))
            self.screen.blit(stat_text, stat_rect)

        # 重新开始提示
        restart_text = self.font_medium.render("Press ENTER to play again or ESC for menu", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, 480))
        self.screen.blit(restart_text, restart_rect)

    def draw_paused(self):
        """绘制暂停画面"""
        # 半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # 暂停文字
        paused_text = self.font_huge.render("PAUSED", True, YELLOW)
        text_rect = paused_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(paused_text, text_rect)

        # 继续提示
        continue_text = self.font_medium.render("Press P to Continue", True, WHITE)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(continue_text, continue_rect)

    def draw(self):
        """绘制游戏画面"""
        self.screen.fill(BLACK)

        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.HIGH_SCORES:
            self.draw_high_scores()
        else:
            # 游戏画面
            self.draw_board()

            if not self.game_over:
                self.draw_ghost_piece()
                self.draw_piece(self.current_piece)
                self.draw_next_piece()
                self.draw_hold_piece()
                self.draw_stats()
                self.draw_controls()

            # 绘制粒子效果
            for particle in self.particles:
                particle.draw(self.screen)

            # 游戏状态覆盖层
            if self.game_over:
                self.draw_game_over()
            elif self.paused:
                self.draw_paused()

        pygame.display.flip()

    def handle_menu_input(self, event):
        """处理菜单输入"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_menu = (self.selected_menu - 1) % len(self.menu_options)
            elif event.key == pygame.K_DOWN:
                self.selected_menu = (self.selected_menu + 1) % len(self.menu_options)
            elif event.key == pygame.K_RETURN:
                if self.selected_menu == 0:  # 经典模式
                    self.game_mode = GameMode.CLASSIC
                    self.reset_game()
                    self.state = GameState.PLAYING
                elif self.selected_menu == 1:  # 冲刺模式
                    self.game_mode = GameMode.SPRINT
                    self.reset_game()
                    self.state = GameState.PLAYING
                elif self.selected_menu == 2:  # 马拉松模式
                    self.game_mode = GameMode.MARATHON
                    self.reset_game()
                    self.state = GameState.PLAYING
                elif self.selected_menu == 3:  # 高分榜
                    self.state = GameState.HIGH_SCORES
                elif self.selected_menu == 4:  # 退出
                    return False
        return True

    def handle_game_input(self, event):
        """处理游戏输入"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.MENU
            elif event.key == pygame.K_p:
                self.paused = not self.paused
            elif event.key == pygame.K_r:
                self.reset_game()
            elif not self.game_over and not self.paused:
                if event.key == pygame.K_LEFT:
                    self.move_piece(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.move_piece(1, 0)
                elif event.key == pygame.K_DOWN:
                    if self.move_piece(0, 1):
                        self.score += 1
                elif event.key == pygame.K_UP:
                    self.rotate_piece()
                elif event.key == pygame.K_SPACE:
                    self.hard_drop()
                elif event.key == pygame.K_c:
                    self.hold_piece()
            elif self.game_over:
                if event.key == pygame.K_RETURN:
                    self.reset_game()
                    self.state = GameState.PLAYING
        return True

    def handle_input(self):
        """处理用户输入"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if self.state == GameState.MENU:
                return self.handle_menu_input(event)
            elif self.state == GameState.HIGH_SCORES:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU
            else:
                return self.handle_game_input(event)

        return True

    def run(self):
        """运行游戏主循环"""
        running = True

        while running:
            dt = self.clock.tick(60)  # 60 FPS

            running = self.handle_input()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()

def main():
    """主函数"""
    game = EnhancedTetrisGame()
    game.run()

if __name__ == "__main__":
    main()