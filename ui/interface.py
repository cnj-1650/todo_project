import customtkinter as ctk # type: ignore
import pygame # type: ignore
import random
import os
from backend.logic import TaskManager

# --- FOCUS TIMER WINDOW ---
class TimerWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Focus Timer")
        self.geometry("320x450")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        
        pygame.mixer.init()
        self.presets = {"Focus": 1500, "Short Break": 300, "Long Break": 900}
        self.current_sec = 1500
        self.running = False
        self.timer_id = None
        self.mode = "Focus"

        # UI Components
        self.mode_switch = ctk.CTkSegmentedButton(self, values=["Focus", "Short Break", "Long Break"], 
                                                command=self.change_mode)
        self.mode_switch.set("Focus")
        self.mode_switch.pack(pady=25, padx=20)

        self.label = ctk.CTkLabel(self, text="25:00", font=("Roboto", 70, "bold"))
        self.label.pack(pady=10)

        self.progress = ctk.CTkProgressBar(self, width=240, height=10)
        self.progress.set(1.0)
        self.progress.pack(pady=20)

        self.btn = ctk.CTkButton(self, text="START", font=("Roboto", 16, "bold"), height=45, 
                                corner_radius=20, command=self.toggle)
        self.btn.pack(pady=15, padx=50, fill="x")

        ctk.CTkButton(self, text="Reset", fg_color="transparent", border_width=1, 
                     command=self.reset).pack()

    def change_mode(self, mode):
        self.stop()
        self.mode = mode
        self.current_sec = self.presets[mode]
        self.update_label()
        self.progress.set(1.0)

    def update_label(self):
        m, s = divmod(self.current_sec, 60)
        self.label.configure(text=f"{m:02d}:{s:02d}")

    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.running = True
            self.btn.configure(text="PAUSE", fg_color="#e74c3c")
            self.tick()

    def stop(self):
        self.running = False
        self.btn.configure(text="START", fg_color="#3b8ed0")
        if self.timer_id: self.after_cancel(self.timer_id)

    def tick(self):
        if self.running and self.current_sec > 0:
            self.current_sec -= 1
            self.update_label()
            self.progress.set(self.current_sec / self.presets[self.mode])
            self.timer_id = self.after(1000, self.tick)
        elif self.current_sec == 0:
            self.alarm()

    def alarm(self):
        self.stop()
        try:
            # Flashing visual cue
            self.label.configure(text_color="#e74c3c")
            # Sound cue
            if os.path.exists("alarm.wav"):
                pygame.mixer.music.load("alarm.wav")
                pygame.mixer.music.play()
            else:
                self.bell()
        except: pass

    def reset(self):
        self.change_mode(self.mode)
        self.label.configure(text_color=("black", "white"))

# --- SETTINGS WINDOW ---
class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Settings")
        self.geometry("300x250")
        self.attributes("-topmost", True)
        
        ctk.CTkLabel(self, text="Appearance Mode", font=("Roboto", 16, "bold")).pack(pady=15)
        self.theme_opt = ctk.CTkOptionMenu(self, values=["System", "Dark", "Light"], 
                                         command=self.change_theme)
        self.theme_opt.set(parent.manager.settings.get("theme", "System"))
        self.theme_opt.pack(pady=10)
        
        ctk.CTkLabel(self, text="Data Management", font=("Roboto", 14)).pack(pady=(15, 5))
        ctk.CTkButton(self, text="Clear Completed Tasks", fg_color="#e74c3c", 
                     hover_color="#c0392b", command=self.clear).pack(pady=10)

    def change_theme(self, mode):
        ctk.set_appearance_mode(mode)
        self.parent.manager.set_theme(mode)

    def clear(self):
        self.parent.manager.clear_completed()
        self.parent.refresh_list()
        self.destroy()

# --- FLAPPY BIRD ENGINE ---
class FlappyBird:
    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((400, 600))
        clock = pygame.time.Clock()
        bird = pygame.Rect(50, 300, 30, 30)
        gravity, movement, score = 0.25, 0, 0
        pipes = []
        SPAWN = pygame.USEREVENT
        pygame.time.set_timer(SPAWN, 1200)
        active = True

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if active: movement = -6
                    else: active = True; pipes.clear(); bird.y = 300; movement = 0; score = 0
                if event.type == SPAWN and active:
                    h = random.randint(150, 400)
                    pipes.append(pygame.Rect(450, h, 60, 600))
                    pipes.append(pygame.Rect(450, 0, 60, h-150))

            screen.fill((52, 152, 219))
            if active:
                movement += gravity
                bird.y += movement
                pygame.draw.rect(screen, (241, 196, 15), bird)
                for p in pipes:
                    p.x -= 3
                    pygame.draw.rect(screen, (46, 204, 113), p)
                    if bird.colliderect(p): active = False
                pipes = [p for p in pipes if p.right > -50]
                if bird.top <= 0 or bird.bottom >= 600: active = False
                score += 0.01
            else:
                f = pygame.font.SysFont("Arial", 30)
                screen.blit(f.render(f"Score: {int(score)}", True, (255,255,255)), (140, 250))
            
            pygame.display.update()
            clock.tick(120)

