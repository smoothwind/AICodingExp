import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import uuid
from datetime import datetime

class TimerTask:
    """Individual timer task class"""
    def __init__(self, name, hours, minutes, seconds, task_id=None):
        self.id = task_id or str(uuid.uuid4())[:8]
        self.name = name
        self.total_seconds = hours * 3600 + minutes * 60 + seconds
        self.remaining_seconds = self.total_seconds
        self.is_running = False
        self.is_paused = False
        self.is_completed = False
        self.created_time = datetime.now()
        self.thread = None

class CountdownTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("多任务倒计时工具")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        # Set window icon and styling
        self.root.configure(bg='#2c3e50')

        # Timer management
        self.timers = {}
        self.active_timers = set()

        # Create GUI elements
        self.create_widgets()

    def create_widgets(self):
        # Main container with paned window
        main_paned = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top frame for adding new timers
        top_frame = tk.Frame(main_paned, bg='#34495e')
        main_paned.add(top_frame, weight=1)

        # Title
        title_label = tk.Label(
            top_frame,
            text="⏰ 多任务倒计时工具",
            font=("Arial", 24, "bold"),
            fg='#ecf0f1',
            bg='#34495e'
        )
        title_label.pack(pady=15)

        # Add timer section
        add_timer_frame = tk.LabelFrame(
            top_frame,
            text="添加新计时器",
            font=("Arial", 14, "bold"),
            fg='#ecf0f1',
            bg='#34495e'
        )
        add_timer_frame.pack(pady=10, padx=20, fill='x')

        # Task name input
        name_frame = tk.Frame(add_timer_frame, bg='#34495e')
        name_frame.pack(pady=5, padx=10, fill='x')

        tk.Label(
            name_frame,
            text="任务名称：",
            font=("Arial", 12),
            fg='#ecf0f1',
            bg='#34495e'
        ).pack(side=tk.LEFT, padx=5)

        self.task_name_var = tk.StringVar(value=f"任务 {len(self.timers) + 1}")
        self.task_name_entry = tk.Entry(
            name_frame,
            textvariable=self.task_name_var,
            font=("Arial", 12),
            width=20
        )
        self.task_name_entry.pack(side=tk.LEFT, padx=5)

        # Time input frame
        time_input_frame = tk.Frame(add_timer_frame, bg='#34495e')
        time_input_frame.pack(pady=5, padx=10, fill='x')

        # Hours
        tk.Label(
            time_input_frame,
            text="小时",
            font=("Arial", 12),
            fg='#ecf0f1',
            bg='#34495e'
        ).grid(row=0, column=0, padx=10)
        self.hours_var = tk.StringVar(value="0")
        hours_spinbox = tk.Spinbox(
            time_input_frame,
            from_=0,
            to=23,
            width=5,
            textvariable=self.hours_var,
            font=("Arial", 16),
            justify='center'
        )
        hours_spinbox.grid(row=1, column=0, padx=10)

        # Minutes
        tk.Label(
            time_input_frame,
            text="分钟",
            font=("Arial", 12),
            fg='#ecf0f1',
            bg='#34495e'
        ).grid(row=0, column=1, padx=10)
        self.minutes_var = tk.StringVar(value="0")
        minutes_spinbox = tk.Spinbox(
            time_input_frame,
            from_=0,
            to=59,
            width=5,
            textvariable=self.minutes_var,
            font=("Arial", 16),
            justify='center'
        )
        minutes_spinbox.grid(row=1, column=1, padx=10)

        # Seconds
        tk.Label(
            time_input_frame,
            text="秒",
            font=("Arial", 12),
            fg='#ecf0f1',
            bg='#34495e'
        ).grid(row=0, column=2, padx=10)
        self.seconds_var = tk.StringVar(value="0")
        seconds_spinbox = tk.Spinbox(
            time_input_frame,
            from_=0,
            to=59,
            width=5,
            textvariable=self.seconds_var,
            font=("Arial", 16),
            justify='center'
        )
        seconds_spinbox.grid(row=1, column=2, padx=10)

        # Add button
        self.add_button = tk.Button(
            time_input_frame,
            text="添加计时器",
            command=self.add_timer,
            font=("Arial", 14),
            bg='#27ae60',
            fg='white',
            width=12,
            height=2
        )
        self.add_button.grid(row=1, column=3, padx=20)

        # Quick set buttons
        quick_frame = tk.Frame(add_timer_frame, bg='#34495e')
        quick_frame.pack(pady=5, padx=10, fill='x')

        tk.Label(
            quick_frame,
            text="快速设置：",
            font=("Arial", 11),
            fg='#ecf0f1',
            bg='#34495e'
        ).pack(side=tk.LEFT, padx=5)

        quick_buttons_frame = tk.Frame(quick_frame, bg='#34495e')
        quick_buttons_frame.pack(side=tk.LEFT)

        quick_times = [
            ("30秒", "0", "0", "30"),
            ("1分钟", "0", "1", "0"),
            ("5分钟", "0", "5", "0"),
            ("10分钟", "0", "10", "0"),
            ("15分钟", "0", "15", "0"),
            ("30分钟", "0", "30", "0"),
            ("1小时", "1", "0", "0"),
            ("2小时", "2", "0", "0")
        ]

        for i, (text, h, m, s) in enumerate(quick_times):
            btn = tk.Button(
                quick_buttons_frame,
                text=text,
                command=lambda h=h, m=m, s=s: self.set_quick_time(h, m, s),
                font=("Arial", 10),
                bg='#95a5a6',
                fg='white',
                width=8
            )
            btn.grid(row=0, column=i, padx=2)

        # Bottom frame for timer list
        bottom_frame = tk.Frame(main_paned, bg='#2c3e50')
        main_paned.add(bottom_frame, weight=3)

        # Timer list section
        list_frame = tk.LabelFrame(
            bottom_frame,
            text="计时器列表",
            font=("Arial", 14, "bold"),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        list_frame.pack(pady=10, padx=10, fill='both', expand=True)

        # Create scrollable frame for timers
        self.create_timer_list(list_frame)

        # Control buttons for all timers
        control_frame = tk.Frame(bottom_frame, bg='#2c3e50')
        control_frame.pack(pady=10)

        self.start_all_button = tk.Button(
            control_frame,
            text="全部开始",
            command=self.start_all_timers,
            font=("Arial", 12),
            bg='#27ae60',
            fg='white',
            width=12
        )
        self.start_all_button.pack(side=tk.LEFT, padx=5)

        self.pause_all_button = tk.Button(
            control_frame,
            text="全部暂停",
            command=self.pause_all_timers,
            font=("Arial", 12),
            bg='#f39c12',
            fg='white',
            width=12
        )
        self.pause_all_button.pack(side=tk.LEFT, padx=5)

        self.reset_all_button = tk.Button(
            control_frame,
            text="全部重置",
            command=self.reset_all_timers,
            font=("Arial", 12),
            bg='#e74c3c',
            fg='white',
            width=12
        )
        self.reset_all_button.pack(side=tk.LEFT, padx=5)

        self.clear_completed_button = tk.Button(
            control_frame,
            text="清除已完成",
            command=self.clear_completed_timers,
            font=("Arial", 12),
            bg='#8e44ad',
            fg='white',
            width=12
        )
        self.clear_completed_button.pack(side=tk.LEFT, padx=5)

    def create_timer_list(self, parent):
        """Create scrollable frame for timer list"""
        # Canvas and scrollbar
        canvas = tk.Canvas(parent, bg='#2c3e50', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='#2c3e50')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        # Timer display containers
        self.timer_displays = {}

    def set_quick_time(self, hours, minutes, seconds):
        """Set time from quick buttons"""
        self.hours_var.set(hours)
        self.minutes_var.set(minutes)
        self.seconds_var.set(seconds)

    def add_timer(self):
        """Add a new timer task"""
        try:
            hours = int(self.hours_var.get())
            minutes = int(self.minutes_var.get())
            seconds = int(self.seconds_var.get())
            name = self.task_name_var.get().strip()

            if not name:
                messagebox.showwarning("警告", "请输入任务名称！")
                return

            total_seconds = hours * 3600 + minutes * 60 + seconds
            if total_seconds <= 0:
                messagebox.showwarning("警告", "请设置有效的倒计时时间！")
                return

            # Create new timer task
            timer = TimerTask(name, hours, minutes, seconds)
            self.timers[timer.id] = timer

            # Create display for this timer
            self.create_timer_display(timer)

            # Reset input fields
            self.hours_var.set("0")
            self.minutes_var.set("0")
            self.seconds_var.set("0")
            self.task_name_var.set(f"任务 {len(self.timers) + 1}")

        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字！")

    def create_timer_display(self, timer):
        """Create display for a single timer"""
        # Timer frame
        timer_frame = tk.Frame(self.scrollable_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        timer_frame.pack(pady=5, padx=10, fill='x')

        # Timer info
        info_frame = tk.Frame(timer_frame, bg='#34495e')
        info_frame.pack(fill='x', padx=10, pady=5)

        # Timer name
        name_label = tk.Label(
            info_frame,
            text=f"🔸 {timer.name}",
            font=("Arial", 14, "bold"),
            fg='#ecf0f1',
            bg='#34495e'
        )
        name_label.pack(side=tk.LEFT)

        # Timer ID (small)
        id_label = tk.Label(
            info_frame,
            text=f"ID: {timer.id}",
            font=("Arial", 9),
            fg='#95a5a6',
            bg='#34495e'
        )
        id_label.pack(side=tk.RIGHT)

        # Time display
        time_frame = tk.Frame(timer_frame, bg='#34495e')
        time_frame.pack(pady=5)

        time_label = tk.Label(
            time_frame,
            text="00:00:00",
            font=("Digital-7", 28),
            fg='#3498db',
            bg='#34495e'
        )
        time_label.pack()

        # Progress bar
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            time_frame,
            variable=progress_var,
            maximum=100,
            length=300
        )
        progress_bar.pack(pady=5)

        # Control buttons
        control_frame = tk.Frame(timer_frame, bg='#34495e')
        control_frame.pack(pady=5)

        start_btn = tk.Button(
            control_frame,
            text="开始",
            command=lambda t=timer: self.start_single_timer(t),
            font=("Arial", 10),
            bg='#27ae60',
            fg='white',
            width=8
        )
        start_btn.pack(side=tk.LEFT, padx=2)

        pause_btn = tk.Button(
            control_frame,
            text="暂停",
            command=lambda t=timer: self.pause_single_timer(t),
            font=("Arial", 10),
            bg='#f39c12',
            fg='white',
            width=8,
            state=tk.DISABLED
        )
        pause_btn.pack(side=tk.LEFT, padx=2)

        reset_btn = tk.Button(
            control_frame,
            text="重置",
            command=lambda t=timer: self.reset_single_timer(t),
            font=("Arial", 10),
            bg='#e74c3c',
            fg='white',
            width=8
        )
        reset_btn.pack(side=tk.LEFT, padx=2)

        delete_btn = tk.Button(
            control_frame,
            text="删除",
            command=lambda t=timer: self.delete_timer(t),
            font=("Arial", 10),
            bg='#c0392b',
            fg='white',
            width=8
        )
        delete_btn.pack(side=tk.LEFT, padx=2)

        # Store display elements
        self.timer_displays[timer.id] = {
            'frame': timer_frame,
            'time_label': time_label,
            'progress_var': progress_var,
            'progress_bar': progress_bar,
            'start_btn': start_btn,
            'pause_btn': pause_btn,
            'reset_btn': reset_btn,
            'delete_btn': delete_btn
        }

    def start_single_timer(self, timer):
        """Start a single timer"""
        if timer.is_completed:
            timer.is_completed = False
            timer.remaining_seconds = timer.total_seconds

        timer.is_running = True
        timer.is_paused = False
        self.active_timers.add(timer.id)

        # Update button states
        display = self.timer_displays[timer.id]
        display['start_btn'].config(state=tk.DISABLED)
        display['pause_btn'].config(state=tk.NORMAL, text="暂停")
        display['delete_btn'].config(state=tk.DISABLED)

        # Start timer thread
        timer.thread = threading.Thread(target=self.run_timer, args=(timer,))
        timer.thread.daemon = True
        timer.thread.start()

    def pause_single_timer(self, timer):
        """Pause/resume a single timer"""
        if timer.is_running:
            timer.is_paused = not timer.is_paused
            display = self.timer_displays[timer.id]

            if timer.is_paused:
                display['pause_btn'].config(text="继续", bg='#27ae60')
            else:
                display['pause_btn'].config(text="暂停", bg='#f39c12')

    def reset_single_timer(self, timer):
        """Reset a single timer"""
        timer.is_running = False
        timer.is_paused = False
        timer.is_completed = False
        timer.remaining_seconds = timer.total_seconds
        self.active_timers.discard(timer.id)

        # Update display
        self.update_timer_display(timer)

        # Update button states
        display = self.timer_displays[timer.id]
        display['start_btn'].config(state=tk.NORMAL)
        display['pause_btn'].config(state=tk.DISABLED, text="暂停", bg='#f39c12')
        display['delete_btn'].config(state=tk.NORMAL)

    def delete_timer(self, timer):
        """Delete a timer"""
        if timer.is_running:
            if messagebox.askyesno("确认", "计时器正在运行，确定要删除吗？"):
                timer.is_running = False
                self.active_timers.discard(timer.id)
        else:
            if not messagebox.askyesno("确认", f"确定要删除计时器 '{timer.name}' 吗？"):
                return

        # Remove display
        display = self.timer_displays[timer.id]
        display['frame'].destroy()
        del self.timer_displays[timer.id]

        # Remove timer
        del self.timers[timer.id]

    def start_all_timers(self):
        """Start all non-completed timers"""
        for timer in self.timers.values():
            if not timer.is_completed and not timer.is_running:
                self.start_single_timer(timer)

    def pause_all_timers(self):
        """Pause/resume all running timers"""
        for timer in self.timers.values():
            if timer.is_running:
                self.pause_single_timer(timer)

    def reset_all_timers(self):
        """Reset all timers"""
        for timer in self.timers.values():
            self.reset_single_timer(timer)

    def clear_completed_timers(self):
        """Clear all completed timers"""
        completed_timers = [t for t in self.timers.values() if t.is_completed]

        if not completed_timers:
            messagebox.showinfo("提示", "没有已完成的计时器")
            return

        if messagebox.askyesno("确认", f"确定要清除 {len(completed_timers)} 个已完成的计时器吗？"):
            for timer in completed_timers:
                self.delete_timer(timer)

    def run_timer(self, timer):
        """Run a timer in a separate thread"""
        while timer.is_running and timer.remaining_seconds > 0:
            if not timer.is_paused:
                # Update display
                self.root.after(0, self.update_timer_display, timer)

                # Decrement time
                timer.remaining_seconds -= 1
                time.sleep(1)
            else:
                time.sleep(0.1)

        # Timer completed
        if timer.remaining_seconds <= 0:
            self.root.after(0, self.timer_completed, timer)

    def update_timer_display(self, timer):
        """Update the display for a specific timer"""
        if timer.id not in self.timer_displays:
            return

        display = self.timer_displays[timer.id]

        hours = timer.remaining_seconds // 3600
        minutes = (timer.remaining_seconds % 3600) // 60
        seconds = timer.remaining_seconds % 60

        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        display['time_label'].config(text=time_str)

        # Update progress bar
        if timer.total_seconds > 0:
            progress = ((timer.total_seconds - timer.remaining_seconds) / timer.total_seconds) * 100
            display['progress_var'].set(progress)

        # Change color when less than 10 seconds
        if timer.remaining_seconds <= 10 and timer.remaining_seconds > 0:
            display['time_label'].config(fg='#e74c3c')
        elif timer.is_paused:
            display['time_label'].config(fg='#f39c12')
        elif timer.is_running:
            display['time_label'].config(fg='#3498db')
        else:
            display['time_label'].config(fg='#27ae60')

    def timer_completed(self, timer):
        """Handle timer completion"""
        timer.is_running = False
        timer.is_completed = True
        self.active_timers.discard(timer.id)

        # Update display
        self.update_timer_display(timer)

        # Update button states
        display = self.timer_displays[timer.id]
        display['start_btn'].config(state=tk.NORMAL, text="重新开始")
        display['pause_btn'].config(state=tk.DISABLED, text="暂停", bg='#f39c12')
        display['delete_btn'].config(state=tk.NORMAL)

        # Show completion message with name
        self.root.after(0, lambda: messagebox.showinfo("时间到！", f"任务 '{timer.name}' 已完成！"))

        # Flash the display
        for _ in range(3):
            if timer.id in self.timer_displays:
                self.timer_displays[timer.id]['time_label'].config(fg='#ffffff')
                self.root.update()
                time.sleep(0.2)
                self.timer_displays[timer.id]['time_label'].config(fg='#e74c3c')
                self.root.update()
                time.sleep(0.2)

def main():
    root = tk.Tk()
    app = CountdownTimer(root)
    root.mainloop()

if __name__ == "__main__":
    main()