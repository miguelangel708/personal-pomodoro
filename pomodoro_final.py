#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
import subprocess
import csv
import json
from pathlib import Path
from datetime import datetime

# Usar directorio home del usuario para archivos
DATA_DIR = Path.home() / ".pomodoro"
DATA_DIR.mkdir(exist_ok=True)
CONFIG_FILE = DATA_DIR / "pomodoro_config.json"
DATA_FILE = DATA_DIR / "pomodoro_data.csv"

DEFAULT_CONFIG = {
    "pomodoro_minutes": 0.5,
    "break_minutes": 0.2,
    "daily_goal": 8,
    "idle_threshold": 60,
    "transparency": 0.9
}

class Pomodoro:
    def __init__(self):
        self.config = self.load_config()
        
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", self.config.get("transparency", 0.9))
        
        # Posicionar usando posición guardada o por defecto
        if "window_x" in self.config and "window_y" in self.config:
            x_pos = self.config["window_x"]
            y_pos = self.config["window_y"]
        else:
            screen_width = self.root.winfo_screenwidth()
            x_pos = screen_width - 200
            y_pos = 40
        
        self.root.wm_geometry(f"+{x_pos}+{y_pos}")
        
        # Hacer que aparezca en todos los escritorios/Spaces de macOS
        try:
            subprocess.run([
                "osascript", "-e",
                'tell application "System Events" to set visible of every window of (every process whose name is "Python") to true'
            ], check=False)
        except:
            pass
        
        frame = tk.Frame(self.root, bg="#2d2d2d")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Columna izquierda: tiempos
        left_frame = tk.Frame(frame, bg="#2d2d2d")
        left_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.label = tk.Label(
            left_frame,
            text="00:00 | P:0/8",
            font=("Menlo", 12),
            bg="#2d2d2d",
            fg="#00ff00",
            padx=4,
            pady=4
        )
        self.label.pack()
        
        self.break_label = tk.Label(
            left_frame,
            text="Descanso: 00:00",
            font=("Menlo", 10),
            bg="#2d2d2d",
            fg="#ffaa00",
            padx=4,
            pady=2
        )
        self.break_label.pack()
        
        # Botón para expandir tareas
        self.tasks_toggle_btn = tk.Button(
            left_frame,
            text="▼ Tareas",
            font=("Menlo", 9),
            bg="#2d2d2d",
            fg="#888888",
            bd=0,
            command=self.toggle_tasks_panel,
            cursor="hand2"
        )
        self.tasks_toggle_btn.pack(pady=(5, 0))
        
        # Columna derecha: botones verticales
        btn_container = tk.Frame(frame, bg="#2d2d2d")
        btn_container.pack(side=tk.RIGHT, padx=5, pady=5)
        
        stats_btn = tk.Button(
            btn_container,
            text="📊",
            font=("Arial", 10),
            bg="#3d3d3d",
            fg="#888888",
            bd=0,
            width=2,
            height=1,
            relief="flat",
            command=self.open_stats,
            cursor="hand2"
        )
        stats_btn.pack(pady=2)
        
        btn = tk.Button(
            btn_container,
            text="⚙",
            font=("Arial", 10),
            bg="#3d3d3d",
            fg="#888888",
            bd=0,
            width=2,
            height=1,
            relief="flat",
            command=self.open_settings,
            cursor="hand2"
        )
        btn.pack(pady=2)
        
        self.break_btn = tk.Button(
            btn_container,
            text="☕",
            font=("Arial", 10),
            bg="#3d3d3d",
            fg="#ffaa00",
            bd=0,
            width=2,
            height=1,
            relief="flat",
            command=self.toggle_break,
            cursor="hand2"
        )
        self.break_btn.pack(pady=2)
        
        self.play_btn = tk.Button(
            btn_container,
            text="▶",
            font=("Arial", 10),
            bg="#3d3d3d",
            fg="#00ff00",
            bd=0,
            width=2,
            height=1,
            relief="flat",
            command=self.resume_work,
            cursor="hand2"
        )
        # play_btn se muestra solo cuando está pausado
        
        self.active_seconds = 0
        self.pomodoros = 0
        self.break_seconds = 0
        self.on_break = False
        self.paused = False
        self.tasks = []
        self.selected_task = None
        self.tasks_expanded = False
        self.drag_mode = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.load_stats()
        self.load_tasks()
        
        self.root.after(1000, self.tick)
        self.root.mainloop()
    
    def load_config(self):
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return DEFAULT_CONFIG.copy()
    
    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=2)
    
    def enable_drag_mode(self):
        self.drag_mode = True
        self.root.config(cursor="fleur")
        
        def start_drag(event):
            self.drag_start_x = event.x
            self.drag_start_y = event.y
        
        def do_drag(event):
            x = self.root.winfo_x() + (event.x - self.drag_start_x)
            y = self.root.winfo_y() + (event.y - self.drag_start_y)
            self.root.geometry(f"+{x}+{y}")
        
        def stop_drag(event):
            self.drag_mode = False
            self.root.config(cursor="")
            # Guardar posición
            self.config["window_x"] = self.root.winfo_x()
            self.config["window_y"] = self.root.winfo_y()
            self.save_config()
            self.root.unbind("<Button-1>")
            self.root.unbind("<B1-Motion>")
            self.root.unbind("<ButtonRelease-1>")
        
        self.root.bind("<Button-1>", start_drag)
        self.root.bind("<B1-Motion>", do_drag)
        self.root.bind("<ButtonRelease-1>", stop_drag)
    
    def resume_work(self):
        self.paused = False
        self.on_break = False
        self.break_btn.config(fg="#ffaa00")
        self.play_btn.pack_forget()
    
    def toggle_break(self):
        if self.break_seconds <= 0:
            return
        self.on_break = not self.on_break
        if self.on_break:
            self.break_btn.config(fg="#00ff00")
            self.paused = False
        else:
            self.break_btn.config(fg="#ffaa00")
    
    def get_idle_time(self):
        try:
            result = subprocess.run(
                ["ioreg", "-c", "IOHIDSystem"],
                capture_output=True,
                text=True,
                timeout=1
            )
            for line in result.stdout.split("\n"):
                if "HIDIdleTime" in line:
                    idle_ns = int(line.split("=")[1].strip())
                    return idle_ns / 1_000_000_000
        except:
            pass
        return 0
    
    def open_stats(self):
        stats_win = tk.Toplevel(self.root)
        stats_win.title("📊 Estadísticas")
        stats_win.geometry("700x500")
        stats_win.attributes("-topmost", True)
        
        data = self.load_all_data()
        
        if not data["stats"]:
            tk.Label(stats_win, text="No hay datos disponibles", font=("Arial", 14)).pack(pady=50)
            return
        
        dates = []
        hours = []
        pomodoros = []
        
        for row in data["stats"]:
            if row:
                dates.append(row[0][-5:])
                hours.append(int(row[1]) / 3600)
                pomodoros.append(int(row[2]))
        
        canvas = tk.Canvas(stats_win, bg="#2d2d2d", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Gráfica de productividad general
        max_hours = max(hours) if hours else 1
        max_pomodoros = max(pomodoros) if pomodoros else 1
        spacing = 60
        start_x = 50
        start_y = 200
        
        canvas.create_text(350, 20, text="Productividad General", font=("Arial", 12, "bold"), fill="white")
        
        for i, (date, hour, pomo) in enumerate(zip(dates, hours, pomodoros)):
            x = start_x + i * spacing
            
            h_height = (hour / max_hours) * 100
            canvas.create_rectangle(x, start_y - h_height, x + 15, start_y, fill="#4a90e2")
            
            p_height = (pomo / max_pomodoros) * 100
            canvas.create_rectangle(x + 20, start_y - p_height, x + 35, start_y, fill="#00ff00")
            
            canvas.create_text(x + 17, start_y + 15, text=date, font=("Arial", 8), fill="white")
            canvas.create_text(x + 7, start_y - h_height - 10, text=f"{hour:.1f}h", font=("Arial", 8), fill="white")
            canvas.create_text(x + 27, start_y - p_height - 10, text=f"{pomo}p", font=("Arial", 8), fill="white")
        
        canvas.create_rectangle(20, 40, 35, 55, fill="#4a90e2")
        canvas.create_text(70, 47, text="Horas trabajadas", font=("Arial", 10), anchor="w", fill="white")
        canvas.create_rectangle(20, 65, 35, 80, fill="#00ff00")
        canvas.create_text(70, 72, text="Pomodoros", font=("Arial", 10), anchor="w", fill="white")
        
        # Gráfica de tareas (últimos 7 días)
        if data["task_history"]:
            canvas.create_text(350, 250, text="Tiempo por Tarea (Últimos 7 días)", font=("Arial", 12, "bold"), fill="white")
            
            # Obtener últimos 7 días
            recent_history = data["task_history"][-7:]
            task_names = set()
            for date, tasks in recent_history:
                for task in tasks:
                    if task:
                        task_names.add(task[0])
            
            task_names = list(task_names)[:5]  # Máximo 5 tareas
            colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#f9ca24", "#6c5ce7"]
            
            start_y_tasks = 450
            bar_height = 20
            
            for i, task_name in enumerate(task_names):
                y = 280 + i * 30
                canvas.create_rectangle(50, y, 65, y + 15, fill=colors[i % len(colors)])
                canvas.create_text(75, y + 7, text=task_name[:15], font=("Arial", 9), anchor="w", fill="white")
                
                # Barras por día
                for j, (date, tasks) in enumerate(recent_history):
                    task_seconds = 0
                    for task in tasks:
                        if task and task[0] == task_name:
                            task_seconds = int(task[1]) if len(task) > 1 else 0
                            break
                    
                    if task_seconds > 0:
                        task_hours = task_seconds / 3600
                        bar_width = min(task_hours * 50, 100)
                        x_pos = 200 + j * 70
                        canvas.create_rectangle(x_pos, y, x_pos + bar_width, y + 15, fill=colors[i % len(colors)])
                        canvas.create_text(x_pos + bar_width + 5, y + 7, text=f"{task_hours:.1f}h", font=("Arial", 7), anchor="w", fill="white")
    
    def open_settings(self):
        settings = tk.Toplevel(self.root)
        settings.title("⚙ Configuración")
        settings.geometry("300x300")
        settings.attributes("-topmost", True)
        
        tk.Label(settings, text="Duración Pomodoro (min):", anchor="w").pack(fill="x", padx=10, pady=(10,0))
        pomodoro_var = tk.DoubleVar(value=self.config["pomodoro_minutes"])
        tk.Spinbox(settings, from_=0.1, to=60, increment=0.1, textvariable=pomodoro_var, width=10, format="%.1f").pack(padx=10)
        
        tk.Label(settings, text="Duración Descanso (min):", anchor="w").pack(fill="x", padx=10, pady=(10,0))
        break_var = tk.DoubleVar(value=self.config["break_minutes"])
        tk.Spinbox(settings, from_=0.1, to=30, increment=0.1, textvariable=break_var, width=10, format="%.1f").pack(padx=10)
        
        tk.Label(settings, text="Meta Diaria (pomodoros):", anchor="w").pack(fill="x", padx=10, pady=(10,0))
        goal_var = tk.IntVar(value=self.config["daily_goal"])
        tk.Spinbox(settings, from_=1, to=20, textvariable=goal_var, width=10).pack(padx=10)
        
        tk.Label(settings, text="Tiempo Inactividad (seg):", anchor="w").pack(fill="x", padx=10, pady=(10,0))
        idle_var = tk.IntVar(value=self.config["idle_threshold"])
        tk.Spinbox(settings, from_=10, to=300, textvariable=idle_var, width=10).pack(padx=10)
        
        tk.Label(settings, text="Transparencia:", anchor="w").pack(fill="x", padx=10, pady=(10,0))
        transparency_var = tk.DoubleVar(value=self.config.get("transparency", 0.9))
        transparency_scale = tk.Scale(
            settings,
            from_=0.3,
            to=1.0,
            resolution=0.05,
            orient=tk.HORIZONTAL,
            variable=transparency_var,
            command=lambda v: self.root.attributes("-alpha", float(v))
        )
        transparency_scale.pack(padx=10, fill="x")
        
        # Botón para ajustar posición
        tk.Button(settings, text="📍 Ajustar Posición", command=self.enable_drag_mode, bg="#ffaa00").pack(pady=5)
        
        def save():
            self.config["pomodoro_minutes"] = pomodoro_var.get()
            self.config["break_minutes"] = break_var.get()
            self.config["daily_goal"] = goal_var.get()
            self.config["idle_threshold"] = idle_var.get()
            self.config["transparency"] = transparency_var.get()
            self.save_config()
            settings.destroy()
        
        tk.Button(settings, text="Guardar", command=save, bg="#00ff00").pack(pady=15)

    def tick(self):
        if self.paused:
            self.root.after(1000, self.tick)
            return
            
        if self.on_break:
            if self.break_seconds > 0:
                self.break_seconds -= 1
            else:
                self.on_break = False
                self.paused = True
                self.break_btn.config(fg="#ffaa00")
                self.play_btn.pack(pady=2)
        else:
            if self.get_idle_time() < self.config["idle_threshold"]:
                self.active_seconds += 1
                
                # Registrar tiempo en tarea seleccionada
                if self.selected_task is not None and self.selected_task < len(self.tasks):
                    self.tasks[self.selected_task]["seconds"] += 1
                    self.save_tasks()
                
                pomodoro_seconds = int(self.config["pomodoro_minutes"] * 60)
                if pomodoro_seconds > 0 and self.active_seconds % pomodoro_seconds == 0 and self.active_seconds > 0:
                    self.pomodoros += 1
                    break_to_add = int(self.config["break_minutes"] * 60)
                    self.break_seconds += break_to_add
                    self.notify()
                    self.save_stats()
        
        mins, secs = divmod(self.active_seconds, 60)
        goal = self.config["daily_goal"]
        break_mins, break_secs = divmod(self.break_seconds, 60)
        
        status = "⏸" if self.paused else ("🟢" if self.on_break else "")
        self.label.config(text=f"{status}{mins:02d}:{secs:02d} | P:{self.pomodoros}/{goal}")
        self.break_label.config(text=f"Descanso: {break_mins:02d}:{break_secs:02d}")
        
        self.root.after(1000, self.tick)
    
    def notify(self):
        subprocess.run([
            "osascript", "-e",
            f'display notification "¡Pomodoro #{self.pomodoros} completado!" with title "🍅 Pomodoro"'
        ], check=False)
    
    def load_stats(self):
        if not DATA_FILE.exists():
            return
        today = datetime.now().strftime("%Y-%m-%d")
        with open(DATA_FILE, "r") as f:
            section = None
            for row in csv.reader(f):
                if not row:
                    continue
                if row[0] == "[STATS]":
                    section = "stats"
                    continue
                if row[0].startswith("["):
                    section = None
                    continue
                
                if section == "stats" and row[0] == today:
                    self.active_seconds = int(row[1])
                    self.pomodoros = int(row[2])
                    if len(row) > 3:
                        self.break_seconds = int(row[3])
                    break
    
    def save_stats(self):
        today = datetime.now().strftime("%Y-%m-%d")
        data = self.load_all_data()
        
        # Actualizar stats del día
        stats_updated = False
        for i, row in enumerate(data["stats"]):
            if row[0] == today:
                data["stats"][i] = [today, self.active_seconds, self.pomodoros, self.break_seconds]
                stats_updated = True
                break
        
        if not stats_updated:
            data["stats"].append([today, self.active_seconds, self.pomodoros, self.break_seconds])
        
        self.save_all_data(data)
    
    def load_tasks(self):
        if not DATA_FILE.exists():
            return
        today = datetime.now().strftime("%Y-%m-%d")
        with open(DATA_FILE, "r") as f:
            section = None
            for row in csv.reader(f):
                if not row:
                    continue
                if row[0] == "[TASKS]":
                    section = "tasks"
                    continue
                if row[0] == "[TASK_HISTORY]":
                    section = None
                    continue
                if row[0].startswith("["):
                    section = None
                    continue
                
                if section == "tasks":
                    self.tasks.append({"name": row[0], "seconds": int(row[1]) if len(row) > 1 else 0})
    
    def save_tasks(self):
        today = datetime.now().strftime("%Y-%m-%d")
        data = self.load_all_data()
        
        # Actualizar tareas actuales
        data["tasks"] = [[t["name"], t["seconds"]] for t in self.tasks]
        
        # Guardar historial diario de tareas
        task_history_today = {today: [[t["name"], t["seconds"]] for t in self.tasks]}
        
        # Actualizar o agregar historial del día
        history_updated = False
        for i, (date, tasks_data) in enumerate(data["task_history"]):
            if date == today:
                data["task_history"][i] = (today, [[t["name"], t["seconds"]] for t in self.tasks])
                history_updated = True
                break
        
        if not history_updated:
            data["task_history"].append((today, [[t["name"], t["seconds"]] for t in self.tasks]))
        
        self.save_all_data(data)
    
    def load_all_data(self):
        data = {"stats": [], "tasks": [], "task_history": []}
        
        if not DATA_FILE.exists():
            return data
        
        with open(DATA_FILE, "r") as f:
            section = None
            current_date = None
            current_tasks = []
            
            for row in csv.reader(f):
                if not row:
                    continue
                
                if row[0] == "[STATS]":
                    section = "stats"
                    continue
                elif row[0] == "[TASKS]":
                    section = "tasks"
                    continue
                elif row[0] == "[TASK_HISTORY]":
                    section = "task_history"
                    continue
                elif row[0].startswith("[DATE:") and section == "task_history":
                    if current_date and current_tasks:
                        data["task_history"].append((current_date, current_tasks))
                    current_date = row[0][6:-1]  # Extract date from [DATE:YYYY-MM-DD]
                    current_tasks = []
                    continue
                
                if section == "stats":
                    data["stats"].append(row)
                elif section == "tasks":
                    data["tasks"].append(row)
                elif section == "task_history" and current_date:
                    current_tasks.append(row)
            
            # Add last task history entry
            if current_date and current_tasks:
                data["task_history"].append((current_date, current_tasks))
        
        return data
    
    def save_all_data(self, data):
        with open(DATA_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            
            # Write stats section
            writer.writerow(["[STATS]"])
            for row in data["stats"]:
                writer.writerow(row)
            writer.writerow([])
            
            # Write tasks section
            writer.writerow(["[TASKS]"])
            for row in data["tasks"]:
                writer.writerow(row)
            writer.writerow([])
            
            # Write task history section
            writer.writerow(["[TASK_HISTORY]"])
            for date, tasks in data["task_history"]:
                writer.writerow([f"[DATE:{date}]"])
                for task_row in tasks:
                    writer.writerow(task_row)
    
    def create_tasks_toggle(self):
        # Botón para expandir/colapsar tareas (se agrega al frame principal)
        pass  # Ya implementado en __init__
    
    def toggle_tasks_panel(self):
        if self.tasks_expanded:
            # Colapsar panel
            if self.tasks_panel:
                self.tasks_panel.destroy()
                self.tasks_panel = None
            self.tasks_toggle_btn.config(text="▼ Tareas")
            self.tasks_expanded = False
        else:
            # Expandir panel
            self.create_tasks_panel()
            self.tasks_toggle_btn.config(text="▲ Tareas")
            self.tasks_expanded = True
    
    def create_tasks_panel(self):
        # Crear ventana desplegable debajo del contador
        screen_width = self.root.winfo_screenwidth()
        x_pos = screen_width - 200
        y_pos = self.root.winfo_y() + self.root.winfo_height() + 5
        
        self.tasks_panel = tk.Toplevel(self.root)
        self.tasks_panel.overrideredirect(True)
        self.tasks_panel.attributes("-topmost", True)
        self.tasks_panel.attributes("-alpha", self.config.get("transparency", 0.9))
        self.tasks_panel.wm_geometry(f"+{x_pos}+{y_pos}")
        self.tasks_panel.config(bg="#2d2d2d")
        
        frame = tk.Frame(self.tasks_panel, bg="#2d2d2d")
        frame.pack(padx=10, pady=10)
        
        # Botones superiores
        top_btns = tk.Frame(frame, bg="#2d2d2d")
        top_btns.pack(pady=5)
        
        add_btn = tk.Button(
            top_btns,
            text="+ Nueva",
            font=("Menlo", 10),
            bg="#3d3d3d",
            fg="#00ff00",
            bd=0,
            command=self.add_task,
            cursor="hand2"
        )
        add_btn.pack(side=tk.LEFT, padx=2)
        
        reset_btn = tk.Button(
            top_btns,
            text="↻ Reset",
            font=("Menlo", 10),
            bg="#3d3d3d",
            fg="#ffaa00",
            bd=0,
            command=self.reset_tasks,
            cursor="hand2"
        )
        reset_btn.pack(side=tk.LEFT, padx=2)
        
        # Lista de tareas
        self.tasks_list_frame = tk.Frame(frame, bg="#2d2d2d")
        self.tasks_list_frame.pack()
        
        self.refresh_tasks_list()
    
    def refresh_tasks_list(self):
        # Limpiar lista
        for widget in self.tasks_list_frame.winfo_children():
            widget.destroy()
        
        # Mostrar tareas
        for i, task in enumerate(self.tasks):
            task_frame = tk.Frame(self.tasks_list_frame, bg="#2d2d2d")
            task_frame.pack(fill=tk.X, pady=2)
            
            # Radio button para seleccionar
            is_selected = self.selected_task == i
            btn = tk.Button(
                task_frame,
                text=f"{'●' if is_selected else '○'} {task['name'][:20]}{'...' if len(task['name']) > 20 else ''}",
                font=("Menlo", 8),
                bg="#3d3d3d" if is_selected else "#2d2d2d",
                fg="#00ff00" if is_selected else "#888888",
                bd=0,
                anchor="w",
                width=18,
                command=lambda idx=i: self.select_task(idx),
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT)
            
            # Tiempo dedicado
            mins = task["seconds"] // 60
            tk.Label(
                task_frame,
                text=f"{mins}m",
                font=("Menlo", 7),
                bg="#2d2d2d",
                fg="#888888"
            ).pack(side=tk.RIGHT, padx=2)
            
            # Botón eliminar (más pequeño)
            del_btn = tk.Button(
                task_frame,
                text="−",
                font=("Arial", 8),
                bg="#2d2d2d",
                fg="#ff5555",
                bd=0,
                width=1,
                command=lambda idx=i: self.delete_task(idx),
                cursor="hand2"
            )
            del_btn.pack(side=tk.RIGHT)
    
    def add_task(self):
        # Ventana simple para agregar tarea
        dialog = tk.Toplevel(self.root)
        dialog.title("Nueva Tarea")
        dialog.geometry("250x100")
        dialog.attributes("-topmost", True)
        
        tk.Label(dialog, text="Nombre de la tarea:").pack(pady=10)
        entry = tk.Entry(dialog, width=30)
        entry.pack(pady=5)
        entry.focus()
        
        def save():
            name = entry.get().strip()
            if name:
                self.tasks.append({"name": name, "seconds": 0})
                self.save_tasks()
                if self.tasks_panel:
                    self.refresh_tasks_list()
                dialog.destroy()
        
        tk.Button(dialog, text="Agregar", command=save, bg="#00ff00").pack(pady=10)
        entry.bind("<Return>", lambda e: save())
    
    def select_task(self, index):
        self.selected_task = index
        if self.tasks_panel:
            self.refresh_tasks_list()
    
    def delete_task(self, index):
        if index < len(self.tasks):
            self.tasks.pop(index)
            if self.selected_task == index:
                self.selected_task = None
            elif self.selected_task is not None and self.selected_task > index:
                self.selected_task -= 1
            self.save_tasks()
            if self.tasks_panel:
                self.refresh_tasks_list()
    
    def reset_tasks(self):
        # Eliminar todas las tareas
        self.tasks = []
        self.selected_task = None
        self.save_tasks()
        if self.tasks_panel:
            self.refresh_tasks_list()

if __name__ == "__main__":
    Pomodoro()
