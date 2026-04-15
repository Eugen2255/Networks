import socket
import subprocess
import csv


def resolve_dns(domain):
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror as e:
        print(f"[!] DNS ошибка для {domain}: {e}")
        return None

def run_traceroute(ip):

    cmd = ["tracert", "-d", "-h", "15", ip]
    try:
        result = subprocess.run(
            cmd, capture_output=True, 
            text=True, timeout=45, 
            check=False, encoding='cp866'
        )
        if result.returncode != 0:
            return f"traceroute завершился с кодом {result.returncode}\n{result.stderr.strip()}"
        
        return result.stdout.strip()

    except Exception as e:
        return f"Ошибка: {e}"

def main():
    output_file = "dns_traceroute_results.csv"
    domains = ["google.com", "github.com", "example.com", "yandex.ru"]

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["domain", "ip_address", "traceroute_result"])

        for domain in domains:
            ip = resolve_dns(domain)
            if ip:
                trace = run_traceroute(ip)
                writer.writerow([domain, ip, trace])
            else:
                writer.writerow([domain, "N/A", "Ошибка DNS"])

if __name__ == "__main__":
    main()