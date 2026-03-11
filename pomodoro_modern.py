#!/usr/bin/env python3
import customtkinter as ctk
import subprocess
import csv
import json
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')

# Configuración de customtkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Usar directorio home del usuario para archivos
DATA_DIR = Path.home() / ".pomodoro"
DATA_DIR.mkdir(exist_ok=True)
CONFIG_FILE = DATA_DIR / "pomodoro_config.json"
DATA_FILE = DATA_DIR / "pomodoro_data.csv"

DEFAULT_CONFIG = {
    "pomodoro_minutes": 25,
    "break_minutes": 5,
    "daily_goal": 8,
    "idle_threshold": 60,
    "transparency": 0.95,
    "transparent_bg": False
}

class PomodoroModern(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.config = self.load_config()
        
        # Configuración de ventana
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", self.config.get("transparency", 0.95))
        
        # Configurar transparencia del fondo
        if self.config.get("transparent_bg", False):
            self.bg_color = "systemTransparent"
        else:
            self.bg_color = "systemTransparent"
        
        # Posicionar
        if "window_x" in self.config and "window_y" in self.config:
            x_pos = self.config["window_x"]
            y_pos = self.config["window_y"]
        else:
            screen_width = self.winfo_screenwidth()
            x_pos = screen_width - 250
            y_pos = 40
        
        self.geometry(f"+{x_pos}+{y_pos}")
        
        # Hacer que aparezca en todos los escritorios/Spaces de macOS
        try:
            subprocess.run([
                "osascript", "-e",
                'tell application "System Events" to set visible of every window of (every process whose name is "Python") to true'
            ], check=False)
        except:
            pass
        
        # Variables de estado
        self.active_seconds = 0  # Tiempo total del día
        self.session_seconds = 0  # Tiempo de la sesión actual de pomodoro
        self.pomodoros_today = 0
        self.break_seconds = 0
        self.is_break = False
        self.paused = False
        self.last_activity_time = datetime.now()
        
        # Variables de tareas
        self.tasks = []
        self.selected_task = None
        self.tasks_expanded = False
        
        # Variables de arrastre
        self.drag_mode = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Crear UI
        self.create_ui()
        
        # Cargar datos
        self.load_stats()
        self.load_tasks()
        
        # Iniciar timer
        self.after(1000, self.tick)
        
        # Dibujar fondo redondeado después de crear UI
        self.after(100, self.draw_rounded_bg)
    
    def create_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius=15, **kwargs):
        """Crear rectángulo con bordes redondeados"""
        points = [
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        ]
        return canvas.create_polygon(points, smooth=True, **kwargs)
    
    def draw_rounded_bg(self):
        """Dibujar rectángulo redondeado como fondo"""
        self.main_frame.update_idletasks()
        width = self.main_frame.winfo_width() + 20
        height = self.main_frame.winfo_height() + 20
        
        # Redimensionar canvas
        self.canvas.config(width=width, height=height)
        self.geometry(f"{width}x{height}")
        
        # Eliminar rectángulo anterior si existe
        if hasattr(self, 'rounded_rect_id'):
            self.canvas.delete(self.rounded_rect_id)
        
        # Dibujar rectángulo redondeado
        self.rounded_rect_id = self.create_rounded_rectangle(
            self.canvas, 0, 0, width, height, radius=15, fill=self.bg_color, outline=""
        )
        
        # Centrar el frame dentro del canvas
        self.canvas.coords(self.canvas_window, 10, 10)
    
    def create_ui(self):
        """Crear interfaz moderna con customtkinter"""
        import tkinter as tk
        
        # Habilitar transparencia en la ventana
        self.wm_attributes("-transparent", True)
        
        # Canvas para dibujar el fondo con bordes redondeados
        self.canvas = tk.Canvas(
            self,
            bg="systemTransparent",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Frame principal de customtkinter sobre el canvas
        # Usar el color guardado o el predeterminado
        if self.config.get("transparent_bg", False):
            frame_color = "transparent"
        else:
            frame_color = self.config.get("bg_color", "#1c1c1e")
        
        self.main_frame = ctk.CTkFrame(
            self.canvas,
            fg_color=frame_color,
            corner_radius=15
        )
        self.canvas_window = self.canvas.create_window(0, 0, window=self.main_frame, anchor="nw")
        
        # Columna izquierda: tiempos
        left_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        left_frame.pack(side="left", padx=10, pady=10)
        
        # Label principal con ancho fijo
        self.label = ctk.CTkLabel(
            left_frame,
            text="00:00 | P:0/8",
            font=("SF Pro Display", 14, "bold"),
            text_color="#00ff00",
            width=120  # Ancho fijo
        )
        self.label.pack(pady=(0, 5))
        
        # Label de descanso con ancho fijo
        self.break_label = ctk.CTkLabel(
            left_frame,
            text="Descanso: 00:00",
            font=("SF Pro Display", 11),
            text_color="#ffaa00",
            width=120  # Ancho fijo
        )
        self.break_label.pack(pady=(0, 8))
        
        # Botón para expandir tareas (estilo sutil)
        self.tasks_toggle_btn = ctk.CTkButton(
            left_frame,
            text="▼ Tareas",
            font=("SF Pro Display", 10),
            fg_color="transparent",
            text_color="#8e8e93",  # Gris más sutil
            hover_color="#2c2c2e",
            corner_radius=8,
            width=80,
            height=24,
            command=self.toggle_tasks_panel
        )
        self.tasks_toggle_btn.pack()
        
        # Columna derecha: botones
        btn_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_container.pack(side="right", padx=10, pady=10)
        
        # Botón de estadísticas (estilo Dynamic Island)
        stats_btn = ctk.CTkButton(
            btn_container,
            text="📈",
            font=("SF Pro Display", 14),
            width=32,
            height=32,
            corner_radius=16,  # Más redondeado
            fg_color="#2c2c2e",  # Gris oscuro sutil
            hover_color="#3a3a3c",  # Hover más claro
            border_width=0,
            command=self.open_stats
        )
        stats_btn.pack(pady=(0, 6))
        
        # Botón de configuración (estilo Dynamic Island)
        settings_btn = ctk.CTkButton(
            btn_container,
            text="⚙️",
            font=("SF Pro Display", 14),
            width=32,
            height=32,
            corner_radius=16,
            fg_color="#2c2c2e",
            hover_color="#3a3a3c",
            border_width=0,
            command=self.open_settings
        )
        settings_btn.pack(pady=(0, 6))
        
        # Botón de descanso (estilo Dynamic Island)
        self.break_btn = ctk.CTkButton(
            btn_container,
            text="☕️",
            font=("SF Pro Display", 14),
            width=32,
            height=32,
            corner_radius=16,
            fg_color="#2c2c2e",
            hover_color="#3a3a3c",
            border_width=0,
            command=self.toggle_break
        )
        self.break_btn.pack()
    
    def load_config(self):
        """Cargar configuración"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                return {**DEFAULT_CONFIG, **config}
        return DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """Guardar configuración"""
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=2)
    
    def load_stats(self):
        """Cargar estadísticas del día"""
        if not DATA_FILE.exists():
            return
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        with open(DATA_FILE, "r") as f:
            content = f.read()
            if "[STATS]" in content:
                stats_section = content.split("[STATS]")[1].split("[")[0].strip()
                for line in stats_section.split("\n"):
                    if line.startswith(today):
                        parts = line.split(",")
                        self.active_seconds = int(parts[1])
                        self.pomodoros_today = int(parts[2])
                        self.break_seconds = int(parts[3])
                        break
    
    def load_tasks(self):
        """Cargar tareas actuales"""
        if not DATA_FILE.exists():
            return
        
        with open(DATA_FILE, "r") as f:
            content = f.read()
            if "[TASKS]" in content:
                tasks_section = content.split("[TASKS]")[1].split("[")[0].strip()
                for line in tasks_section.split("\n"):
                    if line and "," in line:
                        name, seconds = line.rsplit(",", 1)
                        self.tasks.append({"name": name, "seconds": int(seconds)})
    
    def save_all_data(self):
        """Guardar todos los datos en archivo unificado"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Leer datos existentes
        existing_data = {"stats": {}, "tasks": self.tasks, "history": {}}
        
        if DATA_FILE.exists():
            with open(DATA_FILE, "r") as f:
                content = f.read()
                
                # Parsear STATS
                if "[STATS]" in content:
                    stats_section = content.split("[STATS]")[1].split("[")[0].strip()
                    for line in stats_section.split("\n"):
                        if line and "," in line:
                            parts = line.split(",")
                            existing_data["stats"][parts[0]] = parts[1:]
                
                # Parsear TASK_HISTORY
                if "[TASK_HISTORY]" in content:
                    history_section = content.split("[TASK_HISTORY]")[1].strip()
                    current_date = None
                    for line in history_section.split("\n"):
                        if line.startswith("[DATE:"):
                            current_date = line.split(":")[1].rstrip("]")
                            existing_data["history"][current_date] = []
                        elif line and current_date and "," in line:
                            existing_data["history"][current_date].append(line)
        
        # Actualizar stats de hoy
        existing_data["stats"][today] = [
            str(self.active_seconds),
            str(self.pomodoros_today),
            str(self.break_seconds)
        ]
        
        # Escribir archivo
        with open(DATA_FILE, "w") as f:
            # Sección STATS
            f.write("[STATS]\n")
            for date, values in sorted(existing_data["stats"].items()):
                f.write(f"{date},{','.join(values)}\n")
            
            # Sección TASKS
            f.write("\n[TASKS]\n")
            for task in self.tasks:
                f.write(f"{task['name']},{task['seconds']}\n")
            
            # Sección TASK_HISTORY
            f.write("\n[TASK_HISTORY]\n")
            for date, tasks in sorted(existing_data["history"].items()):
                f.write(f"[DATE:{date}]\n")
                for task_line in tasks:
                    f.write(f"{task_line}\n")
    
    def tick(self):
        """Actualizar cada segundo"""
        # Detectar inactividad
        idle_time = self.get_idle_time()
        
        if idle_time > self.config["idle_threshold"]:
            self.paused = True
        else:
            self.paused = False
            self.last_activity_time = datetime.now()
        
        # Actualizar tiempo
        if not self.paused:
            if self.is_break:
                if self.break_seconds > 0:
                    self.break_seconds -= 1
                else:
                    self.is_break = False
                    self.break_btn.configure(text="☕️")
            else:
                self.active_seconds += 1
                self.session_seconds += 1
                
                # Tracking de tarea seleccionada
                if self.selected_task:
                    for task in self.tasks:
                        if task["name"] == self.selected_task:
                            task["seconds"] += 1
                            break
                
                # Verificar si completó un pomodoro
                pomodoro_seconds = int(self.config["pomodoro_minutes"] * 60)
                if self.session_seconds >= pomodoro_seconds:
                    self.pomodoros_today += 1
                    self.break_seconds += int(self.config["break_minutes"] * 60)
                    self.session_seconds = 0  # Reiniciar sesión
                    self.show_notification("¡Pomodoro completado!", f"Has completado {self.pomodoros_today} pomodoros hoy")
        
        # Actualizar UI
        self.update_display()
        
        # Guardar datos cada minuto
        if self.active_seconds > 0 and self.active_seconds % 60 == 0:
            self.save_all_data()
        
        # Siguiente tick
        self.after(1000, self.tick)
    
    def update_display(self):
        """Actualizar display"""
        # Tiempo de la sesión actual (no el total del día)
        hours = self.session_seconds // 3600
        minutes = (self.session_seconds % 3600) // 60
        seconds = self.session_seconds % 60
        
        if hours > 0:
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            time_str = f"{minutes:02d}:{seconds:02d}"
        
        # Label principal
        goal = self.config["daily_goal"]
        self.label.configure(text=f"{time_str} | P:{self.pomodoros_today}/{goal}")
        
        # Label de descanso
        break_mins = self.break_seconds // 60
        break_secs = self.break_seconds % 60
        self.break_label.configure(text=f"Descanso: {break_mins:02d}:{break_secs:02d}")
        
        # Color según estado
        if self.paused:
            self.label.configure(text_color="#ff0000")
        elif self.is_break:
            self.label.configure(text_color="#ffaa00")
        else:
            self.label.configure(text_color="#00ff00")
    
    def get_idle_time(self):
        """Obtener tiempo de inactividad en segundos"""
        try:
            result = subprocess.run(
                ["ioreg", "-c", "IOHIDSystem"],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.split("\n"):
                if "HIDIdleTime" in line:
                    idle_ns = int(line.split("=")[1].strip())
                    return idle_ns // 1_000_000_000
        except:
            pass
        return 0
    
    def show_notification(self, title, message):
        """Mostrar notificación de macOS"""
        try:
            subprocess.run([
                "osascript", "-e",
                f'display notification "{message}" with title "{title}"'
            ], check=False)
        except:
            pass
    
    def toggle_break(self):
        """Alternar modo descanso"""
        if self.break_seconds > 0:
            self.is_break = not self.is_break
            self.break_btn.configure(text="▶" if self.is_break else "☕")
    
    def toggle_tasks_panel(self):
        """Alternar panel de tareas con animación"""
        if self.tasks_expanded:
            # Animar cierre
            self.animate_tasks_panel_close()
        else:
            # Crear y animar apertura
            self.create_tasks_panel()
            self.animate_tasks_panel_open()
            self.tasks_expanded = True
            self.tasks_toggle_btn.configure(text="▲ Tareas")
    
    def animate_tasks_panel_open(self):
        """Animar apertura del panel de tareas"""
        if not hasattr(self, 'tasks_panel') or not self.tasks_panel.winfo_exists():
            return
        
        target_height = self.tasks_panel_target_height
        steps = 10
        step_height = target_height / steps
        
        def animate_step(current_step):
            if current_step <= steps and self.tasks_panel.winfo_exists():
                current_height = int(step_height * current_step)
                self.tasks_panel.geometry(f"250x{current_height}")
                if current_step < steps:
                    self.after(20, lambda: animate_step(current_step + 1))
        
        # Iniciar con altura 0
        self.tasks_panel.geometry(f"250x0")
        animate_step(1)
    
    def animate_tasks_panel_close(self):
        """Animar cierre del panel de tareas"""
        if not hasattr(self, 'tasks_panel') or not self.tasks_panel.winfo_exists():
            self.tasks_expanded = False
            self.tasks_toggle_btn.configure(text="▼ Tareas")
            return
        
        current_height = self.tasks_panel.winfo_height()
        steps = 10
        step_height = current_height / steps
        
        def animate_step(current_step):
            if current_step <= steps and self.tasks_panel.winfo_exists():
                new_height = int(current_height - (step_height * current_step))
                if new_height > 0:
                    self.tasks_panel.geometry(f"250x{new_height}")
                    self.after(20, lambda: animate_step(current_step + 1))
                else:
                    self.tasks_panel.destroy()
                    self.tasks_expanded = False
                    self.tasks_toggle_btn.configure(text="▼ Tareas")
        
        animate_step(1)
    
    def create_tasks_panel(self):
        """Crear panel de tareas moderno"""
        self.update_idletasks()
        x_pos = self.winfo_x()
        y_pos = self.winfo_y() + self.winfo_height() + 5
        
        self.tasks_panel = ctk.CTkToplevel(self)
        self.tasks_panel.overrideredirect(True)
        self.tasks_panel.attributes("-topmost", True)
        self.tasks_panel.attributes("-alpha", self.config.get("transparency", 0.95))
        self.tasks_panel.geometry(f"+{x_pos}+{y_pos}")
        
        # Frame principal
        main_frame = ctk.CTkFrame(
            self.tasks_panel,
            fg_color="#1a1a1a",
            corner_radius=15
        )
        main_frame.pack(fill="both", expand=True, padx=6, pady=6)
        
        # Botones de acción
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkButton(
            btn_frame,
            text="➕ Nueva",
            font=("SF Pro Display", 11),
            width=70,
            height=28,
            corner_radius=8,
            fg_color="#007AFF",
            hover_color="#0051D5",
            command=self.add_task
        ).pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(
            btn_frame,
            text="🔄 Reset",
            font=("SF Pro Display", 11),
            width=70,
            height=28,
            corner_radius=8,
            fg_color="#FF3B30",
            hover_color="#D32F2F",
            command=self.reset_tasks
        ).pack(side="left")
        
        # Lista de tareas
        self.tasks_list_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="transparent",
            width=200,
            height=150
        )
        self.tasks_list_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        self.refresh_tasks_list()
        
        # Calcular altura objetivo después de crear el contenido
        self.tasks_panel.update_idletasks()
        self.tasks_panel_target_height = main_frame.winfo_reqheight() + 12  # +12 por padding
    
    def refresh_tasks_list(self):
        """Refrescar lista de tareas"""
        for widget in self.tasks_list_frame.winfo_children():
            widget.destroy()
        
        # Variable compartida para radio buttons
        radio_var = ctk.StringVar(value=self.selected_task or "")
        
        for task in self.tasks:
            task_frame = ctk.CTkFrame(self.tasks_list_frame, fg_color="#2d2d2d", corner_radius=8)
            task_frame.pack(fill="x", pady=3)
            
            # Radio button
            radio = ctk.CTkRadioButton(
                task_frame,
                text="",
                value=task["name"],
                variable=radio_var,
                command=lambda t=task["name"], v=radio_var: self.select_task(t, v),
                width=20
            )
            radio.pack(side="left", padx=5)
            
            # Nombre de tarea
            name = task["name"][:18] + "..." if len(task["name"]) > 18 else task["name"]
            hours = task["seconds"] // 3600
            mins = (task["seconds"] % 3600) // 60
            time_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"
            
            ctk.CTkLabel(
                task_frame,
                text=f"{name} ({time_str})",
                font=("SF Pro Display", 11),
                anchor="w"
            ).pack(side="left", fill="x", expand=True, padx=5)
            
            # Botón eliminar
            ctk.CTkButton(
                task_frame,
                text="✕",
                font=("SF Pro Display", 12),
                width=24,
                height=24,
                corner_radius=6,
                fg_color="transparent",
                hover_color="#FF3B30",
                command=lambda t=task: self.delete_task(t)
            ).pack(side="right", padx=5)
    
    def select_task(self, task_name, radio_var):
        """Seleccionar o deseleccionar tarea"""
        if self.selected_task == task_name:
            # Deseleccionar
            self.selected_task = None
            radio_var.set("")
        else:
            # Seleccionar
            self.selected_task = task_name
    
    def add_task(self):
        """Agregar nueva tarea"""
        # Crear ventana de diálogo personalizada
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nueva Tarea")
        dialog.geometry("300x150")
        dialog.attributes("-topmost", True)
        
        # Frame principal
        frame = ctk.CTkFrame(dialog, fg_color="#1a1a1a", corner_radius=15)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(
            frame,
            text="Nombre de la tarea:",
            font=("SF Pro Display", 13)
        ).pack(pady=(10, 5))
        
        entry = ctk.CTkEntry(
            frame,
            font=("SF Pro Display", 12),
            corner_radius=10,
            height=35
        )
        entry.pack(fill="x", padx=15, pady=(0, 10))
        entry.focus()
        
        def save_task():
            task_name = entry.get()
            if task_name:
                self.tasks.append({"name": task_name, "seconds": 0})
                self.save_all_data()
                self.refresh_tasks_list()
                dialog.destroy()
        
        ctk.CTkButton(
            frame,
            text="Agregar",
            font=("SF Pro Display", 12, "bold"),
            corner_radius=10,
            height=35,
            fg_color="#007AFF",
            hover_color="#0051D5",
            command=save_task
        ).pack(fill="x", padx=15, pady=(0, 10))
        
        entry.bind("<Return>", lambda e: save_task())
    
    def delete_task(self, task):
        """Eliminar tarea"""
        self.tasks.remove(task)
        if self.selected_task == task["name"]:
            self.selected_task = None
        self.save_all_data()
        self.refresh_tasks_list()
    
    def reset_tasks(self):
        """Resetear todas las tareas"""
        self.tasks = []
        self.selected_task = None
        self.save_all_data()
        self.refresh_tasks_list()
    
    def open_stats(self):
        """Abrir ventana de estadísticas con gráficas"""
        stats_window = ctk.CTkToplevel(self)
        stats_window.title("📈 Estadísticas")
        stats_window.geometry("900x700")
        stats_window.attributes("-topmost", True)
        
        # Frame principal
        main_frame = ctk.CTkFrame(stats_window, fg_color="#1a1a1a", corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Título
        ctk.CTkLabel(
            main_frame,
            text="📊 Estadísticas de Productividad",
            font=("SF Pro Display", 18, "bold")
        ).pack(pady=(15, 10))
        
        # Cargar datos
        stats_data = self.load_historical_stats()
        task_history = self.load_task_history()
        
        # Frame para gráficas
        graphs_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        graphs_frame.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        
        # Gráfica 1: Productividad General
        self.create_productivity_graph(graphs_frame, stats_data)
        
        # Gráfica 2: Tiempo por Tarea
        self.create_tasks_graph(graphs_frame, task_history)
    
    def create_productivity_graph(self, parent, stats_data):
        """Crear gráfica de productividad general"""
        frame = ctk.CTkFrame(parent, fg_color="#2d2d2d", corner_radius=12)
        frame.pack(fill="both", expand=True, pady=(0, 10))
        
        ctk.CTkLabel(
            frame,
            text="⏱️ Tiempo y Pomodoros por Día",
            font=("SF Pro Display", 14, "bold")
        ).pack(pady=(10, 5))
        
        # Preparar datos (últimos 7 días)
        dates = list(stats_data.keys())[-7:]
        hours = [int(stats_data[d]["active_seconds"]) / 3600 for d in dates]
        pomodoros = [int(stats_data[d]["pomodoros"]) for d in dates]
        
        # Crear figura
        fig, ax1 = plt.subplots(figsize=(8, 3), facecolor='#2d2d2d')
        ax1.set_facecolor('#2d2d2d')
        
        # Eje izquierdo: Horas
        color = '#00ff00'
        ax1.set_xlabel('Fecha', color='white', fontsize=10)
        ax1.set_ylabel('Horas', color=color, fontsize=10)
        ax1.plot(dates, hours, color=color, marker='o', linewidth=2, label='Horas')
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.tick_params(axis='x', colors='white', rotation=45)
        ax1.grid(True, alpha=0.2, color='white')
        
        # Eje derecho: Pomodoros
        ax2 = ax1.twinx()
        color = '#007AFF'
        ax2.set_ylabel('Pomodoros', color=color, fontsize=10)
        ax2.bar(dates, pomodoros, alpha=0.3, color=color, label='Pomodoros')
        ax2.tick_params(axis='y', labelcolor=color)
        
        plt.tight_layout()
        
        # Integrar en tkinter
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(5, 10))
    
    def create_tasks_graph(self, parent, task_history):
        """Crear gráfica de tiempo por tarea"""
        frame = ctk.CTkFrame(parent, fg_color="#2d2d2d", corner_radius=12)
        frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            frame,
            text="📋 Tiempo por Tarea (últimos 7 días)",
            font=("SF Pro Display", 14, "bold")
        ).pack(pady=(10, 5))
        
        # Preparar datos
        dates = list(task_history.keys())[-7:]
        tasks_names = set()
        for date in dates:
            tasks_names.update(task_history[date].keys())
        
        tasks_names = list(tasks_names)[:5]  # Máximo 5 tareas
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(8, 3), facecolor='#2d2d2d')
        ax.set_facecolor('#2d2d2d')
        
        # Colores para cada tarea
        colors = ['#007AFF', '#00ff00', '#ffaa00', '#FF3B30', '#AF52DE']
        
        # Datos por tarea
        for i, task_name in enumerate(tasks_names):
            hours = []
            for date in dates:
                seconds = task_history.get(date, {}).get(task_name, 0)
                hours.append(seconds / 3600)
            
            ax.plot(dates, hours, marker='o', linewidth=2, 
                   label=task_name[:15], color=colors[i % len(colors)])
        
        ax.set_xlabel('Fecha', color='white', fontsize=10)
        ax.set_ylabel('Horas', color='white', fontsize=10)
        ax.tick_params(axis='both', colors='white')
        ax.tick_params(axis='x', rotation=45)
        ax.legend(facecolor='#2d2d2d', edgecolor='white', 
                 labelcolor='white', fontsize=9)
        ax.grid(True, alpha=0.2, color='white')
        
        plt.tight_layout()
        
        # Integrar en tkinter
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(5, 10))
    
    def load_task_history(self):
        """Cargar historial de tareas"""
        history = {}
        
        if not DATA_FILE.exists():
            return history
        
        with open(DATA_FILE, "r") as f:
            content = f.read()
            if "[TASK_HISTORY]" in content:
                history_section = content.split("[TASK_HISTORY]")[1].strip()
                current_date = None
                
                for line in history_section.split("\n"):
                    if line.startswith("[DATE:"):
                        current_date = line.split(":")[1].rstrip("]")
                        history[current_date] = {}
                    elif line and current_date and "," in line:
                        name, seconds = line.rsplit(",", 1)
                        history[current_date][name] = int(seconds)
        
        return history
    
    def load_historical_stats(self):
        """Cargar estadísticas históricas"""
        stats = {}
        
        if not DATA_FILE.exists():
            return stats
        
        with open(DATA_FILE, "r") as f:
            content = f.read()
            if "[STATS]" in content:
                stats_section = content.split("[STATS]")[1].split("[")[0].strip()
                for line in stats_section.split("\n"):
                    if line and "," in line:
                        parts = line.split(",")
                        stats[parts[0]] = {
                            "active_seconds": parts[1],
                            "pomodoros": parts[2],
                            "break_seconds": parts[3]
                        }
        
        return stats
    
    def open_settings(self):
        """Abrir ventana de configuración"""
        settings = ctk.CTkToplevel(self)
        settings.title("⚙ Configuración")
        settings.geometry("400x600")  # Más grande
        settings.attributes("-topmost", True)
        
        # Frame principal
        main_frame = ctk.CTkFrame(settings, fg_color="#1a1a1a", corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Duración Pomodoro
        ctk.CTkLabel(
            main_frame,
            text="Duración Pomodoro (min):",
            font=("SF Pro Display", 13),
            anchor="w"
        ).pack(fill="x", padx=15, pady=(15, 5))
        
        pomodoro_var = ctk.StringVar(value=str(self.config["pomodoro_minutes"]))
        ctk.CTkEntry(
            main_frame,
            textvariable=pomodoro_var,
            font=("SF Pro Display", 12),
            corner_radius=10,
            height=35
        ).pack(fill="x", padx=15, pady=(0, 10))
        
        # Duración Descanso
        ctk.CTkLabel(
            main_frame,
            text="Duración Descanso (min):",
            font=("SF Pro Display", 13),
            anchor="w"
        ).pack(fill="x", padx=15, pady=(5, 5))
        
        break_var = ctk.StringVar(value=str(self.config["break_minutes"]))
        ctk.CTkEntry(
            main_frame,
            textvariable=break_var,
            font=("SF Pro Display", 12),
            corner_radius=10,
            height=35
        ).pack(fill="x", padx=15, pady=(0, 10))
        
        # Meta Diaria
        ctk.CTkLabel(
            main_frame,
            text="Meta Diaria (pomodoros):",
            font=("SF Pro Display", 13),
            anchor="w"
        ).pack(fill="x", padx=15, pady=(5, 5))
        
        goal_var = ctk.StringVar(value=str(self.config["daily_goal"]))
        ctk.CTkEntry(
            main_frame,
            textvariable=goal_var,
            font=("SF Pro Display", 12),
            corner_radius=10,
            height=35
        ).pack(fill="x", padx=15, pady=(0, 10))
        
        # Tiempo de Inactividad
        ctk.CTkLabel(
            main_frame,
            text="Tiempo Inactividad (seg):",
            font=("SF Pro Display", 13),
            anchor="w"
        ).pack(fill="x", padx=15, pady=(5, 5))
        
        idle_var = ctk.StringVar(value=str(self.config["idle_threshold"]))
        ctk.CTkEntry(
            main_frame,
            textvariable=idle_var,
            font=("SF Pro Display", 12),
            corner_radius=10,
            height=35
        ).pack(fill="x", padx=15, pady=(0, 10))
        
        # Transparencia
        ctk.CTkLabel(
            main_frame,
            text="Transparencia Ventana:",
            font=("SF Pro Display", 13),
            anchor="w"
        ).pack(fill="x", padx=15, pady=(5, 5))
        
        transparency_var = ctk.DoubleVar(value=self.config.get("transparency", 0.95))
        transparency_slider = ctk.CTkSlider(
            main_frame,
            from_=0.5,
            to=1.0,
            variable=transparency_var,
            command=lambda v: self.attributes("-alpha", v)
        )
        transparency_slider.pack(fill="x", padx=15, pady=(0, 10))
        
        # Fondo Transparente (Switch)
        ctk.CTkLabel(
            main_frame,
            text="Fondo Transparente:",
            font=("SF Pro Display", 13),
            anchor="w"
        ).pack(fill="x", padx=15, pady=(5, 5))
        
        transparent_bg_var = ctk.BooleanVar(value=self.config.get("transparent_bg", False))
        transparent_bg_switch = ctk.CTkSwitch(
            main_frame,
            text="Activar",
            variable=transparent_bg_var,
            command=lambda: self.toggle_transparent_bg(transparent_bg_var.get())
        )
        transparent_bg_switch.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Color de Fondo
        ctk.CTkLabel(
            main_frame,
            text="Color de Fondo:",
            font=("SF Pro Display", 13),
            anchor="w"
        ).pack(fill="x", padx=15, pady=(5, 5))
        
        # Frame para selector de color
        color_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        color_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Colores predefinidos
        colors = [
            ("#000000", "Deep Black"),
            ("#1c1c1e", "Negro"),
            ("#2c2c2e", "Gris Oscuro"),
            ("#1a1a2e", "Azul Oscuro"),
            ("#1e1a1a", "Rojo Oscuro"),
            ("#1a1e1a", "Verde Oscuro")
        ]
        
        current_color = self.config.get("bg_color", "#1c1c1e")
        color_var = ctk.StringVar(value=current_color)
        
        for color_hex, color_name in colors:
            is_selected = color_hex == current_color
            btn = ctk.CTkButton(
                color_frame,
                text=color_name,
                font=("SF Pro Display", 11),
                width=100,
                height=30,
                corner_radius=8,
                fg_color=color_hex,
                hover_color=color_hex,
                border_width=2 if is_selected else 0,
                border_color="#007AFF" if is_selected else color_hex,
                command=lambda c=color_hex: self.change_bg_color(c, color_var)
            )
            btn.pack(side="left", padx=2)
        
        # Botón Ajustar Posición
        ctk.CTkButton(
            main_frame,
            text="📍 Ajustar Posición",
            font=("SF Pro Display", 13),
            corner_radius=10,
            height=35,
            fg_color="#FF9500",
            hover_color="#CC7700",
            command=lambda: self.enable_drag_mode(settings)
        ).pack(fill="x", padx=15, pady=(0, 10))
        
        # Botón Guardar
        def save():
            self.config["pomodoro_minutes"] = float(pomodoro_var.get())
            self.config["break_minutes"] = float(break_var.get())
            self.config["daily_goal"] = int(goal_var.get())
            self.config["idle_threshold"] = int(idle_var.get())
            self.config["transparency"] = transparency_var.get()
            self.config["transparent_bg"] = transparent_bg_var.get()
            self.config["bg_color"] = color_var.get()
            self.save_config()
            settings.destroy()
        
        ctk.CTkButton(
            main_frame,
            text="Guardar",
            font=("SF Pro Display", 14, "bold"),
            corner_radius=12,
            height=40,
            fg_color="#007AFF",
            hover_color="#0051D5",
            command=save
        ).pack(fill="x", padx=15, pady=(10, 15))
    
    def change_bg_color(self, color, color_var):
        """Cambiar color de fondo del contador"""
        color_var.set(color)
        # Actualizar inmediatamente si no está en modo transparente
        if not self.config.get("transparent_bg", False):
            self.main_frame.configure(fg_color=color)
    
    def toggle_transparent_bg(self, enabled):
        """Alternar fondo transparente"""
        if enabled:
            self.bg_color = "systemTransparent"
            frame_color = "transparent"
        else:
            self.bg_color = "systemTransparent"
            frame_color = self.config.get("bg_color", "#1c1c1e")
        
        # Actualizar el frame principal
        self.main_frame.configure(fg_color=frame_color)
        
        # Guardar configuración
        self.config["transparent_bg"] = enabled
        self.save_config()
        
        # Redibujar el fondo
        self.draw_rounded_bg()
    
    def enable_drag_mode(self, settings_window):
        """Habilitar modo arrastrar"""
        self.drag_mode = True
        settings_window.destroy()
        
        # Cambiar cursor
        self.configure(cursor="hand2")
        
        # Bind eventos de arrastre
        self.bind("<Button-1>", self.start_drag)
        self.bind("<B1-Motion>", self.do_drag)
        self.bind("<ButtonRelease-1>", self.stop_drag)
    
    def start_drag(self, event):
        """Iniciar arrastre"""
        if self.drag_mode:
            self.drag_start_x = event.x
            self.drag_start_y = event.y
    
    def do_drag(self, event):
        """Realizar arrastre"""
        if self.drag_mode:
            x = self.winfo_x() + (event.x - self.drag_start_x)
            y = self.winfo_y() + (event.y - self.drag_start_y)
            self.geometry(f"+{x}+{y}")
    
    def stop_drag(self, event):
        """Detener arrastre y guardar posición"""
        if self.drag_mode:
            self.drag_mode = False
            self.configure(cursor="")
            
            # Unbind eventos
            self.unbind("<Button-1>")
            self.unbind("<B1-Motion>")
            self.unbind("<ButtonRelease-1>")
            
            # Guardar posición
            self.config["window_x"] = self.winfo_x()
            self.config["window_y"] = self.winfo_y()
            self.save_config()

if __name__ == "__main__":
    app = PomodoroModern()
    app.mainloop()