# --- MAIN APPLICATION ---
class TodoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.manager = TaskManager()
        ctk.set_appearance_mode(self.manager.settings.get("theme", "System"))
        
        self.title("Task Master Pro")
        self.geometry("480x750")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        # Header Area
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        ctk.CTkLabel(head, text="Dashboard", font=("Roboto", 32, "bold")).pack(side="left")
        
        # Header Icons
        btn_config = {"width": 40, "fg_color": ("gray85", "gray25"), "text_color": ("black", "white")}
        ctk.CTkButton(head, text="⚙", command=lambda: SettingsWindow(self), **btn_config).pack(side="right", padx=2)
        ctk.CTkButton(head, text="⏱", command=lambda: TimerWindow(self), **btn_config).pack(side="right", padx=2)
        ctk.CTkButton(head, text="🎮", hover_color="#f1c40f", command=lambda: FlappyBird().run(), **btn_config).pack(side="right", padx=2)

        # Progress Card
        self.card = ctk.CTkFrame(self, corner_radius=15, fg_color=("gray90", "gray15"))
        self.card.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        self.stats = ctk.CTkLabel(self.card, text="0/0 Completed", font=("Roboto", 14))
        self.stats.pack(pady=(10, 0))
        self.prog = ctk.CTkProgressBar(self.card, height=12)
        self.prog.pack(fill="x", padx=20, pady=15)

        # Search Bar
        self.search = ctk.CTkEntry(self, placeholder_text="🔍 Search tasks...", height=35, corner_radius=10)
        self.search.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        self.search.bind("<KeyRelease>", lambda e: self.refresh_list())

        # Input Area
        entry_f = ctk.CTkFrame(self, fg_color="transparent")
        entry_f.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        self.entry = ctk.CTkEntry(entry_f, placeholder_text="What needs to be done?", height=45, corner_radius=10)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.prio = ctk.CTkOptionMenu(entry_f, values=["Low", "Medium", "High"], width=100, height=45)
        self.prio.set("Medium")
        self.prio.pack(side="left", padx=(0, 10))
        ctk.CTkButton(entry_f, text="+", width=50, height=45, corner_radius=10, 
                     font=("Roboto", 24), command=self.add).pack(side="right")

        # Task List
        self.scroll = ctk.CTkScrollableFrame(self, label_text="My Tasks", corner_radius=15)
        self.scroll.grid(row=4, column=0, sticky="nsew", padx=20, pady=(10, 20))
        self.scroll.grid_columnconfigure(0, weight=1)

    def refresh_list(self):
        done, total, per = self.manager.get_stats()
        self.stats.configure(text=f"{done}/{total} Tasks Completed ({int(per*100)}%)")
        self.prog.set(per)

        for w in self.scroll.winfo_children(): w.destroy()
        
        tasks = self.manager.filter_tasks(self.search.get())
        for i, t in enumerate(tasks):
            self.create_task_row(i, t)

    def create_task_row(self, i, t):
        row = ctk.CTkFrame(self.scroll, fg_color=("gray95", "gray20"), corner_radius=10)
        row.grid(row=i, column=0, sticky="ew", pady=5, padx=2)
        
        p_color = {"High": "#ff4d4d", "Medium": "#ffa500", "Low": "#2ecc71"}[t.get('priority', 'Medium')]
        ctk.CTkFrame(row, width=4, height=30, fg_color=p_color).pack(side="left", padx=5, pady=5)
        
        font = ("Roboto", 14, "overstrike") if t['completed'] else ("Roboto", 14)
        cb = ctk.CTkCheckBox(row, text=t['title'], font=font, command=lambda idx=i: self.toggle(idx))
        if t['completed']: cb.select()
        cb.pack(side="left", padx=10, fill="x", expand=True)
        
        ctk.CTkButton(row, text="×", width=30, height=30, fg_color="transparent", text_color="gray", 
                     hover_color="#e74c3c", command=lambda idx=i: self.delete(idx)).pack(side="right", padx=5)

    def add(self):
        if self.manager.add_task(self.entry.get(), self.prio.get()):
            self.entry.delete(0, 'end')
            self.refresh_list()

    def toggle(self, i):
        self.manager.toggle_complete(i)
        self.refresh_list()

    def delete(self, i):
        self.manager.delete_task(i)
        self.refresh_list()