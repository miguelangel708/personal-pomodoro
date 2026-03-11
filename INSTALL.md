# 🚀 Guía de Instalación Rápida

## Para Usuarios (Usar la App)

1. **Descargar** `PomodoroTimer.app` de [Releases](https://github.com/miguelangel708/personal-pomodoro/releases)
2. **Arrastrar** a la carpeta `Aplicaciones`
3. **Abrir** con doble click
   - Si macOS bloquea: `Sistema > Privacidad y Seguridad > Abrir de todos modos`

## Para Desarrolladores (Ejecutar desde código)

### Instalación Inicial

```bash
# 1. Clonar repositorio
git clone https://github.com/miguelangel708/personal-pomodoro.git
cd personal-pomodoro

# 2. Instalar Python con Tkinter
brew install python-tk@3.11

# 3. Crear entorno virtual
/opt/homebrew/bin/python3.11 -m venv ~/pomodoro_env

# 4. Instalar dependencias
~/pomodoro_env/bin/pip install -r requirements.txt

# 5. Ejecutar
~/pomodoro_env/bin/python3 pomodoro_modern.py
```

### Compilar la Aplicación

```bash
# Desde el directorio del proyecto
./create_app.sh

# La app se genera en: ./PomodoroTimer.app
```

### Actualizar en Otro Mac

```bash
cd personal-pomodoro
git pull origin main
~/pomodoro_env/bin/python3 pomodoro_modern.py
```

## 📦 Dependencias

- **Python 3.11+** con Tkinter
- **customtkinter 5.2+**
- **matplotlib 3.10+**

## 📁 Estructura de Archivos

```
personal-pomodoro/
├── pomodoro_modern.py      # Script principal (CustomTkinter)
├── pomodoro_final.py       # Versión anterior (Tkinter)
├── create_app.sh           # Script de compilación
├── README.md               # Documentación completa
├── INSTALL.md              # Esta guía
├── assets/                 # Iconos
│   └── AppIcon.icns
└── ~/.pomodoro/            # Datos del usuario (se crea automáticamente)
    ├── pomodoro_config.json
    └── pomodoro_data.csv
```

## ⚡ Inicio Rápido

```bash
# Ejecutar directamente
~/pomodoro_env/bin/python3 pomodoro_modern.py

# O usar la app compilada
open PomodoroTimer.app
```

## 🐛 Problemas Comunes

### "No module named 'customtkinter'"
```bash
~/pomodoro_env/bin/pip install -r requirements.txt
```

### "La ventana no muestra texto"
Usa Python de Homebrew:
```bash
brew install python-tk@3.11
```

### "Permission denied: ./create_app.sh"
```bash
chmod +x create_app.sh
```

---

**Versión**: 3.0  
**Repositorio**: https://github.com/miguelangel708/personal-pomodoro
