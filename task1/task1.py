import subprocess
import csv
import platform
import re

# смотрим какая система
system = platform.system().lower() == 'windows'

def ping_domain(domain, count=4):
    """
    Пинг домена и получение статистики  
    Первое значение - инфа, второе - ошибка
    """
    # Определяем команду ping в зависимости от ОС
    param = '-n' if system else '-c'
    
    try:
        # Выполняем ping
        result = subprocess.run(
            ['ping', param, str(count), domain],
            capture_output=True,
            text=True,
            encoding='cp866'
        )
        
        output = result.stdout
        
        if result.returncode != 0:
            return None, f"Ошибка ping {domain}"
        
        # Извлекаем данные из вывода ping
        return parse_ping_output(output, domain), None
        
    except Exception as e:
        return None, f"Ошибка: {str(e)}"

def parse_ping_output(output, domain):
    """
    Парсинг вывода команды ping
    """
    data = {
        'domain': domain,
        'min_rtt': None,
        'avg_rtt': None,
        'max_rtt': None,
        'packet_loss': 100.0,
    }

    try:
        # Отдельные регулярные выражения для Windows и Linux
        # Для Windows
        if system:
            # Ищем потерю пакетов
            loss_match = re.search(r'(\d+)% потерь', output)
            if loss_match:
                data['packet_loss'] = float(loss_match.group(1))


            # Ищем статистику RTT
            rtt_match = re.search(r'Минимальное = (\d+)мсек, ' \
                                   'Максимальное = (\d+) мсек, ' \
                                   'Среднее = (\d+) мсек', output)
            
            if rtt_match:
                data['min_rtt'] = rtt_match.group(1)
                data['max_rtt'] = rtt_match.group(2)
                data['avg_rtt'] = rtt_match.group(3)

        # Для Linux   
        else:
            # Ищем потерю пакетов
            loss_match = re.search(r'(\d+)% packet loss', output)
            if loss_match:
                data['packet_loss'] = float(loss_match.group(1))
            
            # Ищем статистику RTT
            rtt_match = re.search(r'(\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)', output)
            if rtt_match:
                data['min_rtt'] = float(rtt_match.group(1))
                data['avg_rtt'] = float(rtt_match.group(2))
                data['max_rtt'] = float(rtt_match.group(3))
        
    except Exception as e:
        data['error'] = f"Ошибка парсинга: {str(e)}"
    
    return data


# Список доменов для проверки
domains = [
    'google.com',
    'wikipedia.org',
    'ya.ru',
    'hh.ru',
    'github.com',
    'ozon.ru',
    'wildberries.ru',
    'qweqweqwe123.com',
    'nexusmods.com',
    'steamcommunity.com'
]

results = []

for domain in domains:
    data, error = ping_domain(domain)
    
    if error:
        print(f"ОШИБКА: {error}")
        results.append({
            'domain': domain,
            'min_rtt_ms': 'N/A',
            'avg_rtt_ms': 'N/A',
            'max_rtt_ms': 'N/A',
            'packet_loss_%': 100,
        })
    else:
        results.append({
            'domain': domain,
            'min_rtt_ms': data['min_rtt'],
            'avg_rtt_ms': data['avg_rtt'],
            'max_rtt_ms': data['max_rtt'],
            'packet_loss_%': data['packet_loss'],
        })

# Сохраняем результаты в CSV
filename = 'results.csv'

with open(filename, 'w', newline='') as csvfile:
    fieldnames = [
        'domain',
        'min_rtt_ms',
        'avg_rtt_ms',
        'max_rtt_ms',
        'packet_loss_%',
    ]
    
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)