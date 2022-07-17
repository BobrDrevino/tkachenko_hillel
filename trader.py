import json
from random import uniform
from argparse import ArgumentParser
import os.path


def load_start_config():
    """
    This function loads a json file with initial input data.
    :return: config with rate, amount UAH, amount USD and delta at start (dict)
    """
    with open('config.json', 'r') as js:
        data = json.load(js)

    with open('updated_config.json', "w") as js:
        json.dump(data, js)

    return data


def start_exchange_rate():
    """
    Function to show the starting exchange rate
    :return: exchange rate at start (int)
    """
    rate_1 = load_start_config()
    start_rate = rate_1['exchange_rate']
    return start_rate


def rate_update():
    """
    Function generates new rate in the XX.XX format and add new value in updated_config.json
    :return: new rate (float)
    """
    with open('config.json', 'r') as js:
        data = json.load(js)

        rate1 = data['exchange_rate']
        uah1 = data['uah']
        usd1 = data['usd']
        delta1 = data['delta']

        new_rate = round(uniform((rate1 - delta1), (rate1 + delta1)), 2)
        dif = {"exchange_rate": new_rate, "uah": uah1, "usd": usd1, "delta": delta1}

    with open('updated_config.json', 'w') as js:
        json.dump(dif, js)

    return new_rate


def change_config(changes):
    """
    This function update config after any changes
    :param : dict with changes after any transactions
    """
    ch_par = changes
    to_change = {'exchange_rate': ch_par['exchange_rate'],
                 'uah': float(round(ch_par['uah'], 2)),
                 'usd': float(round(ch_par['usd'], 2)),
                 'delta': ch_par['delta']}

    with open('updated_config.json', "w") as js:
        json.dump(to_change, js)


def availble_balance():
    """
    Balance check function
    :return: balance (list)
    """
    if os.path.exists('updated_config.json'):
        with open('updated_config.json', 'r') as js:
            data_balance = json.load(js)
            bal_uah = float(data_balance['uah'])
            bal_usd = float(data_balance['usd'])
            result = [bal_uah, bal_usd]
    else:
        with open('config.json', 'r') as js:
            data_balance = json.load(js)
            bal_uah = float(data_balance['uah'])
            bal_usd = float(data_balance['usd'])
            result = [bal_uah, bal_usd]

    return result


def buy_usd(how_many_usd):
    """
    Function to buy $
    :param how_many_usd:
    :return: new params for changeable config (dict)
    """
    all_balance = availble_balance()
    uah_bal = all_balance[0]
    usd_bal = all_balance[1]

    with open('updated_config.json', 'r') as js:
        data = json.load(js)
    rate = data['exchange_rate']

    if how_many_usd * rate <= uah_bal > 0:
        usd_bal += how_many_usd
        uah_bal -= round(how_many_usd * rate, 2)
        difference = {"exchange_rate": rate, "uah": uah_bal, "usd": usd_bal, 'delta': 0.5}
        return change_config(difference)
    else:
        print(f"UNAVAILABLE, REQUIRED BALANCE UAH {how_many_usd * rate}, AVAILABLE {uah_bal}")


def sell_usd(how_many_usd):
    """
    Function to sell $
    :param how_many_usd:
    :return: new params for changeable config (dict)
    """
    all_balance = availble_balance()
    uah_bal = all_balance[0]
    usd_bal = all_balance[1]

    with open('updated_config.json', 'r') as js:
        data = json.load(js)
    rate = data['exchange_rate']

    if how_many_usd <= usd_bal > 0:
        usd_bal -= how_many_usd
        uah_bal += round(how_many_usd * rate, 2)
        difference = {"exchange_rate": rate, "uah": uah_bal, "usd": usd_bal, 'delta': 0.5}
        return change_config(difference)
    else:
        print(f"UNAVAILABLE, REQUIRED BALANCE USD {how_many_usd}, AVAILABLE {usd_bal}")



def buy_usd_for_all_uah():
    """
    Function to buy the maximum possible number of dollars
    :return: new params for changeable config (dict)
    """
    all_balance = availble_balance()
    uah_bal1 = float(all_balance[0])
    usd_bal = float(all_balance[1])

    with open('updated_config.json', 'r') as js:
        data = json.load(js)
    rate = data['exchange_rate']

    if uah_bal1 > 0:
        ua_b1 = uah_bal1 // rate            # Сколько целых $ влазит
        uah_bal = round((uah_bal1 - (ua_b1 * rate))/100, 2)   # Остаток в UAH в копейках

        ua_b2 = round(uah_bal1 - uah_bal, 2)   # Количество гривен, которые доступны под конвертацию без остатка копеек
        usd_bal += round(ua_b2 / rate, 2)  # Количество целых $ и центов, которые можно купить

        difference = {"exchange_rate": rate, "uah": uah_bal, "usd": usd_bal, 'delta': 0.5}
        return change_config(difference)
    else:
        print(f'There is not enough UAH on the balance. Balance: {uah_bal1}')



def buy_uah_for_all_usd():
    """
    Function to buy the UAH for all $
    :return: new params for changeable config (dict)
    """
    all_balance = availble_balance()
    uah_bal = float(all_balance[0])
    usd_bal = float(all_balance[1])

    with open('updated_config.json', 'r') as js:
        data = json.load(js)
    rate = data['exchange_rate']

    if usd_bal > 0:
        uah_bal += round(usd_bal * rate, 2)
        usd_bal = 0
        difference = {"exchange_rate": rate, "uah": uah_bal, "usd": usd_bal, 'delta': 0.5}
        return change_config(difference)
    else:
        print('The $ balance is zero')


args = ArgumentParser()
parsers_command = args.add_subparsers(dest='command')

rate = parsers_command.add_parser('RATE')
available = parsers_command.add_parser('AVAILABLE')
buy_xxx = parsers_command.add_parser('BUY')
sell_xxx = parsers_command.add_parser('SELL')
buy_all = parsers_command.add_parser('BUY ALL')
sell_all = parsers_command.add_parser('SELL ALL')
next_rate = parsers_command.add_parser('NEXT')
restart = parsers_command.add_parser('RESTART')


buy_xxx.add_argument('amount', type=int)
sell_xxx.add_argument('amount', type=int)


args2 = args.parse_args()


if args2.command == 'RATE':
    args_rate = start_exchange_rate()
    print(f'Start exchange rate is: {args_rate}')

elif args2.command == 'AVAILABLE':
    args_balance = availble_balance()
    uah_bal = args_balance[0]
    usd_bal = args_balance[1]
    print(f'USD {usd_bal} | UAH {uah_bal}')

elif args2.command == "BUY ALL":
    buy_usd_for_all_uah()

elif args2.command == "SELL ALL":
    buy_uah_for_all_usd()

elif args2.command == 'BUY':
    buy_usd(args2.amount)

elif args2.command == "SELL":
    sell_usd(args2.amount)

elif args2.command == "NEXT":
    rate_update()

elif args2.command == "RESTART":
    load_start_config()
