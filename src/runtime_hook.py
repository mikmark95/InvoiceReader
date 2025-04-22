# runtime_hook.py
import os
import sys

if hasattr(sys, 'frozen'):
    base_dir = os.path.dirname(sys.executable)
    qt_plugins_path = os.path.join(base_dir, 'PyQt6', 'Qt6', 'plugins')
    os.environ['QT_PLUGIN_PATH'] = qt_plugins_path
