# 🍅 Pomodoro Timer - Widget Moderno para macOS

Temporizador Pomodoro con diseño moderno estilo Dynamic Island de macOS, construido con CustomTkinter.

## ✨ Características

✅ **Diseño Moderno**: Interfaz estilo Widget de macOS con bordes redondeados y efectos sutiles  
✅ **Detección Automática**: Pausa automática por inactividad  
✅ **Sistema de Descansos**: Acumula tiempo de descanso por cada pomodoro completado  
✅ **Tracking de Tareas**: Registra tiempo dedicado a cada tarea con animaciones fluidas  
✅ **Estadísticas Visuales**: Gráficas de productividad general y por tarea  
✅ **Personalización**: 6 temas de color, transparencia ajustable, posición configurable  
✅ **Notificaciones**: Alertas nativas de macOS  
✅ **Persistencia**: Datos guardados en `~/.pomodoro/`  

## 📦 Instalación

### Opción 1: Usar la aplicación compilada (Recomendado para usuarios)

1. **Descargar**: Descarga `PomodoroTimer-v3.0.zip` de [Releases](https://github.com/miguelangel708/personal-pomodoro/releases)
2. **Descomprimir**: Extrae el archivo ZIP
3. **Instalar**: Arrastra `Pomodoro Timer.app` a tu carpeta `Aplicaciones`
4. **Abrir**: Doble click en la aplicación
   - Si macOS bloquea: `Sistema > Privacidad y Seguridad > Abrir de todos modos`

> ✅ **No requiere instalar Python ni dependencias**

### Opción 2: Ejecutar desde código fuente (Para desarrolladores en macOS)

```bash
# Clonar repositorio
git clone https://github.com/miguelangel708/personal-pomodoro.git
cd personal-pomodoro

# Instalar Python con Tkinter (macOS)
brew install python-tk@3.11

# Crear entorno virtual
/opt/homebrew/bin/python3.11 -m venv ~/pomodoro_env

# Instalar dependencias
~/pomodoro_env/bin/pip install -r requirements.txt

# Ejecutar
~/pomodoro_env/bin/python3 pomodoro_modern.py
```

## 🎨 Personalización

### Temas de Color
Abre configuración (⚙️) y elige entre 6 temas:
- **Deep Black**: Negro puro estilo Dynamic Island (#000000)
- **Material Dark**: Gris oscuro de Apple (#161617)
- **Negro**: Gris muy oscuro (#1c1c1e)
- **Gris Oscuro**: Gris medio (#2c2c2e)
- **Azul Oscuro**: Tono azulado (#1a1a2e)
- **Rojo Oscuro**: Tono rojizo (#1e1a1a)

### Transparencia
- **Transparencia de Ventana**: Ajusta la opacidad general (0.5 - 1.0)
- **Fondo Transparente**: Switch para ocultar el fondo y ver solo los componentes flotando

### Posición
- Click en **📍 Ajustar Posición** para arrastrar el contador
- La posición se guarda automáticamente

## 🎯 Uso

### Contador Principal
- **Inicio automático**: Detecta actividad del teclado/mouse
- **Pausa automática**: Se pausa tras el tiempo de inactividad configurado
- **Completar pomodoro**: Cada 25 min acumula tiempo de descanso
- **Activar descanso**: Click en **●** (botón naranja)

### Sistema de Tareas
1. Click en **⌄** para expandir el panel
2. **+ Nueva**: Agregar tarea
3. **○**: Seleccionar tarea activa
4. **×**: Eliminar tarea
5. **↻ Reset**: Limpiar todas las tareas

### Estadísticas
Click en **◐** para ver:
- Productividad general (horas y pomodoros por día)
- Tiempo por tarea (últimos 7 días)

## 📊 Archivos de Datos

Los datos se guardan en `~/.pomodoro/`:

```
~/.pomodoro/
├── pomodoro_config.json    # Configuración personalizada
└── pomodoro_data.csv        # Estadísticas y tareas
```

### Formato de `pomodoro_data.csv`

**[STATS]** - Estadísticas diarias:
```csv
2026-03-11,7200,4,900
```
(Fecha, Segundos_Activos, Pomodoros, Descanso_Acumulado)

**[TASKS]** - Tareas actuales:
```csv
Desarrollo Frontend,3600
```
(Nombre_Tarea, Segundos_Dedicados)

**[TASK_HISTORY]** - Historial diario:
```csv
[DATE:2026-03-11]
Desarrollo Frontend,3600
```

## 🔧 Compilar la Aplicación

```bash
# Activar entorno virtual
source ~/pomodoro_env/bin/activate

# Compilar con py2app
cd /Users/miguelangelmunoz/Desktop/kiro-labs
./create_app.sh

# La app se genera en: ./PomodoroTimer.app
```

## 🔄 Actualizar en Otro Mac

```bash
cd personal-pomodoro
git pull origin main
```

Los archivos de configuración se crean automáticamente en `~/.pomodoro/` en el nuevo Mac.

## 🐛 Solución de Problemas

### La ventana no muestra texto
- Usa Python de Homebrew: `/opt/homebrew/bin/python3.11`
- Verifica: `which python3` debe mostrar `/opt/homebrew/bin/python3.11`

### El contador no avanza
- Revisa "Tiempo Inactividad" en configuración
- Verifica que estés usando activamente el teclado/mouse

### Archivos no se crean
- Ejecuta la aplicación al menos una vez
- Verifica: `ls -la ~/.pomodoro/`

### Animaciones lentas
- Aumenta la transparencia de ventana a 1.0
- Cierra otras aplicaciones pesadas

## 🎨 Paleta de Colores (Sistema Apple)

- **Verde**: `#34C759` (trabajo activo)
- **Naranja**: `#FF9F0A` (descanso)
- **Rojo**: `#FF3B30` (pausado/eliminar)
- **Azul**: `#007AFF` (acciones principales)
- **Gris**: `#A1A1A6` (texto secundario)

## 📝 Tecnologías

- **Python 3.11+** con Tkinter
- **CustomTkinter 5.2+** para interfaz moderna
- **Matplotlib 3.10+** para gráficas
- **py2app** para compilación en macOS

---

**Versión**: 3.0 (CustomTkinter)  
**Compatibilidad**: macOS 11+  
**Repositorio**: https://github.com/miguelangel708/personal-pomodoro
