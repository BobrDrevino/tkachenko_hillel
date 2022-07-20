import json
from random import uniform
from argparse import ArgumentParser
import os.path


def json_read(filename):
    """
    For reading config.json and updated_config.json
    :return: k:v from json (dict)
    """
    try:
        with open(filename, 'r') as js:
            data = json.load(js)
            return data
    except FileNotFoundError:
        with open('updated_config.json', "w") as js:
            json.dump(json_read('config.json'), js)
            return json_read('config.json')


def json_write(dif):
    """
    For writing new k:v to updated_config.json
    :param dif: dict with new params
    """
    with open('updated_config.json', 'w') as js:
        json.dump(dif, js)


def load_start_config():
    """
    This function loads a json file with initial input data.
    :return: config with rate, amount UAH, amount USD and delta at start (dict)
    """
    json_read('config.json')

    json_write(json_read('config.json'))

    return json_read('config.json')


def start_exchange_rate():
    """
    Function to show the starting exchange rate
    :return: exchange rate at start (int)
    """
    if os.path.exists('updated_config.json'):
        start_rate = json_read('updated_config.json')['exchange_rate']
    else:
        start_rate = json_read('config.json')['exchange_rate']
    return start_rate


def rate_update():
    """
    Function generates new rate in the XX.XX format and add new value in updated_config.json
    :return: new rate (float)
    """
    data_config = json_read('config.json')
    rate1 = data_config['exchange_rate']
    delta1 = data_config['delta']
    new_rate = round(uniform((rate1 - delta1), (rate1 + delta1)), 2)

    if os.path.exists('updated_config.json'):
        data_up_config = json_read('updated_config.json')
        dif = {"exchange_rate": new_rate,
               "uah": data_up_config['uah'],
               "usd": data_up_config['usd'],
               "delta": delta1}
        json_write(dif)
    else:
        dif = {"exchange_rate": new_rate, "uah": data_config['uah'], "usd": data_config['usd'], "delta": delta1}
        json_write(dif)

    return new_rate


def availble_balance():
    """
    Balance check function
    :return: balance (list)
    """

    if os.path.exists('updated_config.json'):
        data_up_config = json_read('updated_config.json')
        bal_uah = float(data_up_config['uah'])
        bal_usd = float(data_up_config['usd'])
        result = [bal_uah, bal_usd]

    else:
        data_config = json_read('config.json')
        bal_uah = float(data_config['uah'])
        bal_usd = float(data_config['usd'])
        result = [bal_uah, bal_usd]

    return result


all_balance = availble_balance()
data_config = json_read('config.json')
data_up_config = json_read('updated_config.json')


def buy_usd(how_many_usd):
    """
    Function to buy $
    :param how_many_usd:
    :return: new params for changeable config (dict)
    """
    how_many = int(how_many_usd)
    uah_bal = all_balance[0]
    usd_bal = all_balance[1]
    rate = data_up_config['exchange_rate']

    if how_many * rate <= uah_bal > 0:
        usd_bal += how_many
        uah_bal -= round(how_many * rate, 2)
        difference = {"exchange_rate": rate,
                      "uah": uah_bal,
                      "usd": usd_bal,
                      'delta': 0.5}
        json_write(difference)
    else:
        print(f"UNAVAILABLE, REQUIRED BALANCE UAH {how_many * rate}, AVAILABLE {uah_bal}")


def sell_usd(how_many_usd):
    """
    Function to sell $
    :param how_many_usd:
    :return: new params for changeable config (dict)
    """
    how_many = int(how_many_usd)
    uah_bal = all_balance[0]
    usd_bal = all_balance[1]
    rate = data_up_config['exchange_rate']

    if how_many <= usd_bal:
        usd_bal -= how_many
        uah_bal += round(how_many * rate, 2)
        difference = {"exchange_rate": rate, "uah": uah_bal, "usd": usd_bal, 'delta': 0.5}
        json_write(difference)
    else:
        print(f"UNAVAILABLE, REQUIRED BALANCE USD {how_many}, AVAILABLE {usd_bal}")


def buy_usd_for_all_uah():
    """
    Function to buy the maximum possible number of dollars
    :return: new params for changeable config (dict)
    """

    uah_bal1 = float(all_balance[0])
    usd_bal = float(all_balance[1])
    rate = data_up_config['exchange_rate']

    if uah_bal1 > 0:
        ua_b1 = uah_bal1 // rate  # Сколько целых $ влазит
        uah_bal = round((uah_bal1 - (ua_b1 * rate)) / 100, 2)  # Остаток в UAH в копейках

        ua_b2 = round(uah_bal1 - uah_bal, 2)  # Количество гривен, которые доступны под конвертацию без остатка копеек
        usd_bal += round(ua_b2 / rate, 2)  # Количество целых $ и центов, которые можно купить

        difference = {"exchange_rate": rate, "uah": uah_bal, "usd": usd_bal, 'delta': 0.5}
        json_write(difference)


def buy_uah_for_all_usd():
    """
    Function to buy the UAH for all $
    :return: new params for changeable config (dict)
    """
    uah_bal = float(all_balance[0])
    usd_bal = float(all_balance[1])
    rate = data_up_config['exchange_rate']

    if usd_bal > 0:
        uah_bal += round(usd_bal * rate, 2)
        usd_bal = 0
        difference = {"exchange_rate": rate, "uah": uah_bal, "usd": usd_bal, 'delta': 0.5}
        json_write(difference)


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

buy_xxx.add_argument('amount')
sell_xxx.add_argument('amount')

args2 = args.parse_args()

if args2.command == 'RATE':
    args_rate = start_exchange_rate()
    print(args_rate)

elif args2.command == 'AVAILABLE':
    args_balance = availble_balance()
    uah_bal = args_balance[0]
    usd_bal = args_balance[1]
    print(f'USD {usd_bal} | UAH {uah_bal}')

elif args2.command == 'BUY':
    try:
        if type(int(args2.amount)) is int:
            buy_usd(args2.amount)
    except ValueError:
        buy_usd_for_all_uah()

elif args2.command == "SELL":
    try:
        if type(int(args2.amount)) is int:
            sell_usd(args2.amount)
    except ValueError:
        buy_uah_for_all_usd()

elif args2.command == "NEXT":
    rate_update()

elif args2.command == "RESTART":
    load_start_config()
