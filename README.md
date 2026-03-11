# 🍅 Pomodoro Automático - Guía de Instalación

## 📦 Archivos del Proyecto

```
personal-pomodoro/
├── pomodoro_final.py          # Script principal ✅
├── pomodoro_config.example.json  # Ejemplo de configuración ✅
├── README.md                   # Esta guía ✅
├── .gitignore                  # Archivos ignorados por Git ✅
└── backup/                     # Versiones antiguas (no en Git)
```

### Archivos que se crean automáticamente:
- **`pomodoro_config.json`** - Se crea al primer uso con valores por defecto
- **`pomodoro_data.csv`** - Se crea automáticamente para guardar:
  - Estadísticas diarias (tiempo activo, pomodoros, descanso)
  - Tareas actuales con tiempo acumulado
  - Historial diario de tiempo por tarea

> **Nota**: Estos archivos contienen tus datos personales y NO se suben a Git (están en `.gitignore`)

## 🚀 Instalación en un Mac Nuevo

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/miguelangel708/personal-pomodoro.git
cd personal-pomodoro
```

### Paso 2: Instalar Homebrew (si no está instalado)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Paso 3: Instalar Python con Tkinter

```bash
brew install python-tk@3.11
```

### Paso 4: Crear entorno virtual

```bash
/opt/homebrew/bin/python3.11 -m venv venv
```

### Paso 5: Ejecutar la aplicación

```bash
# Modo desarrollo (ver en terminal)
./venv/bin/python3 pomodoro_final.py

# Modo segundo plano
nohup ./venv/bin/python3 pomodoro_final.py > /dev/null 2>&1 &
```

## ⚙️ Configuración

Al abrir la aplicación, haz clic en el botón **⚙** para configurar:

- **Duración Pomodoro**: Tiempo de trabajo (minutos)
- **Duración Descanso**: Tiempo que se acumula por cada pomodoro
- **Meta Diaria**: Cantidad de pomodoros objetivo
- **Tiempo Inactividad**: Segundos sin actividad para pausar automáticamente
- **Transparencia**: Nivel de transparencia del contador (0.3 - 1.0)

## 🎯 Cómo Usar

### Contador Principal
1. **Inicio automático**: El contador comienza cuando detecta actividad
2. **Completar pomodoro**: Cada 25 min (configurable) se suma tiempo de descanso
3. **Activar descanso**: Presiona **☕** para consumir tiempo acumulado
4. **Reanudar trabajo**: Presiona **▶** cuando el descanso termine

### Sistema de Tareas
1. **Expandir panel**: Presiona **▼ Tareas** debajo del contador
2. **Agregar tarea**: Click en **+ Nueva** y escribe el nombre
3. **Seleccionar tarea**: Click en el círculo (○) para activarla (●)
4. **Tracking automático**: El tiempo se registra en la tarea seleccionada
5. **Eliminar tarea**: Click en **−** al lado de cada tarea
6. **Reset diario**: Click en **↻ Reset** para eliminar todas las tareas

### Estadísticas
1. **Ver gráficas**: Presiona **📊** para abrir estadísticas
2. **Productividad General**: Horas trabajadas y pomodoros por día
3. **Tiempo por Tarea**: Distribución de tiempo en los últimos 7 días

## 📊 Archivos de Datos

### `pomodoro_config.json` (se crea automáticamente)
Configuración personalizada:
```json
{
  "pomodoro_minutes": 25,
  "break_minutes": 5,
  "daily_goal": 8,
  "idle_threshold": 60,
  "transparency": 0.9
}
```

### `pomodoro_data.csv` (se crea automáticamente)
Archivo unificado con 3 secciones:

**[STATS]** - Estadísticas diarias:
```csv
2026-03-10,7200,4,900
```
(Fecha, Segundos_Activos, Pomodoros, Descanso_Acumulado)

**[TASKS]** - Tareas actuales:
```csv
Desarrollo Frontend,3600
Reuniones,1800
```
(Nombre_Tarea, Segundos_Dedicados)

**[TASK_HISTORY]** - Historial diario:
```csv
[DATE:2026-03-10]
Desarrollo Frontend,3600
Reuniones,1800
```

## 🛑 Detener la Aplicación

```bash
# Si está en primer plano: Ctrl+C

# Si está en segundo plano:
pkill -f pomodoro_final.py
```

## 🔄 Actualizar en Otro Mac

```bash
cd personal-pomodoro
git pull origin main
```

Los archivos `pomodoro_config.json` y `pomodoro_data.csv` se crearán automáticamente en el nuevo Mac.

## ⚡ Inicio Automático (Opcional)

Para que se ejecute al iniciar sesión, crea un LaunchAgent:

```bash
cat > ~/Library/LaunchAgents/com.pomodoro.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.pomodoro</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/TU_USUARIO/personal-pomodoro/venv/bin/python3</string>
        <string>/Users/TU_USUARIO/personal-pomodoro/pomodoro_final.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# Cargar el servicio
launchctl load ~/Library/LaunchAgents/com.pomodoro.plist
```

**Nota**: Reemplaza `TU_USUARIO` con tu nombre de usuario real.

## 🐛 Solución de Problemas

### La ventana no muestra texto
- Asegúrate de usar Python de Homebrew, no el del sistema
- Verifica: `which python3` debe mostrar `/opt/homebrew/bin/python3.11`

### El contador no avanza
- Revisa la configuración de "Tiempo Inactividad"
- Verifica que estés usando activamente el teclado/mouse

### No se guardan las estadísticas
- Verifica permisos de escritura en la carpeta del proyecto
- Revisa que `pomodoro_data.csv` exista y sea editable

### Archivos no se crean automáticamente
- Ejecuta la aplicación al menos una vez
- Los archivos se crean en el mismo directorio que `pomodoro_final.py`

## 📝 Características

✅ Detección automática de actividad (macOS nativo)  
✅ Pausa automática por inactividad  
✅ Sistema de descansos acumulados  
✅ Tracking de tiempo por tarea  
✅ Historial diario de tareas  
✅ Persistencia de datos por día  
✅ Notificaciones nativas de macOS  
✅ Gráficas de productividad general y por tarea  
✅ 100% portable (sin dependencias externas)  
✅ Transparencia configurable  

---

**Versión**: 2.0  
**Compatibilidad**: macOS 11+  
**Requisitos**: Python 3.11+ con Tkinter  
**Repositorio**: https://github.com/miguelangel708/personal-pomodoro
