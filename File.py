import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import time
import threading
import random
import math
import os

# Try to import pygame for MP3 playback
try:
    from pygame import mixer
    mixer.init()
    PYGAME_AVAILABLE = True
except:
    PYGAME_AVAILABLE = False

# ========================= GLOBAL VARIABLES =========================
timer_thread = None
stop_event = threading.Event()
timer_running = False
alarm_playing = False
is_paused = False
remaining_seconds = 0

# Progress bar smooth animation
current_progress = 0.0
target_progress = 0.0

# Custom alarm sound
custom_alarm_file = None

# Theme colors
current_bg_color = [224, 242, 254]  # #e0f2fe (day theme)
target_bg_color = [224, 242, 254]
transition_speed = 2

# Sound settings (for Windows)
try:
    import winsound
    SOUND_AVAILABLE = True
except:
    SOUND_AVAILABLE = False

ALARM_SOUNDS = {
    "🔔 Gentle Beep": (800, 600),
    "⏰ Classic Alarm": (1000, 500),
    "🚨 Urgent Alert": (1500, 300),
    "🎵 Melodic Tone": (1200, 700),
    "💫 Space Beep": (2000, 400),
    "🎧 Custom Sound": None  # For custom MP3
}

# ========================= PARTICLE SYSTEM =========================
class Particle:
    """Advanced particle system for background effects"""
    def __init__(self, canvas, x, y, color, size=3):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-3, -1)
        self.size = size
        self.life = 100
        self.max_life = 100
        self.color = color
        
        self.particle = canvas.create_oval(
            x, y, x + size, y + size,
            fill=color, outline=""
        )
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # Gravity
        self.life -= 2
        
        if self.life <= 0:
            return False
        
        # Fade out effect
        opacity = self.life / self.max_life
        self.canvas.coords(self.particle, self.x, self.y, 
                          self.x + self.size, self.y + self.size)
        return True

# ========================= STAR SYSTEM =========================
class Star:
    """Enhanced star with twinkling effect"""
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.size = random.randint(2, 7)
        self.speed = random.uniform(0.15, 0.6)
        self.direction = random.uniform(-0.25, 0.25)
        self.is_night = False
        
        # Twinkling effect
        self.twinkle_speed = random.uniform(0.02, 0.08)
        self.twinkle_phase = random.uniform(0, math.pi * 2)
        self.base_opacity = random.uniform(0.6, 1.0)
        
        # Day colors (blue tones)
        self.day_colors = ["#bae6fd", "#7dd3fc", "#38bdf8", "#0ea5e9", "#ffffff", "#93c5fd"]
        # Night colors (yellow/gold tones)
        self.night_colors = ["#fef08a", "#fde047", "#facc15", "#eab308", "#ffffff", "#fbbf24", "#fcd34d"]
        
        self.base_color = random.choice(self.day_colors)
        self.current_color = self.base_color
        
        # Create star with glow effect
        self.glow = canvas.create_oval(
            self.x - 2, self.y - 2,
            self.x + self.size + 2, self.y + self.size + 2,
            fill="", outline=self.current_color, width=0
        )
        
        self.star = canvas.create_oval(
            self.x, self.y,
            self.x + self.size, self.y + self.size,
            fill=self.current_color, outline=""
        )
    
    def change_theme(self, is_night):
        """Change star color based on theme"""
        if is_night != self.is_night:
            self.is_night = is_night
            if is_night:
                self.base_color = random.choice(self.night_colors)
            else:
                self.base_color = random.choice(self.day_colors)
    
    def update(self):
        """Update star position and twinkling effect"""
        # Movement
        self.y += self.speed
        self.x += self.direction
        
        # Twinkling effect
        self.twinkle_phase += self.twinkle_speed
        twinkle_factor = (math.sin(self.twinkle_phase) + 1) / 2  # 0 to 1
        opacity = self.base_opacity * (0.3 + 0.7 * twinkle_factor)
        
        # Reset position if out of bounds
        if self.y > self.height + 20:
            self.y = random.randint(-50, -10)
            self.x = random.randint(0, self.width)
            self.direction = random.uniform(-0.25, 0.25)
            if self.is_night:
                self.base_color = random.choice(self.night_colors)
            else:
                self.base_color = random.choice(self.day_colors)
        
        if self.x < -10:
            self.x = self.width + 10
        elif self.x > self.width + 10:
            self.x = -10
        
        # Update position
        self.canvas.coords(self.star, self.x, self.y,
                          self.x + self.size, self.y + self.size)
        self.canvas.coords(self.glow, self.x - 2, self.y - 2,
                          self.x + self.size + 2, self.y + self.size + 2)
        
        # Update color with opacity (simplified)
        self.canvas.itemconfig(self.star, fill=self.base_color)

