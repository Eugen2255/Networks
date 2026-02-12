import subprocess
import csv
import platform
import re


def ping_domain(domain, count=4):
    """
    Выполняет команду ping для указанного домена и возвращает статистику.

    Функция автоматически определяет параметры команды в зависимости от ОС:
    - Windows: использует параметр '-n'
    - Linux/macOS: использует параметр '-c'

    Args:
        domain (str): Доменное имя или IP-адрес для проверки.
        count (int, optional): Количество отправляемых ICMP-пакетов. По умолчанию 4.

    Returns:
        tuple: Кортеж из двух элементов:
            - dict или None: Словарь с распарсенными данными (при успехе) или None (при ошибке).
            - str или None: Сообщение об ошибке (при неудаче) или None (при успехе).

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
    Парсит вывод команды ping и извлекает сетевую статистику.
    Обрабатывает формат вывода как для Windows, так и для Linux/macOS:
    
    Args:
        output (str): Сырой вывод команды ping.
        domain (str): Доменное имя, для которого выполнялся ping.

    Returns:
        dict: Словарь со следующими ключами:
            - 'domain' (str): Исходный домен.
            - 'min_rtt' (str или float или None): Минимальное время отклика (мс).
            - 'avg_rtt' (str или float или None): Среднее время отклика (мс).
            - 'max_rtt' (str или float или None): Максимальное время отклика (мс).
            - 'packet_loss' (float): Процент потерь пакетов (по умолчанию 100.0).
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

# смотрим какая система
system = platform.system().lower() == 'windows'

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