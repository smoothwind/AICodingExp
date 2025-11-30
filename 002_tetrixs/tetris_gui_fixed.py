# -*- coding: utf-8 -*-
"""
修复版GUI俄罗斯方块游戏
包含完整的错误处理和堆栈打印
"""

import tkinter as tk
from tkinter import messagebox
import random
import time
import sys
import threading
import traceback
import logging
import queue
from enum import Enum

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../tetris_debug.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# 游戏常量
CELL_SIZE = 30
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
FALL_SPEED = 1.0  # 秒

# 颜色定义
COLORS = [
    "#000000",  # 黑色 (空格)
    "#00FFFF",  # 青色 (I型)
    "#FFFF00",  # 黄色 (O型)
    "#FF00FF",  # 品红色 (T型)
    "#00FF00",  # 绿色 (S型)
    "#0000FF",  # 蓝色 (Z型)
    "#FFA500",  # 橙色 (J型)
    "#FFA500"   # 橙色 (L型)
]

# 方块字符表示
BLOCK_CHARS = [" ", "□", "△", "○", "◇", "◆", "♣"]

class GameState(Enum):
    """游戏状态"""
    MENU = "菜单"
    PLAYING = "游戏中"
    PAUSED = "暂停"
    GAME_OVER = "游戏结束"

