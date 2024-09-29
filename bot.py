import requests
import time
from colorama import init, Fore, Style
import sys
import os
from datetime import datetime
import pytz

init(autoreset=True)

# API endpoints
API_CLAIM = 'https://elb.seeddao.org/api/v1/seed/claim'
API_BALANCE = 'https://elb.seeddao.org/api/v1/profile/balance'
API_CHECKIN = 'https://elb.seeddao.org/api/v1/login-bonuses'
API_UPGRADE_STORAGE = 'https://elb.seeddao.org/api/v1/seed/storage-size/upgrade'
API_UPGRADE_MINING = 'https://elb.seeddao.org/api/v1/seed/mining-speed/upgrade'
API_UPGRADE_HOLY = 'https://elb.seeddao.org/api/v1/upgrades/holy-water'
API_PROFILE = 'https://elb.seeddao.org/api/v1/profile'
API_TASKS = 'https://elb.seeddao.org/api/v1/tasks/progresses'
API_WORM = 'https://elb.seeddao.org/api/v1/worms'
API_CATCH_WORM = 'https://elb.seeddao.org/api/v1/worms/catch'

# Request headers template
HEADERS_TEMPLATE = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-ID,en-US;q=0.9,en;q=0.8,id;q=0.7',
    'content-length': '0',
    'dnt': '1',
    'origin': 'https://cf.seeddao.org',
    'priority': 'u=1, i',
    'referer': 'https://cf.seeddao.org/',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
}

def read_tokens():
    try:
        with open('query.txt', 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(Fore.RED + "query.txt file is missing.")
        return []
    except Exception as e:
        print(Fore.RED + f"Error reading tokens: {e}")
        return []

def fetch_data(api_url, headers, method="GET", data=None):
    try:
        if method == "POST":
            response = requests.post(api_url, headers=headers, json=data)
        else:
            response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(Fore.RED + f"Failed to fetch data from {api_url}, Status Code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(Fore.RED + f"Request failed: {e}")
        return None

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def verify_balance(headers):
    balance_data = fetch_data(API_BALANCE, headers)
    if balance_data:
        balance = balance_data['data'] / 1000000000
        print(Fore.YELLOW + f"[ Balance ]: {balance:.9f}")
        return True
    return False

def perform_daily_checkin(headers):
    checkin_data = fetch_data(API_CHECKIN, headers, method="POST")
    if checkin_data:
        day = checkin_data.get('data', {}).get('no', '')
        print(Fore.GREEN + f"[ Check-in ]: Successfully checked in | Day {day}")
    else:
        print(Fore.RED + "[ Check-in ]: Failed to check in")

def upgrade(api_url, headers, confirm):
    if confirm.lower() == 'y':
        response = fetch_data(api_url, headers, method="POST")
        if response:
            return "[ Upgrade ]: Successful"
        else:
            return "[ Upgrade ]: Failed"
    return None

def complete_tasks(headers):
    tasks_data = fetch_data(API_TASKS, headers)
    if tasks_data:
        tasks = tasks_data['data']
        for task in tasks:
            if not task.get('task_user', {}).get('completed', False):
                task_id = task['id']
                task_name = task['name']
                response = fetch_data(f'https://elb.seeddao.org/api/v1/tasks/{task_id}', headers, method="POST")
                if response:
                    print(Fore.GREEN + f"[ Task ]: Task '{task_name}' marked complete")
                else:
                    print(Fore.RED + f"[ Task ]: Failed to complete task '{task_name}'")

def process_accounts(tokens, auto_upgrade_storage, auto_upgrade_mining, auto_upgrade_holy, auto_clear_tasks):
    for token in tokens:
        headers = HEADERS_TEMPLATE.copy()
        headers['telegram-data'] = token

        clear_screen()
        # بدلاً من طباعة الـ token، ننتظر الحصول على اسم الحساب
        print(Fore.CYAN + "Processing account...\n")
        
        profile_data = fetch_data(API_PROFILE, headers)
        if profile_data:
            user_name = profile_data['data']['name']
            print(Fore.CYAN + f"Account: {user_name}\n")  # طباعة اسم الحساب فقط
        
        if verify_balance(headers):
            claim_data = fetch_data(API_CLAIM, headers, method="POST")
            if claim_data:
                print(Fore.GREEN + "[ Claim ]: Claim successful")
            else:
                print(Fore.RED + "[ Claim ]: Claim failed")

            perform_daily_checkin(headers)

            if auto_clear_tasks == 'y':
                complete_tasks(headers)

            storage_upgrade_result = upgrade(API_UPGRADE_STORAGE, headers, auto_upgrade_storage)
            mining_upgrade_result = upgrade(API_UPGRADE_MINING, headers, auto_upgrade_mining)
            holy_upgrade_result = upgrade(API_UPGRADE_HOLY, headers, auto_upgrade_holy)
            
            if storage_upgrade_result:
                print(storage_upgrade_result)
            if mining_upgrade_result:
                print(mining_upgrade_result)
            if holy_upgrade_result:
                print(holy_upgrade_result)

        print(Fore.CYAN + "\nFinished processing account. Moving to the next...\n")
        time.sleep(5)

def main():
    tokens = read_tokens()
    if not tokens:
        return
    
    auto_upgrade_storage = input("Upgrade storage? (y/n): ")
    auto_upgrade_mining = input("Upgrade mining? (y/n): ")
    auto_upgrade_holy = input("Upgrade holy? (y/n): ")
    auto_clear_tasks = input("Clear tasks? (y/n): ")

    while True:
        process_accounts(tokens, auto_upgrade_storage, auto_upgrade_mining, auto_upgrade_holy, auto_clear_tasks)
        countdown_timer(3600)
        clear_screen()

def countdown_timer(seconds):
    while seconds > 0:
        sys.stdout.write(f"\r{Fore.CYAN}Waiting {seconds} seconds...")
        sys.stdout.flush()
        time.sleep(1)
        seconds -= 1

if __name__ == "__main__":
    main()
