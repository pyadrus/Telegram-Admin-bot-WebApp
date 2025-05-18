import os
import subprocess
import sys

# Путь к корню проекта (где находится scr/)
project_root = os.path.dirname(os.path.abspath(__file__))

# Команды с указанием PYTHONPATH
commands = [
    [sys.executable, "scr/app/app.py"],
    [sys.executable, "scr/bot/bot.py"],
    ["tuna", "http", "8080", "--subdomain=mybotadmin"]
]

# Установить PYTHONPATH на корень проекта
env = os.environ.copy()
env["PYTHONPATH"] = project_root

processes = [subprocess.Popen(cmd, env=env) for cmd in commands]
