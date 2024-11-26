import requests
import time

input_file = 'address_list.txt'
balances_file = 'balances.txt'
found_btc_file = 'balance_current_btc.txt'

addresses = []

try:
    # Read the addresses from the input file
    with open(input_file, 'r') as f:
        addresses = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print(f"Input file '{input_file}' not found.")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred while reading '{input_file}': {e}")
    exit(1)

total_addresses = len(addresses)
processed = 0

with open(balances_file, 'w') as balances_f, open(found_btc_file, 'w') as found_btc_f:
    for addr in addresses:
        try:
            url = f'https://blockchain.info/balance?active={addr}'
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                balance_info = data.get(addr, {})
                final_balance = balance_info.get('final_balance', 0)
                # Convert balance from satoshis to BTC
                final_balance_btc = final_balance / 1e8
                # Write the response to balances.txt
                balances_f.write(f'{addr}: {final_balance_btc} BTC\n')
                # If balance > 0, write to found_btc.txt
                if final_balance > 0:
                    found_btc_f.write(f'{addr}: {final_balance_btc} BTC\n')
                print(f'Processed {addr}: balance {final_balance_btc} BTC')
            elif response.status_code == 429:
                print(f'Rate limit exceeded when processing {addr}. Waiting for 60 seconds.')
                time.sleep(60)
                continue  # Retry the same address after waiting
            else:
                print(f'Error fetching data for {addr}: HTTP {response.status_code}')
                balances_f.write(f'{addr}: Error HTTP {response.status_code}\n')
            time.sleep(2)
        except requests.exceptions.RequestException as e:
            print(f'Network error for {addr}: {e}')
            balances_f.write(f'{addr}: Network error {e}\n')
            time.sleep(2)
        except Exception as e:
            print(f'Unexpected error for {addr}: {e}')
            balances_f.write(f'{addr}: Unexpected error {e}\n')
            time.sleep(2)
        processed += 1

print(f"Processed {processed} addresses out of {total_addresses}.")
