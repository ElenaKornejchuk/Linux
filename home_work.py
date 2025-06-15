import subprocess
from collections import defaultdict

def get_ps_aux_output():
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    return result.stdout.strip().split('\n')

def parse_ps_aux(lines):
    header = lines[0]
    data_lines = lines[1:]

    user_process_count = defaultdict(int)
    users_set = set()
    total_mem = 0.0
    total_cpu = 0.0

    max_mem = (0.0, "")  # (mem, command)
    max_cpu = (0.0, "")  # (cpu, command)

    for line in data_lines:
        parts = line.split(maxsplit=10)
        if len(parts) < 11:
            continue  # malformed line
        user, pid, cpu, mem, vsz, rss, tty, stat, start, time, command = parts

        cpu = float(cpu)
        mem = float(mem)

        users_set.add(user)
        user_process_count[user] += 1
        total_mem += mem
        total_cpu += cpu

        if mem > max_mem[0]:
            max_mem = (mem, command[:20])
        if cpu > max_cpu[0]:
            max_cpu = (cpu, command[:20])

    return {
        "users": sorted(users_set),
        "total_processes": len(data_lines),
        "user_process_count": user_process_count,
        "total_mem": round(total_mem, 1),
        "total_cpu": round(total_cpu, 1),
        "max_mem_process": max_mem,
        "max_cpu_process": max_cpu,
    }

def print_report(info):
    print("Отчёт о состоянии системы:")
    print("Пользователи системы: " + ", ".join("'" + user + "'" for user in info['users']))
    print(f"Процессов запущено: {info['total_processes']}\n")

    print("Пользовательских процессов:")
    for user, count in info['user_process_count'].items():
        print(f"{user}: {count}")

    print(f"\nВсего памяти используется: {info['total_mem']}%")
    print(f"Всего CPU используется: {info['total_cpu']}%")
    print(f"Больше всего памяти использует: {info['max_mem_process'][1]}")
    print(f"Больше всего CPU использует: {info['max_cpu_process'][1]}")

if __name__ == "__main__":
    ps_output = get_ps_aux_output()
    parsed_info = parse_ps_aux(ps_output)
    print_report(parsed_info)