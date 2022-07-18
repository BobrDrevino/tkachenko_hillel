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


def cfg_json_read():
    """
    For reading config.json
    :return: k:v from config.json (dict)
    """
    with open('config.json', 'r') as js:
        data = json.load(js)
        return data


def up_cfg_json_read():
    """
    For reading updated_config.json
    :return: k:v from updated_config.json (dict)
    """
    with open('updated_config.json', 'r') as js:
        data = json.load(js)
        return data


def up_cfg_json_write(dif):
    """
    For writing new k:v to updated_config.json
    :param dict with new k:v
    """
    with open('updated_config.json', 'w') as js:
        json.dump(dif, js)


def start_exchange_rate():
    """
    Function to show the starting exchange rate
    :return: exchange rate at start (int)
    """
    if os.path.exists('updated_config.json'):
        start_rate = up_cfg_json_read()['exchange_rate']
    else:
        start_rate = cfg_json_read()['exchange_rate']
    return start_rate


def rate_update():
    """
    Function generates new rate in the XX.XX format and add new value in updated_config.json
    :return: new rate (float)
    """

    rate1 = cfg_json_read()['exchange_rate']
    uah1 = cfg_json_read()['uah']
    usd1 = cfg_json_read()['usd']
    delta1 = cfg_json_read()['delta']

    new_rate = round(uniform((rate1 - delta1), (rate1 + delta1)), 2)
    dif = {"exchange_rate": new_rate, "uah": uah1, "usd": usd1, "delta": delta1}

    up_cfg_json_write(dif)

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

    up_cfg_json_write(to_change)


def availble_balance():
    """
    Balance check function
    :return: balance (list)
    """
    if os.path.exists('updated_config.json'):

        bal_uah = float(up_cfg_json_read()['uah'])
        bal_usd = float(up_cfg_json_read()['usd'])
        result = [bal_uah, bal_usd]
    else:

        bal_uah = float(cfg_json_read()['uah'])
        bal_usd = float(cfg_json_read()['usd'])
        result = [bal_uah, bal_usd]

    return result


def buy_usd(how_many_usd):
    """
    Function to buy $
    :param how_many_usd:
    :return: new params for changeable config (dict)
    """
    how_many = int(how_many_usd)
    all_balance = availble_balance()
    uah_bal = all_balance[0]
    usd_bal = all_balance[1]
    rate = up_cfg_json_read()['exchange_rate']

    if how_many * rate <= uah_bal > 0:
        usd_bal += how_many
        uah_bal -= round(how_many * rate, 2)
        difference = {"exchange_rate": rate, "uah": uah_bal, "usd": usd_bal, 'delta': 0.5}
        change_config(difference)
    else:
        print(f"UNAVAILABLE, REQUIRED BALANCE UAH {how_many * rate}, AVAILABLE {uah_bal}")


def sell_usd(how_many_usd):
    """
    Function to sell $
    :param how_many_usd:
    :return: new params for changeable config (dict)
    """
    how_many = int(how_many_usd)
    all_balance = availble_balance()
    uah_bal = all_balance[0]
    usd_bal = all_balance[1]
    rate = up_cfg_json_read()['exchange_rate']

    if how_many <= usd_bal > 0:
        usd_bal -= how_many
        uah_bal += round(how_many * rate, 2)
        difference = {"exchange_rate": rate, "uah": uah_bal, "usd": usd_bal, 'delta': 0.5}
        change_config(difference)
    else:
        print(f"UNAVAILABLE, REQUIRED BALANCE USD {how_many}, AVAILABLE {usd_bal}")


def buy_usd_for_all_uah():
    """
    Function to buy the maximum possible number of dollars
    :return: new params for changeable config (dict)
    """
    all_balance = availble_balance()
    uah_bal1 = float(all_balance[0])
    usd_bal = float(all_balance[1])
    rate = up_cfg_json_read()['exchange_rate']

    if uah_bal1 > 0:
        ua_b1 = uah_bal1 // rate  # Сколько целых $ влазит
        uah_bal = round((uah_bal1 - (ua_b1 * rate)) / 100, 2)  # Остаток в UAH в копейках

        ua_b2 = round(uah_bal1 - uah_bal, 2)  # Количество гривен, которые доступны под конвертацию без остатка копеек
        usd_bal += round(ua_b2 / rate, 2)  # Количество целых $ и центов, которые можно купить

        difference = {"exchange_rate": rate, "uah": uah_bal, "usd": usd_bal, 'delta': 0.5}
        change_config(difference)


def buy_uah_for_all_usd():
    """
    Function to buy the UAH for all $
    :return: new params for changeable config (dict)
    """
    all_balance = availble_balance()
    uah_bal = float(all_balance[0])
    usd_bal = float(all_balance[1])
    rate = up_cfg_json_read()['exchange_rate']

    if usd_bal > 0:
        uah_bal += round(usd_bal * rate, 2)
        usd_bal = 0
        difference = {"exchange_rate": rate, "uah": uah_bal, "usd": usd_bal, 'delta': 0.5}
        change_config(difference)


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