# ========================= SHOOTING STAR =========================
class ShootingStar:
    """Rare shooting star effect"""
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.x = random.randint(0, width)
        self.y = random.randint(0, height // 2)
        self.vx = random.uniform(3, 6)
        self.vy = random.uniform(1, 3)
        self.length = random.randint(30, 60)
        self.life = 100
        
        self.trail = []
        for i in range(5):
            x2 = self.x - self.vx * (i + 1) * 2
            y2 = self.y - self.vy * (i + 1) * 2
            opacity = 1 - (i / 5)
            color = "#ffffff" if i == 0 else "#fde047"
            
            line = canvas.create_line(
                self.x, self.y, x2, y2,
                fill=color, width=3 - i * 0.5, smooth=True
            )
            self.trail.append(line)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 5
        
        if self.life <= 0:
            for line in self.trail:
                self.canvas.delete(line)
            return False
        
        # Update trail
        for i, line in enumerate(self.trail):
            x2 = self.x - self.vx * (i + 1) * 2
            y2 = self.y - self.vy * (i + 1) * 2
            self.canvas.coords(line, self.x, self.y, x2, y2)
        
        return True

# ========================= SOUND FUNCTIONS =========================
def play_alarm():
    """Play alarm sound with pattern"""
    global alarm_playing
    alarm_playing = True
    
    sound_name = alarm_sound_var.get()
    
    # Check if custom sound is selected
    if sound_name == "🎧 Custom Sound":
        if custom_alarm_file and PYGAME_AVAILABLE:
            def play_custom():
                try:
                    mixer.music.load(custom_alarm_file)
                    mixer.music.play(loops=2)  # Play 3 times
                    while mixer.music.get_busy() and alarm_playing:
                        time.sleep(0.1)
                except Exception as e:
                    print(f"Error playing custom sound: {e}")
                    messagebox.showerror("Error", "Could not play custom sound file!")
            
            threading.Thread(target=play_custom, daemon=True).start()
        else:
            messagebox.showwarning("Warning", "No custom sound file selected or pygame not available!")
        return
    
    # Play built-in beep sounds
    if not SOUND_AVAILABLE:
        return
    
    freq, duration = ALARM_SOUNDS[sound_name]
    
    def alarm_loop():
        for i in range(10):  # Play 10 times
            if not alarm_playing:
                break
            try:
                # Vary frequency for more interesting sound
                varied_freq = freq + (i % 3) * 100
                winsound.Beep(varied_freq, duration)
                time.sleep(0.2)
            except:
                pass
    
    threading.Thread(target=alarm_loop, daemon=True).start()

def stop_alarm():
    """Stop alarm sound"""
    global alarm_playing
    alarm_playing = False
    
    if PYGAME_AVAILABLE:
        try:
            mixer.music.stop()
        except:
            pass

def select_custom_sound():
    """Open file dialog to select custom MP3 alarm"""
    global custom_alarm_file
    
    file_path = filedialog.askopenfilename(
        title="Select Alarm Sound",
        filetypes=[
            ("Audio Files", "*.mp3 *.wav *.ogg"),
            ("MP3 Files", "*.mp3"),
            ("WAV Files", "*.wav"),
            ("All Files", "*.*")
        ]
    )
    
    if file_path:
        custom_alarm_file = file_path
        filename = os.path.basename(file_path)
        custom_sound_label.config(
            text=f"📁 {filename[:30]}..." if len(filename) > 30 else f"📁 {filename}",
            fg="#10b981"
        )
        alarm_sound_var.set("🎧 Custom Sound")
        messagebox.showinfo("Success", f"Custom alarm sound loaded:\n{filename}")

# ========================= TIMER FUNCTIONS =========================
def start_countdown():
    """Start the countdown timer"""
    global timer_thread, timer_running, remaining_seconds, is_paused, target_progress
    
    if timer_running and not is_paused:
        return
    
    if is_paused:
        # Resume from pause
        is_paused = False
        start_button.config(text="⏸️ Pause Timer")
        pause_button.config(state="normal")
        return
    
    try:
        minutes = float(entry_time.get())
        remaining_seconds = int(minutes * 60)
        name = entry_name.get().strip()
        
        if not name:
            messagebox.showwarning("⚠️ Warning", "Please enter your name!")
            return
        
        if remaining_seconds <= 0:
            messagebox.showwarning("⚠️ Warning", "Please enter a valid time!")
            return
        
        stop_event.clear()
        timer_running = True
        is_paused = False
        target_progress = 0
        
        start_button.config(text="⏸️ Pause Timer", state="normal")
        pause_button.config(state="normal")
        reset_button.config(state="normal")
        
        label_status.config(
            text=f"🎮 Hey {name}! Timer started!",
            fg="#10b981"
        )
        
        # Change to night theme
        change_to_night_theme()
        
        def run_timer():
            global timer_running, remaining_seconds, is_paused, target_progress
            
            total_seconds = int(float(entry_time.get()) * 60)
            
            while remaining_seconds >= 0 and not stop_event.is_set():
                if not is_paused:
                    mins, secs = divmod(remaining_seconds, 60)
                    
                    # Color coding based on time remaining
                    if remaining_seconds <= 10:
                        color = "#ef4444"  # Red
                    elif remaining_seconds <= 30:
                        color = "#f59e0b"  # Orange
                    else:
                        color = "#0ea5e9"  # Blue
                    
                    label_timer.config(text=f"{mins:02d}:{secs:02d}", fg=color)
                    
                    # Update target progress for smooth animation
                    target_progress = ((total_seconds - remaining_seconds) / total_seconds) * 100
                    
                    time.sleep(1)
                    remaining_seconds -= 1
                else:
                    time.sleep(0.1)  # Check pause state frequently
            
            if not stop_event.is_set() and remaining_seconds < 0:
                # Timer completed
                target_progress = 100
                label_timer.config(text="00:00", fg="#ef4444")
                label_status.config(
                    text="⏰ WAKE UP NOW!!!",
                    fg="#ef4444"
                )
                
                # Create particle explosion effect
                create_celebration_effect()
                
                play_alarm()
                messagebox.showinfo(
                    "⏰ Wake Up!",
                    f"Time's up {name}! 🎮\nTime to wake up!"
                )
                stop_alarm()
                change_to_day_theme()
            
            timer_running = False
            is_paused = False
            start_button.config(text="▶️ Start Timer", state="normal")
            pause_button.config(state="disabled")
        
        timer_thread = threading.Thread(target=run_timer, daemon=True)
        timer_thread.start()
    
    except ValueError:
        messagebox.showerror("❌ Error", "Please enter a valid number!")

def pause_countdown():
    """Pause/Resume the countdown"""
    global is_paused
    
    if not timer_running:
        return
    
    is_paused = not is_paused
    
    if is_paused:
        start_button.config(text="▶️ Resume Timer")
        label_status.config(text="⏸️ Timer Paused", fg="#f59e0b")
    else:
        start_button.config(text="⏸️ Pause Timer")
        label_status.config(text="⏱️ Timer Running...", fg="#10b981")

def reset_timer():
    """Reset the timer"""
    global timer_running, is_paused, remaining_seconds, current_progress, target_progress
    
    stop_event.set()
    stop_alarm()
    timer_running = False
    is_paused = False
    remaining_seconds = 0
    current_progress = 0.0
    target_progress = 0.0
    progress_bar['value'] = 0
    
    label_timer.config(text="00:00", fg="#0ea5e9")
    label_status.config(text="✨ Ready to start", fg="#64748b")
    
    start_button.config(text="▶️ Start Timer", state="normal")
    pause_button.config(state="disabled")
    reset_button.config(state="normal")
    
    change_to_day_theme()

# ========================= THEME FUNCTIONS =========================
def rgb_to_hex(r, g, b):
    """Convert RGB to hex color"""
    return f'#{int(r):02x}{int(g):02x}{int(b):02x}'

def transition_background():
    """Smoothly transition background color"""
    global current_bg_color
    
    changed = False
    for i in range(3):
        if current_bg_color[i] < target_bg_color[i]:
            current_bg_color[i] = min(
                current_bg_color[i] + transition_speed,
                target_bg_color[i]
            )
            changed = True
        elif current_bg_color[i] > target_bg_color[i]:
            current_bg_color[i] = max(
                current_bg_color[i] - transition_speed,
                target_bg_color[i]
            )
            changed = True
    
    if changed:
        new_color = rgb_to_hex(*current_bg_color)
        canvas_bg.config(bg=new_color)
        root.config(bg=new_color)

def change_to_night_theme():
    """Change to night theme"""
    global target_bg_color
    target_bg_color = [15, 23, 42]  # #0f172a
    for star in stars:
        star.change_theme(True)

def change_to_day_theme():
    """Change to day theme"""
    global target_bg_color
    target_bg_color = [224, 242, 254]  # #e0f2fe
    for star in stars:
        star.change_theme(False)

# ========================= EFFECTS =========================
particles = []
shooting_stars = []

def create_celebration_effect():
    """Create particle celebration effect"""
    center_x = 210
    center_y = 325
    
    colors = ["#fde047", "#facc15", "#fb923c", "#f472b6", "#a78bfa"]
    
    for _ in range(30):
        color = random.choice(colors)
        particle = Particle(canvas_bg, center_x, center_y, color, random.randint(3, 6))
        particles.append(particle)

def update_effects():
    """Update all visual effects"""
    global particles, shooting_stars, current_progress
    
    # Update stars
    for star in stars:
        star.update()
    
    # Update particles
    particles = [p for p in particles if p.update()]
    
    # Update shooting stars
    shooting_stars = [s for s in shooting_stars if s.update()]
    
    # Randomly create shooting stars (rare)
    if random.random() < 0.002 and len(target_bg_color) == 3 and target_bg_color[0] < 100:  # Only at night
        shooting_star = ShootingStar(canvas_bg, 420, 820)
        shooting_stars.append(shooting_star)
    
    # Background transition
    transition_background()
    
    # Smooth progress bar animation
    if abs(current_progress - target_progress) > 0.1:
        # Smooth interpolation
        diff = target_progress - current_progress
        current_progress += diff * 0.15  # Smoothing factor
        progress_bar['value'] = current_progress
    else:
        current_progress = target_progress
        progress_bar['value'] = current_progress
    
    root.after(50, update_effects)

# ========================= PRESET BUTTONS =========================
def set_preset_time(minutes):
    """Set preset time"""
    entry_time.delete(0, tk.END)
    entry_time.insert(0, str(minutes))

# ========================= UI SETUP =========================
root = tk.Tk()
root.title("🎮 Gamer Wake Up Alarm Pro")
root.geometry("420x820")
root.configure(bg="#e0f2fe")
root.resizable(False, False)

# ========================= ANIMATED BACKGROUND =========================
canvas_bg = tk.Canvas(root, width=420, height=820, bg="#e0f2fe", highlightthickness=0)
canvas_bg.place(x=0, y=0)

# Create stars (80 stars for better coverage)
stars = []
for _ in range(80):
    star = Star(canvas_bg, 420, 820)
    stars.append(star)

# ========================= MAIN CARD =========================
# Shadow
shadow = tk.Frame(root, bg="#bae6fd")
shadow.place(relx=0.5, rely=0.5, anchor="center", width=390, height=770)

# Main card
card = tk.Frame(root, bg="white", bd=0, highlightthickness=0)
card.place(relx=0.5, rely=0.5, anchor="center", width=385, height=765)

card.lift()

# ========================= HEADER =========================
header_frame = tk.Frame(card, bg="#0ea5e9", height=80)
header_frame.pack(fill="x")
header_frame.pack_propagate(False)

tk.Label(
    header_frame,
    text="🎮 Gamer Wake Up Alarm",
    font=("Segoe UI", 22, "bold"),
    bg="#0ea5e9",
    fg="white"
).pack(pady=25)

# ========================= CONTENT =========================
content = tk.Frame(card, bg="white")
content.pack(fill="both", expand=True, padx=25, pady=15)

# Name input
tk.Label(
    content,
    text="👤 Your Name",
    font=("Segoe UI", 11, "bold"),
    bg="white",
    fg="#334155"
).pack(anchor="w", pady=(0, 6))

entry_name = tk.Entry(
    content,
    font=("Segoe UI", 13),
    bd=0,
    relief="flat",
    bg="#f8fafc",
    fg="#0f172a",
    highlightthickness=2,
    highlightbackground="#e2e8f0",
    highlightcolor="#0ea5e9"
)
entry_name.pack(fill="x", ipady=10, pady=(0, 12))

# Time input
time_frame = tk.Frame(content, bg="white")
time_frame.pack(fill="x", pady=(0, 10))

tk.Label(
    time_frame,
    text="⏱ Set Time (Minutes)",
    font=("Segoe UI", 11, "bold"),
    bg="white",
    fg="#334155"
).pack(side="left")

# Preset buttons
preset_frame = tk.Frame(time_frame, bg="white")
preset_frame.pack(side="right")

for minutes in [0.1, 1, 5, 10]:
    label = "6s" if minutes == 0.1 else f"{int(minutes)}m"
    btn = tk.Button(
        preset_frame,
        text=label,
        command=lambda m=minutes: set_preset_time(m),
        bg="#e0f2fe",
        fg="#0369a1",
        font=("Segoe UI", 9, "bold"),
        bd=0,
        relief="flat",
        padx=8,
        pady=3,
        cursor="hand2"
    )
    btn.pack(side="left", padx=2)

entry_time = tk.Entry(
    content,
    font=("Segoe UI", 13),
    bd=0,
    relief="flat",
    bg="#f8fafc",
    fg="#0f172a",
    highlightthickness=2,
    highlightbackground="#e2e8f0",
    highlightcolor="#0ea5e9"
)
entry_time.pack(fill="x", ipady=10, pady=(8, 12))

# Alarm sound selector
tk.Label(
    content,
    text="🔊 Alarm Sound",
    font=("Segoe UI", 11, "bold"),
    bg="white",
    fg="#334155"
).pack(anchor="w", pady=(0, 6))

alarm_sound_var = tk.StringVar(value="⏰ Classic Alarm")
alarm_dropdown = ttk.Combobox(
    content,
    textvariable=alarm_sound_var,
    values=list(ALARM_SOUNDS.keys()),
    font=("Segoe UI", 11),
    state="readonly"
)
alarm_dropdown.pack(fill="x", ipady=6, pady=(0, 6))

# Custom sound selector
custom_sound_frame = tk.Frame(content, bg="white")
custom_sound_frame.pack(fill="x", pady=(0, 12))

custom_sound_button = tk.Button(
    custom_sound_frame,
    text="📁 Load Custom Sound (MP3/WAV)",
    command=select_custom_sound,
    bg="#f0f9ff",
    fg="#0369a1",
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    bd=1,
    cursor="hand2",
    activebackground="#e0f2fe"
)
custom_sound_button.pack(side="left", padx=(0, 10))

custom_sound_label = tk.Label(
    custom_sound_frame,
    text="No file selected",
    font=("Segoe UI", 9),
    bg="white",
    fg="#94a3b8"
)
custom_sound_label.pack(side="left")

# Timer display
timer_container = tk.Frame(content, bg="#f0f9ff", bd=0, 
                           highlightthickness=2, highlightbackground="#bae6fd")
timer_container.pack(fill="x", pady=(0, 8))

label_timer = tk.Label(
    timer_container,
    text="00:00",
    font=("Segoe UI", 48, "bold"),
    bg="#f0f9ff",
    fg="#0ea5e9"
)
label_timer.pack(pady=20)

# Progress bar
progress_bar = ttk.Progressbar(
    content,
    orient="horizontal",
    length=335,
    mode="determinate",
    style="Custom.Horizontal.TProgressbar"
)
progress_bar.pack(fill="x", pady=(0, 10))
progress_bar['value'] = 0

# Status label
label_status = tk.Label(
    content,
    text="✨ Ready to start",
    font=("Segoe UI", 11, "bold"),
    bg="white",
    fg="#64748b"
)
label_status.pack(pady=(5, 12))

# Buttons
btn_container = tk.Frame(content, bg="white")
btn_container.pack(pady=(5, 8))

start_button = tk.Button(
    btn_container,
    text="▶️ Start Timer",
    command=start_countdown,
    bg="#0ea5e9",
    fg="white",
    font=("Segoe UI", 12, "bold"),
    width=13,
    relief="flat",
    bd=0,
    cursor="hand2",
    activebackground="#0284c7",
    activeforeground="white"
)
start_button.grid(row=0, column=0, padx=5, ipady=12)

pause_button = tk.Button(
    btn_container,
    text="⏸️ Pause Timer",
    command=pause_countdown,
    bg="#f59e0b",
    fg="white",
    font=("Segoe UI", 12, "bold"),
    width=13,
    relief="flat",
    bd=0,
    cursor="hand2",
    activebackground="#d97706",
    activeforeground="white",
    state="disabled"
)
pause_button.grid(row=0, column=1, padx=5, ipady=12)

reset_button = tk.Button(
    btn_container,
    text="↻ Reset Timer",
    command=reset_timer,
    bg="#64748b",
    fg="white",
    font=("Segoe UI", 12, "bold"),
    width=28,
    relief="flat",
    bd=0,
    cursor="hand2",
    activebackground="#475569",
    activeforeground="white"
)
reset_button.grid(row=1, column=0, columnspan=2, pady=(10, 0), ipady=12)

# Hover effects
def create_hover_effect(button, normal_color, hover_color):
    def on_enter(e):
        if button['state'] != 'disabled':
            button.config(bg=hover_color)
    
    def on_leave(e):
        if button['state'] != 'disabled':
            button.config(bg=normal_color)
    
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)

create_hover_effect(start_button, "#0ea5e9", "#0284c7")
create_hover_effect(pause_button, "#f59e0b", "#d97706")
create_hover_effect(reset_button, "#64748b", "#475569")

# Footer
footer = tk.Label(
    content,
    text="Made with 💙 for Gamers",
    font=("Segoe UI", 9),
    bg="white",
    fg="#94a3b8"
)
footer.pack(side="bottom", pady=(10, 0))

# ========================= STYLE =========================
style = ttk.Style()
style.theme_use('default')
style.configure(
    "Custom.Horizontal.TProgressbar",
    troughcolor='#e2e8f0',
    background='#0ea5e9',
    bordercolor='#e2e8f0',
    lightcolor='#0ea5e9',
    darkcolor='#0284c7'
)

# ========================= START ANIMATION =========================
update_effects()

# ========================= RUN =========================
root.mainloop()
