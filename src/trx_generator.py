import random
from datetime import datetime, timedelta
from faker import Faker
from utils import generate_timestamp, round_to_cents
from config import buyer_profiles, consumption_profile, cities

fake = Faker(['es_ES'])

def generate_trxs(profile_data: dict, from_date: datetime):
    customer_name = profile_data['name']
    account_name = profile_data['iban']
    trx_city = profile_data['city']

    salary = round_to_cents(random.uniform(profile_data["salary"][0], profile_data["salary"][1]))
    partner_salary = 0
    if profile_data['has_partner'] and profile_data['partner_works']:
        partner_salary = round_to_cents(random.uniform(profile_data["salary"][0], profile_data["salary"][1]))

    balance = round_to_cents(random.uniform(
        profile_data['initial_balance_range'][0],
        profile_data['initial_balance_range'][1]
    ))

    to_date = datetime.now()

    idx = 1
    trxs = []
    current_date = from_date
    housing_expense = round_to_cents(random.uniform(*consumption_profile["monthly"]["housing"][1 if profile_data['owns_house'] else 0]["range"]))

    months_since_last_extra_income = 0
    extra_income_amount = round_to_cents(salary * 0.1)

    while current_date <= to_date:
        # Monthly salary (or salaries)
        if current_date.day == 1:
            timestamp = generate_timestamp(current_date)
            balance += salary
            trx_id = f"TRX_N-{str(idx).zfill(5)}-{str(fake.unique.random_number(digits=8)).zfill(8)}"
            trx = {
                'customer': customer_name,
                'account': account_name,
                'trx_id': trx_id,
                'timestamp': timestamp.isoformat(),
                'city': trx_city,
                'trx_type': "transfer",
                'trx_cat': "Salary",
                'amount_eur': salary,
                'balance': balance
            }
            trxs.append(trx)
            idx += 1

            if partner_salary > 0:
                balance += partner_salary
                trx_id = f"TRX_N-{str(idx).zfill(5)}-{str(fake.unique.random_number(digits=8)).zfill(8)}"
                trx = {
                    'customer': customer_name,
                    'account': account_name,
                    'trx_id': trx_id,
                    'timestamp': timestamp.isoformat(),
                    'city': trx_city,
                    'trx_type': "transfer",
                    'trx_cat': "Partner Salary",
                    'amount_eur': partner_salary,
                    'balance': balance
                }
                trxs.append(trx)
                idx += 1

            # Extra income every 2-3 months
            months_since_last_extra_income += 1
            if months_since_last_extra_income >= random.randint(2, 3):
                balance += extra_income_amount
                trx_id = f"TRX_N-{str(idx).zfill(5)}-{str(fake.unique.random_number(digits=8)).zfill(8)}"
                trx = {
                    'customer': customer_name,
                    'account': account_name,
                    'trx_id': trx_id,
                    'timestamp': timestamp.isoformat(),
                    'city': trx_city,
                    'trx_type': "transfer",
                    'trx_cat': "Extra Income",
                    'amount_eur': extra_income_amount,
                    'balance': balance
                }
                trxs.append(trx)
                idx += 1
                months_since_last_extra_income = 0

            # Bonus in June and December
            if current_date.month in [6, 12]:
                bonus = round_to_cents(random.uniform(0.9 * salary, 1.1 * salary))
                balance += bonus
                trx_id = f"TRX_N-{str(idx).zfill(5)}-{str(fake.unique.random_number(digits=8)).zfill(8)}"
                trx = {
                    'customer': customer_name,
                    'account': account_name,
                    'trx_id': trx_id,
                    'timestamp': timestamp.isoformat(),
                    'city': trx_city,
                    'trx_type': "transfer",
                    'trx_cat': "Bonus",
                    'amount_eur': bonus,
                    'balance': balance
                }
                trxs.append(trx)
                idx += 1

        # Rent or Mortgage (5th of each month)
        if current_date.day == 5:
            timestamp = generate_timestamp(current_date)
            balance -= housing_expense
            trx_id = f"TRX_N-{str(idx).zfill(5)}-{str(fake.unique.random_number(digits=8)).zfill(8)}"
            trx = {
                'customer': customer_name,
                'account': account_name,
                'trx_id': trx_id,
                'timestamp': timestamp.isoformat(),
                'city': trx_city,
                'trx_type': "Housing",
                'trx_cat': "Mortgage" if profile_data['owns_house'] else "Rent",
                'amount_eur': -housing_expense,
                'balance': balance
            }
            trxs.append(trx)
            idx += 1

        # Utility bills (5th, 6th, or 7th of each month)
        if current_date.day in [5, 6, 7]:
            for service in consumption_profile["monthly"]["basic_services"]:
                if random.random() < 0.33:  # Distribute bills across the 3 days
                    timestamp = generate_timestamp(current_date)
                    bill_amount = round_to_cents(random.uniform(*service["range"]))
                    balance -= bill_amount
                    trx_id = f"TRX_N-{str(idx).zfill(5)}-{str(fake.unique.random_number(digits=8)).zfill(8)}"
                    trx = {
                        'customer': customer_name,
                        'account': account_name,
                        'trx_id': trx_id,
                        'timestamp': timestamp.isoformat(),
                        'city': trx_city,
                        'trx_type': "Basic services",
                        'trx_cat': service["concept"],
                        'amount_eur': -bill_amount,
                        'balance': balance
                    }
                    trxs.append(trx)
                    idx += 1

        # Other trxs based on frequency
        for category in consumption_profile["frequent"] + consumption_profile["occasional"]:
            if random.random() < (category["frequency"] / 30):  # Adjust frequency to daily probability
                timestamp = generate_timestamp(current_date)
                trx_amount = round_to_cents(random.uniform(*category["range"]))
                balance -= trx_amount
                balance = round_to_cents(balance)
                trx_id = f"TRX_N-{str(idx).zfill(5)}-{str(fake.unique.random_number(digits=8)).zfill(8)}"
                trx = {
                    'customer': customer_name,
                    'account': account_name,
                    'trx_id': trx_id,
                    'timestamp': timestamp.isoformat(),
                    'city': trx_city if random.random() < 0.8 else random.choice(cities),
                    'trx_type': "Expense",
                    'trx_cat': category["concept"],
                    'amount_eur': -trx_amount,
                    'balance': balance
                }
                trxs.append(trx)
                idx += 1

        # Advance to the next day
        current_date += timedelta(days=1)

    trxs.sort(key=lambda x: x['trx_id'])

    return {
        "trxs": trxs,
        "trx_count": len(trxs)
    }