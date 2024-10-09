# from trx_generator import generate_trxs
# from datetime import datetime
# import json
# from collections import OrderedDict
# from pathlib import Path
# from config import buyer_profiles
# from utils import save_to_csv

# def order_trx(trx, profile_name, profile_data):
#     # Crear un diccionario ordenado con el orden de los campos correcto
#     return OrderedDict([
#         ('profile', profile_name),
#         ('name', profile_data['name']),
#         ('surname', profile_data['surname']),
#         ('birth_date', profile_data['birth_date']),
#         ('iban', profile_data['iban']),
#         ('trx_id', trx['trx_id']),
#         ('timestamp', trx['timestamp']),
#         ('city', trx['city']),
#         ('trx_type', trx['trx_type']),
#         ('trx_cat', trx['trx_cat']),
#         ('amount_eur', trx['amount_eur']),
#         ('balance', trx['balance'])
#     ])

# if __name__ == "__main__":
#     start_date = "2022-01-01"
#     all_trxs = []
    
#     for profile_name, profile_data in buyer_profiles.items():
#         print(f"\nGenerating data for {profile_name} profile...")
#         data = generate_trxs(profile_data, datetime.strptime(start_date, "%Y-%m-%d"))
        
#         for trx in data['trxs']:
#             ordered_trx = order_trx(trx, profile_name, profile_data)
#             all_trxs.append(ordered_trx)
        
#         print(f"✅ Generated {data['trx_count']} trxs for {profile_name}")

#     # Crear carpeta de datos
#     project_root = Path(__file__).resolve().parent.parent
#     data_folder = project_root / "data"
#     data_folder.mkdir(parents=True, exist_ok=True)
    
#     # Generar nombre de archivo con fecha y hora actuales
#     current_datetime = datetime.now().strftime("%Y_%m_%d_%H_%M")
#     filename = f"data_bank_trx_{current_datetime}"

#     # Guardar todas las transacciones en un solo archivo JSON
#     json_filename = f"{filename}.json"
#     json_filepath = data_folder / json_filename
#     with open(json_filepath, 'w', encoding='utf-8') as f:
#         json.dump(all_trxs, f, ensure_ascii=False, indent=2)
    
#     # Guardar todas las transacciones en un archivo CSV utilizando la función utilitaria
#     csv_filepath = save_to_csv(all_trxs, filename)

#     # Imprimir información sobre los archivos guardados
#     try:
#         json_relative_path = json_filepath.relative_to(project_root)
#         csv_relative_path = Path(csv_filepath).relative_to(project_root)
        
#         print(f"\n✅ Total trxs generated: {len(all_trxs)}")
#         print(f"✅ JSON file saved at: {json_relative_path}")
#         print(f"✅ CSV  file saved at: {csv_relative_path}")
#     except ValueError as e:
#         print(f"\n❌ Error calculating relative paths: {e}")
#         print(f"✅ Total trxs generated: {len(all_trxs)}")
#         print(f"✅ JSON file saved at: {json_filepath}")
#         print(f"✅ CSV  file saved at: {csv_filepath}")

#     print("\n🚀 Done generating data for all profiles!")


import json
import csv
from datetime import datetime
from pathlib import Path
from config import buyer_profiles
from trx_generator import generate_trxs
from utils import generate_spanish_dni, generate_password

def generate_data():
    users = []
    transactions = []
    start_date = datetime.strptime("2022-01-01", "%Y-%m-%d")

    for profile_name, profile_data in buyer_profiles.items():
        dni = generate_spanish_dni()
        email = f"{profile_data['name'].lower()}.{profile_data['surname'].lower()}@example.com"
        password = generate_password(8)
        
        user = {
            "profile": profile_name,
            "name": profile_data['name'],
            "surname": profile_data['surname'],
            "birth_date": profile_data['birth_date'],
            "dni": dni,
            "email": email,
            "password": password,
            "city": profile_data['city'],
            "iban": profile_data['iban'],
            "balance": 0
        }
        users.append(user)
        
        data = generate_trxs(profile_data, start_date)
        
        for trx in data['trxs']:
            transaction = {
                "dni": dni,
                "category": trx['trx_cat'],
                "amount": trx['amount_eur'],
                "timestamp": {"$date": trx['timestamp']}
            }
            transactions.append(transaction)
            
            # Update user balance
            user['balance'] += trx['amount_eur']

    return users, transactions

def save_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_csv(users, transactions, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['profile', 'name', 'surname', 'birth_date', 'dni', 'email', 'password', 'city', 'iban', 'balance', 'category', 'amount', 'timestamp'])
        
        for user in users:
            user_transactions = [t for t in transactions if t['dni'] == user['dni']]
            if user_transactions:
                for transaction in user_transactions:
                    writer.writerow([
                        user['profile'], user['name'], user['surname'], user['birth_date'],
                        user['dni'], user['email'], user['password'], user['city'], user['iban'], user['balance'],
                        transaction['category'], transaction['amount'], transaction['timestamp']['$date']
                    ])
            else:
                writer.writerow([
                    user['profile'], user['name'], user['surname'], user['birth_date'],
                    user['dni'], user['email'], user['password'], user['city'], user['iban'], user['balance'],
                    '', '', ''
                ])

if __name__ == "__main__":
    users, transactions = generate_data()

    project_root = Path(__file__).resolve().parent
    data_folder = project_root / "data"
    data_folder.mkdir(exist_ok=True)

    users_json_path = data_folder / "userInsert.json"
    transactions_json_path = data_folder / "transactionInsert.json"
    save_json(users, users_json_path)
    save_json(transactions, transactions_json_path)

    csv_path = data_folder / "all_data.csv"
    save_csv(users, transactions, csv_path)

    try:
        users_json_relative_path = users_json_path.relative_to(project_root)
        transactions_json_relative_path = transactions_json_path.relative_to(project_root)
        csv_relative_path = csv_path.relative_to(project_root)
        
        print(f"\n✅ Total users generated: \t\t{len(users)}")
        print(f"✅ Total transactions generated: \t{len(transactions)}")
        print(f"✅ Users         JSON file saved at: {users_json_relative_path}")
        print(f"✅ Transactions  JSON file saved at: {transactions_json_relative_path}")
        print(f"✅ Data          CSV  file saved at: {csv_relative_path}")
    except ValueError as e:
        print(f"\n❌ Error calculating relative paths: {e}")
        print(f"✅ Total users generated: {len(users)}")
        print(f"✅ Total transactions generated: {len(transactions)}")
        print(f"✅ Users JSON file saved at: {users_json_path}")
        print(f"✅ Transactions JSON file saved at: {transactions_json_path}")
        print(f"✅ CSV file saved at: {csv_path}")

    print("\n🚀 Done generating data!")

