# 俄罗斯方块游戏 - Tetris Game

## 📋 项目概述

这是一个完整的俄罗斯方块游戏实现，包含两个版本：
- **基础版本** (`tetris.py`) - 经典俄罗斯方块游戏
- **增强版本** (`tetris_enhanced.py`) - 包含音效、特效、高分榜等高级功能

## 🎮 游戏特性

### 基础版本特性
- ✅ 7种经典俄罗斯方块形状
- ✅ 方块旋转和移动
- ✅ 行消除机制
- ✅ 分数和等级系统
- ✅ 游戏暂停功能
- ✅ 键盘控制

### 增强版本特性
- 🎯 多种游戏模式（经典、冲刺、马拉松）
- 🏆 高分榜系统
- 🎨 视觉特效（粒子效果、闪烁）
- 👻 幽灵方块显示
- 🔄 方块保留功能
- 🎵 音效系统
- 📊 详细统计信息
- 🎭 游戏状态管理（菜单、游戏、暂停、结束）

## 🚀 安装和运行

### 系统要求
- Python 3.7+
- Pygame 库

### 安装步骤

1. **安装Pygame**
```bash
# 使用pip安装
pip install pygame

# 或者使用conda
conda install pygame
```

2. **运行游戏**
```bash
# 运行基础版本
python tetris.py

# 运行增强版本
python tetris_enhanced.py
```

## 🎯 游戏控制

### 基础控制
- `←/→` - 左右移动
- `↓` - 软降落
- `↑` - 旋转方块
- `空格` - 硬降落
- `P` - 暂停/继续
- `R` - 重新开始

### 增强版本控制
- `C` - 保留/交换方块
- `ESC` - 返回主菜单
- `Enter` - 确认选择
- `↑/↓` - 菜单导航

## 🧮 测试结果

### 功能测试
```
=== TETRIS GAME TEST SUITE ===

✅ Test 1: Basic game initialization - PASSED
   - Board size: 20x10
   - Current piece position: (4, 0)
   - Game over status: False

✅ Test 2: Piece movement - PASSED
   - Left/right movement working
   - Boundary detection working
   - Movement validation working

✅ Test 3: Piece rotation - PASSED
   - Rotation mechanics working
   - Shape transformation correct

✅ Test 4: Drop and lock - PASSED
   - Hard drop functioning
   - Piece locking to board
   - Score calculation (32 points for 16 cells dropped)

✅ Test 5: Line clearing - PASSED
   - Complete line detection
   - Line removal and board shifting
   - Score calculation (+100 points per line)

✅ Test 6: Game over detection - PASSED
   - Collision detection with existing blocks
   - New piece spawn validation
   - Game over state management

✅ Test 7: Game loop simulation - PASSED
   - Multi-step game simulation
   - Random movement and rotation
   - State consistency maintained

Overall Result: SUCCESS - All core functionality tests passed!
```

## 📊 游戏机制详解

### 方块形状
1. **I型** - 长条形 `[[1,1,1,1]]`
2. **O型** - 方形 `[[1,1],[1,1]]`
3. **T型** - T形 `[[0,1,0],[1,1,1]]`
4. **S型** - S形 `[[0,1,1],[1,1,0]]`
5. **Z型** - Z形 `[[1,1,0],[0,1,1]]`
6. **J型** - J形 `[[1,0,0],[1,1,1]]`
7. **L型** - L形 `[[0,0,1],[1,1,1]]`

### 分数系统
- **软降落**: 每下降1行 +1分
- **硬降落**: 每下降1行 +2分
- **单行消除**: 100分
- **双行消除**: 300分
- **三行消除**: 500分
- **四行消除(Tetris)**: 800分

### 等级系统
- **经典模式**: 每消除10行升一级，速度递增
- **冲刺模式**: 固定速度，目标消除40行
- **马拉松模式**: 每消除15行升一级，最高15级

## 🛠 技术实现

### 核心组件
1. **TetrisPiece类** - 方块对象管理
2. **TetrisGame类** - 游戏主逻辑
3. **Board系统** - 游戏板和碰撞检测
4. **Score系统** - 分数和等级计算
5. **Input系统** - 用户输入处理

### 关键算法
- **碰撞检测**: 边界和方块碰撞检查
- **旋转算法**: 矩阵旋转变换
- **行消除**: 完整行检测和移除
- **墙踢系统**: 旋转时的位置调整

## 🐛 测试和调试

### 测试文件
- `tetris_test.py` - 核心功能测试
- 运行命令: `python tetris_test.py`

### 测试覆盖
- ✅ 游戏初始化
- ✅ 方块移动
- ✅ 方块旋转
- ✅ 下落和锁定
- ✅ 行消除
- ✅ 游戏结束检测
- ✅ 游戏循环模拟

## 📁 项目结构
```
tetris_project/
├── tetris.py              # 基础版本
├── tetris_enhanced.py     # 增强版本
├── tetris_test.py         # 测试套件
├── tetris_highscores.json # 高分记录文件
└── TETRIS_README.md       # 项目文档
```

## 🎯 开发说明

### 扩展功能
增强版本支持以下扩展：
- 自定义主题和颜色
- 在线多人对战
- 更多游戏模式
- 成就系统
- 排行榜

### 性能优化
- 使用pygame的优化绘图功能
- 高效的碰撞检测算法
- 内存管理优化
- 帧率控制

## 📝 更新日志

### v1.0.0 (当前版本)
- ✅ 完整的俄罗斯方块核心功能
- ✅ 基础和增强两个版本
- ✅ 完整的测试覆盖
- ✅ 详细文档和说明

### 未来计划
- 🔄 添加更多游戏模式
- 🎵 改进音效系统
- 🌐 网络功能
- 📱 移动端适配

## 🤝 贡献指南

欢迎提交问题和改进建议：
1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证。

---

## 🎮 立即开始

```bash
# 克隆或下载项目文件
cd tetris_project

# 安装依赖
pip install pygame

# 开始游戏
python tetris_enhanced.py  # 推荐使用增强版本
```

享受游戏！🎉