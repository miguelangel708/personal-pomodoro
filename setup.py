"""
Setup script para crear aplicación macOS con py2app
"""
from setuptools import setup

APP = ['pomodoro_final.py']
DATA_FILES = [
    ('assets', ['assets/icon.png', 'assets/AppIcon.icns']),
]
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'assets/AppIcon.icns',
    'plist': {
        'CFBundleName': 'Pomodoro Timer',
        'CFBundleDisplayName': 'Pomodoro Timer',
        'CFBundleIdentifier': 'com.personal.pomodoro',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0',
        'LSMinimumSystemVersion': '11.0',
        'LSUIElement': False,
        'NSHighResolutionCapable': True,
    },
    'packages': ['tkinter'],
    'includes': ['subprocess', 'csv', 'json', 'datetime', 'pathlib'],
}

setup(
    name='PomodoroTimer',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