class TetrisPiece:
    """俄罗斯方块类"""

    def __init__(self, x=BOARD_WIDTH // 2 - 1, y=0):
        self.x = x
        self.y = y
        self.shape_index = random.randint(1, 7)  # 1-7，避免0(空格)
        self.shape = self.get_shape()
        self.color = COLORS[self.shape_index - 1]
        self.rotation = 0
        logging.debug(f"Created piece at ({self.x}, {self.y}) with shape index {self.shape_index}")

    def get_shape(self):
        """获取方块形状"""
        shapes = [
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
        return shapes[self.shape_index - 1]

    def get_rotated_shape(self):
        """获取旋转后的形状"""
        if self.shape_index == 2:  # O型不需要旋转
            return self.shape

        # 顺时针旋转90度
        rows = len(self.shape)
        cols = len(self.shape[0])
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]

        for i in range(rows):
            for j in range(cols):
                rotated[j][rows - 1 - i] = self.shape[i][j]

        return rotated

    def rotate(self):
        """旋转方块"""
        if self.shape_index != 2:  # O型不需要旋转
            self.shape = self.get_rotated_shape()
            self.rotation = (self.rotation + 90) % 360
            logging.debug(f"Rotated piece successfully to rotation {self.rotation}°")
            return True
        return False

class RobustTetrisGame:
    """健壮的GUI俄罗斯方块游戏"""

    def __init__(self, master):
        self.master = master
        self.master.title("俄罗斯方块 - 健壮版")
        self.master.geometry("540x700")
        self.master.resizable(False, False)

        # 错误队列
        self.error_queue = queue.Queue()

        # 初始化游戏状态
        self.state = GameState.MENU
        self.reset_game()
        self.keys_pressed = set()

        # 创建UI组件
        if self.create_robust_ui():
            # 绑定键盘事件
            self.master.bind("<KeyPress>", self.safe_key_press)
            self.master.bind("<KeyRelease>", self.safe_key_release)
            self.master.focus_set()

            # 启动错误处理
            self.master.after(100, self.process_error_queue)

            # 启动游戏循环
            self.running = True
            self.state = GameState.PLAYING
            self.game_loop()
        else:
            logging.error("Failed to create UI components")
            self.show_error_dialog("初始化失败", "无法创建游戏界面组件")

    def game_loop(self):
        """游戏主循环"""
        try:
            if self.running and not self.game_over:
                if not self.paused:
                    # 自动下落
                    self.fall_timer += 50  # 50ms
                    if self.fall_timer >= self.fall_speed:
                        self.fall_timer = 0
                        if not self.move_piece(0, 1):
                            self.lock_current_piece()

                # 更新显示
                self.render()
                self.update_labels()

                # 继续循环
                self.master.after(50, self.game_loop)
            else:
                if self.game_over:
                    self.state = GameState.GAME_OVER

        except Exception as e:
            logging.error(f"Game loop error: {str(e)}")
            self.error_queue.put(f"游戏循环错误: {str(e)}")
            self.error_count += 1
            self.running = False

    def reset_game(self):
        """重置游戏"""
        try:
            logging.info("Resetting game...")
            self.board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
            self.current_piece = TetrisPiece()
            self.next_piece = TetrisPiece()
            self.score = 0
            self.lines_cleared = 0
            self.level = 1
            self.fall_timer = 0
            self.fall_speed = 1000  # 1秒
            self.paused = False
            self.game_over = False
            self.move_history = []
            self.error_count = 0

            # 重置UI状态
            self.reset_ui_state()

            logging.info("Game reset successfully")

        except Exception as e:
            logging.error(f"Game reset failed: {str(e)}")
            self.show_error_dialog("游戏重置错误", str(e))
            self.error_count += 1

    def reset_ui_state(self):
        """重置UI状态"""
        try:
            # 重置所有UI组件状态
            if hasattr(self, 'score_label') and self.score_label is not None:
                self.score_label.config(text="分数: 0")

            if hasattr(self, 'lines_label') and self.lines_label is not None:
                self.lines_label.config(text="行数: 0")

            if hasattr(self, 'level_label') and self.level_label is not None:
                self.level_label.config(text="等级: 1")

            if hasattr(self, 'pause_button') and self.pause_button is not None:
                self.pause_button.config(text="暂停", bg="#f39c12", fg="white")

        except Exception as e:
            logging.error(f"UI state reset failed: {str(e)}")
            self.error_count += 1

    def safe_create_label(self, parent, text, font, fg, bg, **kwargs):
        """安全创建标签"""
        try:
            label = tk.Label(parent, text=text, font=font, fg=fg, bg=bg, **kwargs)
            return label
        except Exception as e:
            logging.error(f"Failed to create label: {str(e)}")
            self.error_count += 1
            # 创建简单备用标签
            try:
                return tk.Label(parent, text="标签", font=("Arial", 10), fg="black", bg="white")
            except Exception as e2:
                logging.error(f"Failed to create backup label: {str(e2)}")
                self.error_count += 1
                return None

    def safe_create_button(self, parent, text, command, font, bg, fg, **kwargs):
        """安全创建按钮"""
        try:
            button = tk.Button(parent, text=text, command=command, font=font, bg=bg, fg=fg, **kwargs)
            return button
        except Exception as e:
            logging.error(f"Failed to create button: {str(e)}")
            self.error_count += 1
            try:
                return tk.Button(parent, text="按钮", font=("Arial", 10), bg="gray", fg="black")
            except Exception as e2:
                logging.error(f"Failed to create backup button: {str(e2)}")
                self.error_count += 1
                return None

    def safe_create_text(self, parent, **kwargs):
        """安全创建文本框"""
        try:
            text = tk.Text(parent, **kwargs)
            return text
        except Exception as e:
            logging.error(f"Failed to create text widget: {str(e)}")
            self.error_count += 1
            return None

    def create_robust_ui(self):
        """创建健壮的UI组件"""
        try:
            # 主框架
            self.main_frame = tk.Frame(self.master, bg="#2c3e50")
            self.main_frame.pack(fill=tk.BOTH, expand=True)

            # 标题
            self.title_label = self.safe_create_label(
                self.main_frame,
                text="俄罗斯方块",
                font=("Arial", 16, "bold"),
                fg="#ecf0f1",
                bg="#34495e"
            )
            self.title_label.pack(pady=(0, 20))

            # 信息面板标题
            self.info_title = self.safe_create_label(
                self.main_frame,
                text="游戏信息",
                font=("Arial", 12, "bold"),
                fg="#ecf0f1",
                bg="#34495e"
            )
            self.info_title.pack(pady=(0, 10))

            # 左侧游戏区域
            game_frame = tk.Frame(self.main_frame, bg="#34495e")
            game_frame.pack(side=tk.LEFT, padx=10, pady=5)

            # 游戏画布
            self.canvas = tk.Canvas(
                game_frame,
                width=CELL_SIZE * BOARD_WIDTH,
                height=CELL_SIZE * BOARD_HEIGHT,
                bg="#1a1a1a",
                highlightthickness=2,
                highlightbackground="#ecf0f1"
            )
            self.canvas.pack(pady=5)

            # 右侧信息面板
            info_panel = tk.Frame(self.main_frame, bg="#34495e", width=200)
            info_panel.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

            # 存储UI组件引用
            self.ui_components = {}

            # 分数显示
            self.score_frame = self.create_score_panel(info_panel)
            self.ui_components['score_frame'] = self.score_frame
            self.ui_components['score_label'] = self.score_frame[1]

            # 行数显示
            self.lines_frame = self.create_lines_panel(info_panel)
            self.ui_components['lines_frame'] = self.lines_frame
            self.ui_components['lines_label'] = self.lines_frame[1]

            # 等级显示
            self.level_frame = self.create_level_panel(info_panel)
            self.ui_components['level_frame'] = self.level_frame
            self.ui_components['level_label'] = self.level_frame[1]

            # 下一个方块预览
            self.next_frame = self.create_next_piece_preview(info_panel)
            self.ui_components['next_frame'] = self.next_frame
            self.ui_components['next_canvas'] = self.next_frame[1]

            # 控制按钮
            control_frame = self.create_control_panel(info_panel)
            self.ui_components['control_frame'] = control_frame
            self.ui_components['pause_button'] = control_frame[1]
            self.ui_components['reset_button'] = control_frame[2]
            self.ui_components['quit_button'] = control_frame[3]

            # 调试信息显示
            self.debug_frame = self.create_debug_panel(info_panel)
            self.ui_components['debug_text'] = self.debug_frame[1]

            logging.info("UI components created successfully")
            return True

        except Exception as e:
            logging.error(f"UI creation failed: {str(e)}")
            traceback.print_exc()
            self.error_count += 1
            self.show_error_dialog("界面创建错误", str(e))
            return False

    def create_score_panel(self, parent):
        """创建分数面板"""
        try:
            panel = tk.Frame(parent, bg="#34495e")
            panel.pack(fill=tk.X, pady=5)

            title = self.safe_create_label(
                panel,
                text="分数",
                font=("Arial", 10, "bold"),
                fg="#ecf0f1",
                bg="#34495e"
            )
            title.pack(pady=5)

            label = self.safe_create_label(
                panel,
                text="0",
                font=("Arial", 12),
                fg="#f39c12",
                bg="#34495e"
            )
            self.ui_components['score_label'] = label
            label.pack()

            return panel, label

        except Exception as e:
            logging.error(f"Score panel creation failed: {str(e)}")
            self.error_count += 1
            return None, None

    def create_lines_panel(self, parent):
        """创建行数面板"""
        try:
            panel = tk.Frame(parent, bg="#34495e")
            panel.pack(fill=tk.X, pady=5)

            title = self.safe_create_label(
                panel,
                text="行数",
                font=("Arial", 10, "bold"),
                fg="#ecf0f1",
                bg="#34495e"
            )
            title.pack(pady=5)

            label = self.safe_create_label(
                panel,
                text="0",
                font=("Arial", 12),
                fg="#27ae60",
                bg="#34495e"
            )
            self.ui_components['lines_label'] = label
            label.pack()

            return panel, label

        except Exception as e:
            logging.error(f"Lines panel creation failed: {str(e)}")
            self.error_count += 1
            return None, None

    def create_level_panel(self, parent):
        """创建等级面板"""
        try:
            panel = tk.Frame(parent, bg="#34495e")
            panel.pack(fill=tk.X, pady=5)

            title = self.safe_create_label(
                panel,
                text="等级",
                font=("Arial", 10, "bold"),
                fg="#ecf0f1",
                bg="#34495e"
            )
            title.pack(pady=5)

            label = self.safe_create_label(
                panel,
                text="1",
                font=("Arial", 12),
                fg="#f1c40f",
                bg="#34495e"
            )
            self.ui_components['level_label'] = label
            label.pack()

            return panel, label

        except Exception as e:
            logging.error(f"Level panel creation failed: {str(e)}")
            self.error_count += 1
            return None, None

    def create_next_piece_preview(self, parent):
        """创建下一个方块预览"""
        try:
            panel = tk.Frame(parent, bg="#34495e", relief=tk.RAISED, bd=2)
            panel.pack(pady=10)

            title = self.safe_create_label(
                panel,
                text="下一个",
                font=("Arial", 10, "bold"),
                fg="#ecf0f1",
                bg="#34495e"
            )
            title.pack(pady=5)

            canvas = tk.Canvas(
                panel,
                width=CELL_SIZE * 4,
                height=CELL_SIZE * 4,
                bg="#1a1a1a",
                highlightthickness=1,
                highlightbackground="#ecf0f1"
            )
            canvas.pack(padx=10, pady=(0, 10))
            self.ui_components['next_canvas'] = canvas
            self.ui_components['next_frame'] = panel

            return panel, canvas

        except Exception as e:
            logging.error(f"Next piece preview creation failed: {str(e)}")
            self.error_count += 1
            return None, None

    def create_control_panel(self, parent):
        """创建控制面板"""
        try:
            panel = tk.Frame(parent, bg="#2c3e50")
            panel.pack(pady=20)

            button_frame = tk.Frame(panel, bg="#2c3e50")
            button_frame.pack()

            pause_btn = self.safe_create_button(
                button_frame,
                text="暂停",
                command=self.toggle_pause,
                font=("Arial", 10),
                bg="#f39c12",
                fg="white",
                width=10
            )
            self.ui_components['pause_button'] = pause_btn
            pause_btn.pack(side=tk.LEFT, padx=5)

            reset_btn = self.safe_create_button(
                button_frame,
                text="重新开始",
                command=self.reset_game,
                font=("Arial", 10),
                bg="#e74c3c",
                fg="white",
                width=10
            )
            self.ui_components['reset_button'] = reset_btn
            reset_btn.pack(side=tk.LEFT, padx=5)

            quit_btn = self.safe_create_button(
                button_frame,
                text="退出",
                command=self.quit_game,
                font=("Arial", 10),
                bg="#95a5a6",
                fg="white",
                width=10
            )
            self.ui_components['quit_button'] = quit_btn
            quit_btn.pack(side=tk.LEFT, padx=5)

            return panel, pause_btn, reset_btn, quit_btn

        except Exception as e:
            logging.error(f"Control panel creation failed: {str(e)}")
            self.error_count += 1
            return None

    def create_debug_panel(self, parent):
        """创建调试面板"""
        try:
            panel = tk.Frame(parent, bg="#34495e")
            panel.pack(fill=tk.X, pady=5)

            title = self.safe_create_label(
                panel,
                text="调试信息",
                font=("Arial", 10, "bold"),
                fg="#ecf0f1",
                bg="#34495e"
            )
            title.pack(pady=5)

            # 调试文本框
            self.debug_text = tk.Text(
                panel,
                height=8,
                width=30,
                font=("Courier", 9),
                fg="#ecf0f1",
                bg="#2c3e50",
                wrap=tk.WORD
            )
            self.ui_components['debug_text'] = self.debug_text
            self.debug_text.pack(pady=5, fill=tk.X)

            # 按钮
            button_frame = tk.Frame(panel, bg="#34495e")
            button_frame.pack()

            clear_btn = self.safe_create_button(
                button_frame,
                text="清除日志",
                command=self.clear_debug_log,
                font=("Arial", 9),
                bg="#8e44ad",
                fg="white",
                width=10
            )
            clear_btn.pack(side=tk.LEFT, padx=5)

            print_btn = self.safe_create_button(
                button_frame,
                text="打印堆栈",
                command=self.print_stack_trace,
                font=("Arial", 9),
                bg="#8e44ad",
                fg="white",
                width=10
            )
            print_btn.pack(side=tk.LEFT, padx=5)

            return panel, self.debug_text

        except Exception as e:
            logging.error(f"Debug panel creation failed: {str(e)}")
            self.error_count += 1
            return None

    def show_error_dialog(self, title, message):
        """显示错误对话框"""
        try:
            messagebox.showerror(title, message)
            logging.error(f"Error: {title} - {message}")
            self.error_count += 1
        except Exception as e:
            logging.error(f"Failed to show error dialog: {str(e)}")
            self.error_count += 1

    def draw_board(self):
        """绘制游戏板"""
        try:
            self.canvas.delete("all")

            # 绘制网格背景
            for y in range(BOARD_HEIGHT):
                for x in range(BOARD_WIDTH):
                    x1 = x * CELL_SIZE
                    y1 = y * CELL_SIZE
                    x2 = x1 + CELL_SIZE
                    y2 = y1 + CELL_SIZE

                    # 绘制网格线
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        outline="#34495e",
                        width=1
                    )
                    # 绘制空格或方块
                    if self.board[y][x] == 0:
                        self.canvas.create_rectangle(
                            x1, y1, x2, y2,
                            fill="#1a1a1a",
                            outline="#34495e",
                            width=1
                        )
                    else:
                        color = self.board[y][x]
                        # Ensure color is a valid hex color string
                        if isinstance(color, str) and color.startswith('#'):
                            self.canvas.create_rectangle(
                                x1, y1, x2, y2,
                                fill=color,
                                outline="#ecf0f1",
                                width=1
                            )
                        elif color > 0 and color < len(COLORS):
                            # Handle legacy numeric color values
                            hex_color = COLORS[color - 1]
                            self.canvas.create_rectangle(
                                x1, y1, x2, y2,
                                fill=hex_color,
                                outline="#ecf0f1",
                                width=1
                            )

            logging.debug("Board drawn successfully")

        except Exception as e:
            self.error_queue.put(f"游戏板绘制错误: {str(e)}")
            self.error_count += 1

    def draw_current_piece(self):
        """绘制当前方块"""
        try:
            if self.current_piece and not self.game_over and not self.paused:
                shape = self.current_piece.shape
                color = self.current_piece.color

                for y, row in enumerate(shape):
                    for x, cell in enumerate(row):
                        if cell:
                            board_x = self.current_piece.x + x
                            board_y = self.current_piece.y + y

                            if 0 <= board_x < BOARD_WIDTH and 0 <= board_y < BOARD_HEIGHT:
                                x1 = board_x * CELL_SIZE
                                y1 = board_y * CELL_SIZE
                                x2 = x1 + CELL_SIZE
                                y2 = y1 + CELL_SIZE

                                self.canvas.create_rectangle(
                                    x1, y1, x2, y2,
                                    fill=color,
                                    outline="#ecf0f1",
                                    width=1
                                )
                            else:
                                logging.warning(f"Piece out of bounds: ({board_x}, {board_y})")

        except Exception as e:
            self.error_queue.put(f"方块绘制错误: {str(e)}")
            self.error_count += 1

    def update_labels(self):
        """更新标签显示"""
        try:
            if 'score_label' in self.ui_components:
                self.ui_components['score_label'].config(text=str(self.score))

            if 'lines_label' in self.ui_components:
                self.ui_components['lines_label'].config(text=f"{self.lines_cleared}")

            if 'level_label' in self.ui_components:
                self.ui_components['level_label'].config(text=f"{self.level}")

            logging.debug(f"Updated labels - Score: {self.score}, Lines: {self.lines_cleared}, Level: {self.level}")

        except Exception as e:
            self.error_queue.put(f"标签更新错误: {str(e)}")
            self.error_count += 1

    def draw_next_piece(self):
        """绘制下一个方块预览"""
        try:
            if 'next_canvas' in self.ui_components and self.ui_components['next_canvas']:
                # 清除画布
                self.ui_components['next_canvas'].delete("all")

            if self.next_piece:
                shape = self.next_piece.shape
                color = self.next_piece.color

                # 计算居中偏移
                offset_x = (4 - len(shape[0])) // 2
                offset_y = (4 - len(shape)) // 2

                for y, row in enumerate(shape):
                    for x, cell in enumerate(row):
                        if cell:
                            x1 = (offset_x + x) * CELL_SIZE
                            y1 = (offset_y + y) * CELL_SIZE
                            x2 = x1 + CELL_SIZE
                            y2 = y1 + CELL_SIZE

                            self.ui_components['next_canvas'].create_rectangle(
                                x1, y1, x2, y2,
                                fill=color,
                                outline="#ecf0f1",
                                width=1
                            )

        except Exception as e:
            self.error_queue.put(f"下一个方块绘制错误: {str(e)}")
            self.error_count += 1

    def render(self):
        """渲染游戏画面"""
        try:
            self.draw_board()
            self.draw_current_piece()
            self.draw_next_piece()
            self.draw_controls_info()

            # 添加调试信息
            if 'debug_text' in self.ui_components:
                self.debug_text.insert(tk.END, f"游戏状态: {self.state}")
                self.debug_text.see(tk.END)

        except Exception as e:
            self.error_queue.put(f"渲染错误: {str(e)}")
            self.error_count += 1

    def draw_controls_info(self):
        """绘制控制说明"""
        controls_info = "控制说明:\n"
        controls_info += f"  错误次数: {self.error_count}\n"
        controls_info += f"  暂停: {'是' if self.paused else '否'}\n"
        controls_info += f"  游戏状态: {self.state}\n"
        controls_info += f"  当前分数: {self.score}\n"
        controls_info += f"  消除行数: {self.lines_cleared}\n"
        controls_info += f"  当前等级: {self.level}\n"

        try:
            if 'debug_text' in self.ui_components:
                self.debug_text.insert(tk.END, controls_info)
        except:
            pass  # 如果调试文本不存在，跳过

    def is_valid_position(self, piece, dx=0, dy=0, shape=None):
        """检查位置是否有效"""
        try:
            test_shape = shape if shape else piece.shape

            for y, row in enumerate(test_shape):
                for x, cell in enumerate(row):
                    if cell:
                        new_x = piece.x + x + dx
                        new_y = piece.y + y + dy

                        # 检查边界
                        if new_x < 0 or new_x >= BOARD_WIDTH or new_y >= BOARD_HEIGHT:
                            logging.debug(f"Invalid position: ({new_x}, {new_y})")
                            return False

                        # 检查碰撞
                        if new_y >= 0 and self.board[new_y][new_x] != 0:
                            logging.debug(f"Collision detected at ({new_x}, {new_y})")
                            return False

            logging.debug(f"Position is valid: ({piece.x + dx}, {piece.y + dy})")
            return True

        except Exception as e:
            self.error_queue.put(f"位置检查错误: {str(e)}")
            return False

    def lock_current_piece(self):
        """锁定当前方块"""
        try:
            lines_cleared = self.lock_piece(self.current_piece)

            # 生成新方块
            self.current_piece = self.next_piece
            self.next_piece = TetrisPiece()

            # 检查游戏结束
            if not self.is_valid_position(self.current_piece):
                self.game_over = True
                self.state = GameState.GAME_OVER
                logging.info("Game Over!")
                self.show_error_dialog("游戏结束", f"最终分数: {self.score}")
                return False

            return True

        except Exception as e:
            self.error_queue.put(f"锁定当前方块错误: {str(e)}")
            self.error_count += 1
            return False

    def lock_piece(self, piece):
        """锁定方块到游戏板"""
        try:
            for y, row in enumerate(piece.shape):
                for x, cell in enumerate(row):
                    if cell and piece.y + y >= 0:
                        board_y = piece.y + y
                        board_x = piece.x + x

                        if 0 <= board_x < BOARD_WIDTH and board_y < BOARD_HEIGHT:
                            # Use actual color instead of index
                            if piece.shape_index > 0 and piece.shape_index < len(COLORS):
                                self.board[board_y][board_x] = COLORS[piece.shape_index - 1]
                            else:
                                self.board[board_y][board_x] = piece.color
                            logging.debug(f"Locked piece at ({board_x}, {board_y}) with color index {piece.shape_index}")
                        else:
                            logging.warning(f"Piece position out of bounds: ({board_x}, {board_y})")

            # 清除完整行
            lines_cleared = self.clear_lines()
            if lines_cleared > 0:
                points = [0, 100, 300, 500, 800][lines_cleared] * self.level
                self.score += points

                # 更新等级
                self.level = self.lines_cleared // 10 + 1
                self.fall_speed = max(50, 1000 - (self.level - 1) * 100)
                self.fall_timer = 0

                logging.info(f"Cleared {lines_cleared} lines, earned {points} points, new level: {self.level}")

            return lines_cleared

        except Exception as e:
            self.error_queue.put(f"方块锁定错误: {str(e)}")
            return 0

    def clear_lines(self):
        """清除完整的行"""
        try:
            lines_cleared = 0
            lines_to_clear = []

            # 找出所有完整的行
            for y in range(BOARD_HEIGHT):
                if all(self.board[y][x] != 0 for x in range(BOARD_WIDTH)):
                    lines_to_clear.append(y)
                    logging.debug(f"Found complete line at y={y}")

            # 清除完整的行
            for line_y in lines_to_clear:
                # 从该行开始，将上面的所有行下移
                for y in range(line_y, 0, -1):
                    self.board[y] = self.board[y - 1][:]
                # 顶部添加新的空行
                self.board[0] = [0 for _ in range(BOARD_WIDTH)]
                lines_cleared += 1
                logging.debug(f"Cleared line at y={line_y}")

            # 更新总消除行数
            self.lines_cleared += lines_cleared

            if lines_cleared > 0:
                logging.info(f"Cleared {lines_cleared} lines this move. Total lines: {self.lines_cleared}")

            return lines_cleared

        except Exception as e:
            self.error_queue.put(f"清除行错误: {str(e)}")
            logging.error(f"Error clearing lines: {str(e)}")
            return 0

    def move_piece(self, dx, dy):
        """移动方块"""
        try:
            if self.is_valid_position(self.current_piece, dx, dy):
                old_x = self.current_piece.x
                old_y = self.current_piece.y

                self.current_piece.x += dx
                self.current_piece.y += dy

                # 记录移动历史
                self.move_history.append(f"Move: ({old_x}, {old_y}) → ({self.current_piece.x}, {self.current_piece.y})")

                logging.debug(f"Moved piece by ({dx}, {dy})")

                if dy > 0:
                    self.score += 1  # 软降落加分

                return True
            return False

        except Exception as e:
            self.error_queue.put(f"移动错误: {str(e)}")
            self.error_count += 1

    def rotate_piece(self):
        """旋转方块"""
        try:
            rotated_shape = self.current_piece.get_rotated_shape()

            # 尝试直接旋转
            if self.is_valid_position(self.current_piece, shape=rotated_shape):
                self.current_piece.shape = rotated_shape
                self.current_piece.rotation = (self.current_piece.rotation + 90) % 360
                logging.debug(f"Rotated piece to rotation {self.current_piece.rotation}°")

                return True

            # 尝试墙踢
            for kick_x in [-1, 1, -2, 2]:
                if self.is_valid_position(self.current_piece, dx=kick_x, shape=rotated_shape):
                    self.current_piece.x += kick_x
                    self.current_piece.shape = rotated_shape
                    logging.debug(f"Rotated piece with wall kick at offset {kick_x}")
                    return True

            logging.debug("Failed to rotate piece")
            return False

        except Exception as e:
            self.error_queue.put(f"旋转错误: {str(e)}")
            return False

    def hard_drop(self):
        """硬降落"""
        try:
            drop_distance = 0
            while self.is_valid_position(self.current_piece, dy=1):
                self.current_piece.y += 1
                drop_distance += 1

            self.score += drop_distance * 2
            logging.debug(f"Hard dropped {drop_distance} cells, earned {drop_distance * 2} points")

            self.lock_current_piece()

        except Exception as e:
            self.error_queue.put(f"硬降落错误: {str(e)}")
            return False

    def toggle_pause(self):
        """切换暂停状态"""
        try:
            if not self.game_over:
                self.paused = not self.paused
                action = "继续游戏" if self.paused else "暂停游戏"
                logging.info(f"Game {action.lower()}")

                # 更新暂停按钮
                if 'pause_button' in self.ui_components:
                    if self.paused:
                        self.ui_components['pause_button'].config(
                            text="继续",
                            bg="#27ae60",
                            fg="white"
                        )
                    else:
                        self.ui_components['pause_button'].config(
                            text="暂停",
                            bg="#f39c12",
                            fg="white"
                        )
        except Exception as e:
            self.error_queue.put(f"暂停切换错误: {str(e)}")
            return False

    def reset_game(self):
        """重置游戏"""
        try:
            logging.info("Resetting game...")
            self.board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
            self.current_piece = TetrisPiece()
            self.next_piece = TetrisPiece()
            self.score = 0
            self.lines_cleared = 0
            self.level = 1
            self.fall_timer = 0
            self.fall_speed = 1000  # 1秒
            self.paused = False
            self.game_over = False
            self.move_history = []
            self.error_count = 0

            # 重置UI状态
            self.reset_ui_state()

            logging.info("Game reset successfully")

        except Exception as e:
            self.error_queue.put(f"游戏重置错误: {str(e)}")
            self.show_error_dialog("游戏重置", str(e))
            self.error_count += 1

    def clear_debug_log(self):
        """清除调试日志"""
        try:
            if 'debug_text' in self.ui_components:
                self.debug_text.delete(1.0, tk.END)
                self.debug_text.insert(tk.END, f"调试日志已清除\n时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                logging.info("Debug log cleared by user")

        except Exception as e:
            logging.error(f"清除日志失败: {str(e)}")
            self.error_count += 1

    def print_stack_trace(self):
        """打印调用堆栈"""
        try:
            import inspect
            stack_info = "=== 调用堆栈信息 ===\n"

            # 获取当前堆栈
            stack = inspect.stack()

            for i, frame_info in enumerate(stack):
                filename = frame_info[1] if len(frame_info) > 1 else "Unknown"
                function_name = frame_info[3] if len(frame_info) > 3 else "Unknown"
                line_number = frame_info[2] if len(frame_info) > 2 else "Unknown"

                stack_info += f"{i}: {filename}:{line_number} in {function_name}()\n"
                stack_info += f"  当前位置: {frame_info[0]}:{frame_info[1]}:{frame_info[2]}\n"

            stack_info += "=== 当前游戏状态 ===\n"
            stack_info += f"分数: {self.score}\n"
            stack_info += f"行数: {self.lines_cleared}\n"
            stack_info += f"等级: {self.level}\n"
            stack_info += f"暂停状态: {self.paused}\n"
            stack_info += f"游戏状态: {self.state}\n"

            # 添加到调试信息
            self.debug_text.insert(tk.END, stack_info)
            self.debug_text.see(tk.END)

            # 输出到文件和日志
            print(stack_info)
            logging.info(stack_info)

        except Exception as e:
            logging.error(f"打印堆栈失败: {str(e)}")
            self.error_count += 1

    def process_error_queue(self):
        """处理错误队列"""
        try:
            while not self.error_queue.empty():
                error_msg = self.error_queue.get()
                if error_msg:
                    logging.error(f"Game Error: {error_msg}")
                    self.show_error_dialog("游戏错误", error_msg)
                    self.error_count += 1

                time.sleep(0.1)  # 短暂处理

        except Exception as e:
            logging.error(f"错误队列处理失败: {str(e)}")
            self.error_count += 1

    def run_game_loop(self):
        """游戏主循环 - 已弃用，使用game_loop代替"""
        logging.warning("run_game_loop is deprecated, using game_loop instead")
        return

    def safe_key_press(self, event):
        """安全键盘按下处理"""
        try:
            if self.game_over or self.paused:
                return  # 忽略输入

            # 记录按键状态
            self.keys_pressed.add(event.keysym)

            # 处理按键
            if event.keysym == 'Left':
                self.move_piece(-1, 0)
            elif event.keysym == 'Right':
                self.move_piece(1, 0)
            elif event.keysym == 'Up':
                self.rotate_piece()
            elif event.keysym == 'Down':
                if self.move_piece(0, 1):
                    self.score += 1
            elif event.keysym == 'space':
                self.hard_drop()
            elif event.keysym == 'p':
                self.toggle_pause()
            elif event.keysym == 'r':
                self.reset_game()
            elif event.keysym == 'Escape':
                if self.state == GameState.PLAYING:
                    self.state = GameState.MENU
                    self.running = False
                elif self.state == GameState.GAME_OVER:
                    self.running = False

        except Exception as e:
            self.error_queue.put(f"键盘事件处理错误: {str(e)}")
            self.error_count += 1

    def safe_key_release(self, event):
        """安全键盘释放处理"""
        try:
            self.keys_pressed.discard(event.keysym)

        except Exception as e:
            self.error_queue.put(f"键盘释放事件处理错误: {str(e)}")
            self.error_count += 1

    def quit_game(self):
        """退出游戏"""
        try:
            result = messagebox.askyesno("退出游戏", "确定要退出俄罗斯方块游戏吗？")
            if result:
                logging.info("User chose to quit")
                self.running = False
                self.master.quit()
                sys.exit(0)
            else:
                logging.info("User cancelled quit")
        except Exception as e:
            logging.error(f"退出游戏错误: {str(e)}")
            self.error_count += 1

    def main(self):
        """主函数"""
        try:
            logging.info("Starting Tetris Game...")
            self.master.mainloop()
        except Exception as e:
            logging.error(f"游戏启动失败: {str(e)}")
            self.show_error_dialog("启动失败", str(e))

if __name__ == "__main__":
    game = RobustTetrisGame(tk.Tk())
    game.main()