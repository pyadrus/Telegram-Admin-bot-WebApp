import subprocess
import sys

# Пути к вашим скриптам и командам
commands = [
    [sys.executable, "app.py"],
    [sys.executable, "bot.py"],
    ["tuna", "http", "8080", "--subdomain=adminbot"]
]

# Запуск всех процессов
processes = [subprocess.Popen(cmd) for cmd in commands]

print("Все процессы запущены. Для остановки нажмите Ctrl+C")
try:
    # Ожидание завершения (чтобы скрипт не завершился сразу)
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    print("\nОстановка всех процессов...")
    for p in processes:
        p.terminate()
