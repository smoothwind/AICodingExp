"""
俄罗斯方块游戏 - 完整实现
作者: AI Assistant
使用: Pygame 库
"""

import pygame
import random
import sys

# 初始化Pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
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

# 对应颜色
COLORS = [CYAN, YELLOW, PURPLE, GREEN, RED, BLUE, ORANGE]

class TetrisPiece:
    """俄罗斯方块类"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.shape_index = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_index]
        self.color = COLORS[self.shape_index]
        self.rotation = 0

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

class TetrisGame:
    """俄罗斯方块游戏主类"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("俄罗斯方块")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

        # 游戏状态
        self.reset_game()

        # 游戏设置
        self.fall_time = 0
        self.fall_speed = 500  # 毫秒

    def reset_game(self):
        """重置游戏"""
        self.board = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        self.fall_time = 0

    def new_piece(self):
        """创建新的俄罗斯方块"""
        piece = TetrisPiece(GRID_WIDTH // 2 - 1, 0)
        return piece

    def is_valid_position(self, piece, dx=0, dy=0, rotation=None):
        """检查方块位置是否有效"""
        shape = piece.shape if rotation is None else rotation

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
                if cell:
                    if piece.y + y >= 0:
                        self.board[piece.y + y][piece.x + x] = piece.color

    def clear_lines(self):
        """清除完整的行"""
        lines_to_clear = []

        for y in range(GRID_HEIGHT):
            if all(cell != BLACK for cell in self.board[y]):
                lines_to_clear.append(y)

        for y in lines_to_clear:
            del self.board[y]
            self.board.insert(0, [BLACK for _ in range(GRID_WIDTH)])

        lines_cleared = len(lines_to_clear)
        self.lines_cleared += lines_cleared

        # 更新分数
        if lines_cleared > 0:
            points = [0, 100, 300, 500, 800][lines_cleared] * self.level
            self.score += points

            # 更新等级
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(100, 500 - (self.level - 1) * 50)

        return lines_cleared

    def move_piece(self, dx, dy):
        """移动方块"""
        if self.is_valid_position(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False

    def rotate_piece(self):
        """旋转方块"""
        rotated_shape = self.current_piece.get_rotated_shape()
        if self.is_valid_position(self.current_piece, rotation=rotated_shape):
            self.current_piece.shape = rotated_shape
            return True

        # 尝试墙踢
        for dx in [-1, 1, -2, 2]:
            if self.is_valid_position(self.current_piece, dx=dx, rotation=rotated_shape):
                self.current_piece.x += dx
                self.current_piece.shape = rotated_shape
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

    def lock_current_piece(self):
        """锁定当前方块"""
        self.lock_piece(self.current_piece)
        self.clear_lines()

        # 检查游戏结束
        if not self.is_valid_position(self.next_piece):
            self.game_over = True
        else:
            self.current_piece = self.next_piece
            self.next_piece = self.new_piece()

    def update(self, dt):
        """更新游戏状态"""
        if self.game_over or self.paused:
            return

        self.fall_time += dt

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

                # 绘制方块
                if self.board[y][x] != BLACK:
                    pygame.draw.rect(self.screen, self.board[y][x],
                                   (cell_x, cell_y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, WHITE,
                                   (cell_x, cell_y, CELL_SIZE, CELL_SIZE), 1)
                else:
                    # 绘制网格线
                    pygame.draw.rect(self.screen, DARK_GRAY,
                                   (cell_x, cell_y, CELL_SIZE, CELL_SIZE), 1)

    def draw_piece(self, piece):
        """绘制方块"""
        shape = piece.shape
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    cell_x = BOARD_X + (piece.x + x) * CELL_SIZE
                    cell_y = BOARD_Y + (piece.y + y) * CELL_SIZE
                    pygame.draw.rect(self.screen, piece.color,
                                   (cell_x, cell_y, CELL_SIZE, CELL_SIZE))
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
        next_text = self.font.render("NEXT", True, WHITE)
        self.screen.blit(next_text, (next_x, next_y - 40))

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

    def draw_info(self):
        """绘制游戏信息"""
        info_x = BOARD_X + GRID_WIDTH * CELL_SIZE + 50
        info_y = BOARD_Y + 200

        # 分数
        score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, (info_x, info_y))

        # 已消除行数
        lines_text = self.font.render(f"LINES: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (info_x, info_y + 40))

        # 等级
        level_text = self.font.render(f"LEVEL: {self.level}", True, WHITE)
        self.screen.blit(level_text, (info_x, info_y + 80))

        # 控制说明
        controls_y = info_y + 150
        controls = [
            "CONTROLS:",
            "← → : Move",
            "↓ : Soft Drop",
            "↑ : Rotate",
            "Space: Hard Drop",
            "P : Pause",
            "R : Restart"
        ]

        for i, control in enumerate(controls):
            control_text = self.font.render(control, True, WHITE)
            self.screen.blit(control_text, (info_x, controls_y + i * 30))

    def draw_game_over(self):
        """绘制游戏结束画面"""
        # 半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # 游戏结束文字
        game_over_text = self.big_font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, text_rect)

        # 最终分数
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(score_text, score_rect)

        # 重新开始提示
        restart_text = self.font.render("Press R to Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(restart_text, restart_rect)

    def draw_paused(self):
        """绘制暂停画面"""
        # 半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # 暂停文字
        paused_text = self.big_font.render("PAUSED", True, YELLOW)
        text_rect = paused_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(paused_text, text_rect)

        # 继续提示
        continue_text = self.font.render("Press P to Continue", True, WHITE)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(continue_text, continue_rect)

    def draw(self):
        """绘制游戏画面"""
        self.screen.fill(BLACK)

        self.draw_board()

        if not self.game_over:
            self.draw_piece(self.current_piece)
            self.draw_next_piece()
            self.draw_info()

        if self.game_over:
            self.draw_game_over()

        if self.paused:
            self.draw_paused()

        pygame.display.flip()

    def handle_input(self):
        """处理用户输入"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_game()

                elif not self.game_over:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused

                    elif not self.paused:
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
    game = TetrisGame()
    game.run()

if __name__ == "__main__":
    main()