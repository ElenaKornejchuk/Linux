import os
import re
import json
import argparse
from collections import Counter, defaultdict
from datetime import datetime

LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) - - \[(?P<datetime>[^\]]+)\] "(?P<request>[^"]*)" (?P<status>\d{3}) (?P<bytes>\S+) "[^"]*" "[^"]*" (?P<duration>\d+)'
)


def parse_log_line(line):
    match = LOG_PATTERN.match(line)
    if match:
        request = match.group('request')
        method, url, *_ = request.split() if request else ("", "", "")
        return {
            'ip': match.group('ip'),
            'datetime': match.group('datetime'),
            'method': method,
            'url': url,
            'duration': int(match.group('duration')),
        }
    return None


def analyze_log_file(filepath):
    total_requests = 0
    method_counts = Counter()
    ip_counter = Counter()
    slowest_requests = []

    with open(filepath, 'r') as file:
        for line in file:
            parsed = parse_log_line(line)
            if not parsed:
                continue

            total_requests += 1
            method_counts[parsed['method']] += 1
            ip_counter[parsed['ip']] += 1

            slowest_requests.append(parsed)

    top_slowest = sorted(slowest_requests, key=lambda x: x['duration'], reverse=True)[:3]

    result = {
        'file': os.path.basename(filepath),
        'total_requests': total_requests,
        'method_counts': dict(method_counts),
        'top_3_ips': ip_counter.most_common(3),
        'top_3_slowest_requests': top_slowest
    }

    return result


def save_json_report(data, output_dir='.'):
    filename = os.path.splitext(data['file'])[0]
    out_path = os.path.join(output_dir, f"{filename}_report.json")
    with open(out_path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n📄 Отчёт сохранён в: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Анализатор логов access.log")
    parser.add_argument("path", help="Путь до файла или директории с логами")
    args = parser.parse_args()

    if os.path.isdir(args.path):
        files = [os.path.join(args.path, f) for f in os.listdir(args.path) if f.endswith(".log")]
    else:
        files = [args.path]

    for log_file in files:
        print(f"\n📊 Анализируем: {log_file}")
        report = analyze_log_file(log_file)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        save_json_report(report)


if __name__ == "__main__":
    main()
