# 🍅 Pomodoro Automático - Guía de Instalación

## 📦 Archivos Necesarios

Para compartir este proyecto, incluye los siguientes archivos en una carpeta:

```
pomodoro-app/
├── pomodoro_final.py          # Script principal
├── pomodoro_config.json        # Configuración (opcional, se crea automáticamente)
├── pomodoro_stats.csv          # Estadísticas (opcional, se crea automáticamente)
└── README.md                   # Esta guía
```

## 🚀 Instalación en un Mac Nuevo

### Paso 1: Instalar Homebrew (si no está instalado)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Paso 2: Instalar Python con Tkinter

```bash
brew install python-tk@3.11
```

### Paso 3: Copiar la carpeta del proyecto

Copia la carpeta `pomodoro-app` a cualquier ubicación en tu Mac, por ejemplo:

```bash
# Ejemplo: copiar a tu escritorio
cp -r pomodoro-app ~/Desktop/
cd ~/Desktop/pomodoro-app
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

## 🎯 Cómo Usar

1. **Inicio automático**: El contador comienza cuando detecta actividad
2. **Completar pomodoro**: Cada 25 min (configurable) se suma tiempo de descanso
3. **Activar descanso**: Presiona **☕** para consumir tiempo acumulado
4. **Reanudar trabajo**: Presiona **▶** cuando el descanso termine
5. **Ver estadísticas**: Presiona **📊** para ver gráficas de productividad

## 📊 Archivos de Datos

### `pomodoro_config.json`
Configuración personalizada:
```json
{
  "pomodoro_minutes": 25,
  "break_minutes": 5,
  "daily_goal": 8,
  "idle_threshold": 60
}
```

### `pomodoro_stats.csv`
Historial diario (Fecha, Segundos_Activos, Pomodoros, Descanso_Acumulado):
```csv
2026-03-10,7200,4,900
```

## 🛑 Detener la Aplicación

```bash
# Si está en primer plano: Ctrl+C

# Si está en segundo plano:
pkill -f pomodoro_final.py
```

## 🔄 Actualizar en Otro Mac

Simplemente copia la carpeta completa. Los archivos `pomodoro_config.json` y `pomodoro_stats.csv` se crearán automáticamente si no existen.

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
        <string>/Users/TU_USUARIO/Desktop/pomodoro-app/venv/bin/python3</string>
        <string>/Users/TU_USUARIO/Desktop/pomodoro-app/pomodoro_final.py</string>
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
- Revisa que `pomodoro_stats.csv` exista y sea editable

## 📝 Características

✅ Detección automática de actividad (macOS nativo)  
✅ Pausa automática por inactividad  
✅ Sistema de descansos acumulados  
✅ Persistencia de datos por día  
✅ Notificaciones nativas de macOS  
✅ Gráficas de productividad  
✅ 100% portable (sin dependencias externas)  

---

**Versión**: 1.0  
**Compatibilidad**: macOS 11+  
**Requisitos**: Python 3.11+ con Tkinter
