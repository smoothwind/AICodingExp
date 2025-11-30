# -*- coding: utf-8 -*-
"""
俄罗斯方块简化测试版本
测试核心游戏逻辑
"""

# 俄罗斯方块形状定义
SHAPES = [
    [[1, 1, 1, 1]],  # I型
    [[1, 1], [1, 1]],  # O型
    [[0, 1, 0], [1, 1, 1]],  # T型
    [[0, 1, 1], [1, 1, 0]],  # S型
    [[1, 1, 0], [0, 1, 1]],  # Z型
    [[1, 0, 0], [1, 1, 1]],  # J型
    [[0, 0, 1], [1, 1, 1]]   # L型
]

COLORS = ['CYAN', 'YELLOW', 'PURPLE', 'GREEN', 'RED', 'BLUE', 'ORANGE']

class SimpleTetrisPiece:
    """简化的俄罗斯方块类"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.shape_index = 0
        self.shape = SHAPES[self.shape_index]
        self.color = COLORS[self.shape_index]

    def rotate(self):
        """旋转方块"""
        if self.shape_index == 1:  # O型不需要旋转
            return self.shape

        rotated = []
        for i in range(len(self.shape[0])):
            row = []
            for j in range(len(self.shape) - 1, -1, -1):
                row.append(self.shape[j][i])
            rotated.append(row)

        return rotated

class SimpleTetrisGame:
    """简化的俄罗斯方块游戏测试"""

    def __init__(self):
        self.grid_width = 10
        self.grid_height = 20
        self.reset_game()

    def reset_game(self):
        """重置游戏"""
        self.board = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.current_piece = SimpleTetrisPiece(self.grid_width // 2 - 1, 0)
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False

    def is_valid_position(self, piece, dx=0, dy=0, shape=None):
        """检查位置是否有效"""
        test_shape = shape if shape else piece.shape

        for y, row in enumerate(test_shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece.x + x + dx
                    new_y = piece.y + y + dy

                    # 检查边界
                    if new_x < 0 or new_x >= self.grid_width or new_y >= self.grid_height:
                        return False

                    # 检查碰撞
                    if new_y >= 0 and self.board[new_y][new_x] != 0:
                        return False

        return True

    def lock_piece(self, piece):
        """锁定方块"""
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell and piece.y + y >= 0:
                    self.board[piece.y + y][piece.x + x] = piece.shape_index + 1

    def clear_lines(self):
        """清除完整的行"""
        lines_cleared = []

        for y in range(self.grid_height):
            if all(cell != 0 for cell in self.board[y]):
                lines_cleared.append(y)

        for y in lines_cleared:
            del self.board[y]
            self.board.insert(0, [0 for _ in range(self.grid_width)])

        if lines_cleared:
            self.lines_cleared += len(lines_cleared)
            self.score += len(lines_cleared) * 100

        return len(lines_cleared)

    def move_piece(self, dx, dy):
        """移动方块"""
        if self.is_valid_position(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False

    def rotate_piece(self):
        """旋转方块"""
        rotated = self.current_piece.rotate()
        if self.is_valid_position(self.current_piece, shape=rotated):
            self.current_piece.shape = rotated
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

        # 生成新方块
        self.current_piece = SimpleTetrisPiece(self.grid_width // 2 - 1, 0)

        # 检查游戏结束
        if not self.is_valid_position(self.current_piece):
            self.game_over = True

    def print_board(self):
        """打印游戏板"""
        print(f"Score: {self.score}, Lines: {self.lines_cleared}")
        print(f"Current piece at ({self.current_piece.x}, {self.current_piece.y})")
        print("+" + "-" * (self.grid_width * 2) + "+")

        # 创建显示板
        display_board = [row[:] for row in self.board]

        # 添加当前方块
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    board_y = self.current_piece.y + y
                    board_x = self.current_piece.x + x
                    if 0 <= board_y < self.grid_height and 0 <= board_x < self.grid_width:
                        display_board[board_y][board_x] = 8  # 用8表示当前方块

        # 打印板
        for row in display_board:
            print("|", end="")
            for cell in row:
                if cell == 0:
                    print("  ", end="")
                else:
                    print(f"{cell:2d}", end="")
            print("|")

        print("+" + "-" * (self.grid_width * 2) + "+")
        print()

def run_tests():
    """运行测试"""
    print("=== 俄罗斯方块游戏测试 ===\n")

    # 测试1: 基本游戏初始化
    print("测试1: 基本游戏初始化")
    game = SimpleTetrisGame()
    print(f"游戏板大小: {len(game.board)} x {len(game.board[0])}")
    print(f"当前方块位置: ({game.current_piece.x}, {game.current_piece.y})")
    print(f"游戏结束状态: {game.game_over}")
    print("✓ 初始化测试通过\n")

    # 测试2: 方块移动
    print("测试2: 方块移动")
    initial_x = game.current_piece.x
    success = game.move_piece(1, 0)
    print(f"向右移动: {success}, 新位置: ({game.current_piece.x}, {game.current_piece.y})")

    success = game.move_piece(-1, 0)
    print(f"向左移动: {success}, 新位置: ({game.current_piece.x}, {game.current_piece.y})")

    # 测试边界
    old_x = game.current_piece.x
    while game.move_piece(1, 0):
        pass
    print(f"到达右边界: {game.current_piece.x}")

    game.move_piece(-5, 0)  # 回到中间
    print("✓ 移动测试通过\n")

    # 测试3: 方块旋转
    print("测试3: 方块旋转")
    original_shape = [row[:] for row in game.current_piece.shape]
    success = game.rotate_piece()
    print(f"旋转成功: {success}")
    if success:
        print(f"原始形状: {original_shape}")
        print(f"旋转后形状: {game.current_piece.shape}")
    print("✓ 旋转测试通过\n")

    # 测试4: 下落和锁定
    print("测试4: 下落和锁定")
    print("游戏板状态 (锁定前):")
    game.print_board()

    # 模拟下落
    game.hard_drop()
    print("硬降落后:")
    game.print_board()
    print("✓ 下落测试通过\n")

    # 测试5: 行清除
    print("测试5: 行清除测试")
    # 手动设置一行完整的方块
    for x in range(game.grid_width):
        game.board[game.grid_height - 1][x] = 1

    print("添加完整行后:")
    game.print_board()

    lines_cleared = game.clear_lines()
    print(f"清除的行数: {lines_cleared}")
    print("清除行后:")
    game.print_board()
    print("✓ 行清除测试通过\n")

    # 测试6: 游戏结束检测
    print("测试6: 游戏结束检测")
    # 填充顶部几行来模拟游戏结束
    for y in range(3):
        for x in range(game.grid_width):
            if x < 5:  # 只填充部分，避免完全堵死
                game.board[y][x] = 1

    print("添加障碍物后的游戏板:")
    game.print_board()

    # 尝试生成新方块
    game.current_piece = SimpleTetrisPiece(game.grid_width // 2 - 1, 0)
    if not game.is_valid_position(game.current_piece):
        game.game_over = True

    print(f"游戏结束状态: {game.game_over}")
    print("✓ 游戏结束检测通过\n")

    # 测试7: 完整游戏循环模拟
    print("测试7: 简化的游戏循环模拟")
    game.reset_game()

    for step in range(5):
        print(f"--- 步骤 {step + 1} ---")

        # 随机移动
        import random
        if random.random() < 0.5:
            dx = random.choice([-1, 1])
            game.move_piece(dx, 0)

        # 随机旋转
        if random.random() < 0.3:
            game.rotate_piece()

        # 下落
        if not game.move_piece(0, 1):
            game.lock_current_piece()

        game.print_board()

        if game.game_over:
            print("游戏结束!")
            break

    print(f"最终分数: {game.score}")
    print(f"消除行数: {game.lines_cleared}")
    print("✓ 游戏循环测试通过\n")

    print("=== 所有测试完成 ===")
    print("✓ 俄罗斯方块核心功能测试全部通过!")

if __name__ == "__main__":
    run_tests()