#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import re
from datetime import datetime
from collections import defaultdict

def get_processes_info():
    """Получение информации о процессах с помощью ps aux"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, check=True)
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Ошибка выполнения команды ps aux: {e}")
        return []
    except FileNotFoundError:
        print("Команда 'ps' не найдена. Убедитесь, что вы используете Linux/Unix систему.")
        return []

def parse_processes(process_lines):
    """Парсинг информации о процессах"""
    if not process_lines:
        return [], {}, 0, 0, {}, {}
    
    users = set()
    user_process_count = defaultdict(int)
    total_memory = 0
    total_cpu = 0
    memory_usage = {}
    cpu_usage = {}
    
    # Пропускаем заголовок
    for line in process_lines[1:]:
        parts = re.split(r'\s+', line.strip())
        if len(parts) < 11:
            continue
            
        user = parts[0]
        cpu = float(parts[2])
        mem = float(parts[3])
        command = ' '.join(parts[10:])
        
        users.add(user)
        user_process_count[user] += 1
        
        total_cpu += cpu
        total_memory += mem
        
        # Запоминаем процессы с максимальным использованием ресурсов
        memory_usage[command] = mem
        cpu_usage[command] = cpu
    
    return list(users), user_process_count, total_memory, total_cpu, memory_usage, cpu_usage

def get_top_process(process_dict, top_n=1):
    """Получение процесса с максимальным использованием ресурса"""
    if not process_dict:
        return "N/A", 0
    
    sorted_processes = sorted(process_dict.items(), key=lambda x: x[1], reverse=True)
    if sorted_processes:
        process_name, usage = sorted_processes[0]
        # Обрезаем имя процесса до 20 символов если нужно
        truncated_name = process_name[:20] + '...' if len(process_name) > 20 else process_name
        return truncated_name, usage
    return "N/A", 0

def generate_report():
    """Генерация отчета о процессах"""
    process_lines = get_processes_info()
    if not process_lines:
        return "Не удалось получить информацию о процессах"
    
    users, user_process_count, total_mem, total_cpu, mem_usage, cpu_usage = parse_processes(process_lines)
    total_processes = sum(user_process_count.values())
    
    # Находим процессы с максимальным использованием ресурсов
    top_mem_process, mem_percent = get_top_process(mem_usage)
    top_cpu_process, cpu_percent = get_top_process(cpu_usage)
    
    # Формируем отчет
    report = []
    report.append("Отчёт о состоянии системы:")
    report.append(f"Пользователи системы: {', '.join(sorted(users))}")
    report.append(f"Процессов запущено: {total_processes}")
    report.append("")
    report.append("Пользовательских процессов:")
    for user, count in sorted(user_process_count.items()):
        report.append(f"{user}: {count}")
    report.append("")
    report.append(f"Всего памяти используется: {total_mem:.1f}%")
    report.append(f"Всего CPU используется: {total_cpu:.1f}%")
    report.append(f"Больше всего памяти использует: {top_mem_process} ({mem_percent:.1f}%)")
    report.append(f"Больше всего CPU использует: {top_cpu_process} ({cpu_percent:.1f}%)")
    
    return '\n'.join(report)

def save_report_to_file(report_content):
    """Сохранение отчета в файл с текущей датой и временем"""
    current_time = datetime.now().strftime("%d-%m-%Y-%H:%M")
    filename = f"{current_time}-scan.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"Отчёт сохранён в файл: {filename}")
    except IOError as e:
        print(f"Ошибка при сохранении файла: {e}")

def main():
    """Основная функция"""
    print("Сбор информации о процессах...")
    report = generate_report()
    
    # Вывод в стандартный поток
    print("\n" + "="*50)
    print(report)
    print("="*50)
    
    # Сохранение в файл
    save_report_to_file(report)

if __name__ == "__main__":
    main()