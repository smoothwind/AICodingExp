# PythonProject2

一个包含多个实用Python工具和游戏的项目集合。

## 📁 项目结构

```
PythonProject2/
├── README.md                 # 项目说明文档
├── .gitignore               # Git忽略文件配置
├── .venv/                   # Python虚拟环境
├── 001_countdown/           # 多任务倒计时工具
│   ├── countdown_timer.py   # 倒计时工具主程序
│   └── 多任务倒计时工具-详细设计文档.md  # 设计文档
├── 002_tetrixs/             # 俄罗斯方块游戏
│   ├── tetris_gui_fixed.py  # 游戏主程序
│   └── 项目总结文档.md       # 项目总结
└── __pycache__/             # Python缓存目录
```

## 🚀 项目模块

### 1. 多任务倒计时工具 (`001_countdown/`)

一个功能强大的GUI倒计时工具，支持多任务并发运行。

**主要功能：**
- 支持创建和管理多个独立的计时器
- 多个计时器可以同时运行而不互相影响
- 每个计时器有独立的开始、暂停、重置、删除功能
- 支持对所有计时器的批量控制
- 提供直观的图形界面和丰富的视觉反馈

**技术栈：**
- Python 3.x
- tkinter（GUI框架）
- threading（多线程处理）
- time（时间管理）
- uuid（唯一标识）

**运行方式：**
```bash
cd 001_countdown
python countdown_timer.py
```

### 2. 俄罗斯方块游戏 (`002_tetrixs/`)

一个使用Python和Tkinter开发的完整图形化俄罗斯方块游戏。

**主要功能：**
- 7种标准俄罗斯方块形状（I、O、T、S、Z、J、L型）
- 完整的游戏逻辑：方块移动、旋转、碰撞检测、行消除
- 等级系统：根据消除行数自动提升等级，增加下落速度
- 计分系统：软降落、硬降落、行消除等多种得分机制
- 主游戏区域：10×20的标准游戏板
- 信息面板：实时显示分数、消除行数、当前等级
- 下一个方块预览
- 键盘操作控制和按钮控制

**技术栈：**
- Python 3.x
- tkinter（GUI框架）

**运行方式：**
```bash
cd 002_tetrixs
python tetris_gui_fixed.py
```

## 🛠️ 环境要求

- Python 3.6+
- tkinter（通常随Python安装包一起提供）
- 操作系统：Windows、macOS、Linux

## 📋 安装和运行

1. **克隆项目：**
   ```bash
   git clone <repository-url>
   cd PythonProject2
   ```

2. **创建虚拟环境（推荐）：**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # 或
   .venv\Scripts\activate     # Windows
   ```

3. **运行各个模块：**
   ```bash
   # 运行倒计时工具
   cd 001_countdown
   python countdown_timer.py

   # 运行俄罗斯方块游戏
   cd 002_tetrixs
   python tetris_gui_fixed.py
   ```

## 🎮 游戏控制

### 俄罗斯方块操作：
- **方向键左右**：移动方块
- **方向键下**：加速下落
- **方向键上**：旋转方块
- **空格键**：硬降落（直接落到底部）
- **P键**：暂停/继续
- **R键**：重新开始
- **ESC键**：退出游戏

## 📝 开发说明

这个项目展示了Python在不同应用场景中的使用：

1. **GUI应用开发**：使用tkinter构建用户界面
2. **多线程编程**：倒计时工具中的并发处理
3. **游戏开发**：俄罗斯方块的完整游戏逻辑实现
4. **事件驱动编程**：用户交互和界面更新
5. **面向对象设计**：清晰的类结构和模块划分

## 🤝 贡献

欢迎提交问题报告和功能请求。如果您想贡献代码，请：

1. Fork 这个项目
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情（如果存在）。

## 📞 联系方式

如有任何问题或建议，请通过以下方式联系：

- 项目Issues：[GitHub Issues](链接)
- 邮箱：[您的邮箱]

---

**Happy Coding! 🎉**