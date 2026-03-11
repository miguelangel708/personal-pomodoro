#!/bin/bash

# Script para crear una aplicación macOS (.app) del Pomodoro Timer

APP_NAME="PomodoroTimer"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_DIR="$SCRIPT_DIR/$APP_NAME.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

# Crear estructura de directorios
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Crear el script ejecutable
cat > "$MACOS_DIR/pomodoro_launcher" << EOF
#!/bin/bash
# Ruta absoluta al proyecto
PROJECT_DIR="$SCRIPT_DIR"
cd "\$PROJECT_DIR"
"\$PROJECT_DIR/venv/bin/python3" "\$PROJECT_DIR/pomodoro_modern.py" &
EOF

chmod +x "$MACOS_DIR/pomodoro_launcher"

# Crear Info.plist
cat > "$CONTENTS_DIR/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>pomodoro_launcher</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.personal.pomodoro</string>
    <key>CFBundleName</key>
    <string>Pomodoro Timer</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>3.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>11.0</string>
    <key>LSUIElement</key>
    <false/>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Crear un icono simple (emoji como icono)
cp "$SCRIPT_DIR/assets/AppIcon.icns" "$RESOURCES_DIR/AppIcon.icns"

echo "✅ Aplicación creada: $APP_DIR"
echo ""
echo "Para usar:"
echo "1. Arrastra '$APP_NAME.app' al escritorio o al Dock"
echo "2. Haz doble clic para iniciar el Pomodoro Timer"
echo ""
echo "Nota: La primera vez puede pedir permisos de accesibilidad"
