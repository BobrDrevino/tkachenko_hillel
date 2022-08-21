import json
from random import uniform
from argparse import ArgumentParser
import os.path

CONFIG_FILENAME = 'config.json'
TMP_CONFIG_FILENAME = 'updated_config.json'


def json_read(filename):
    try:
        with open(filename, 'r') as js:
            data = json.load(js)
            return data
    except FileNotFoundError:
        cfg_read = json_read(CONFIG_FILENAME)
        with open(TMP_CONFIG_FILENAME, "w") as js:
            json.dump(cfg_read, js)
            return cfg_read


def json_write(dif):
    with open(TMP_CONFIG_FILENAME, 'w') as js:
        json.dump(dif, js)


def load_start_config():
    config = json_read(CONFIG_FILENAME)
    json_write(config)
    return config


def start_exchange_rate():
    if os.path.exists(TMP_CONFIG_FILENAME):
        start_rate = json_read(TMP_CONFIG_FILENAME)['exchange_rate']
    else:
        start_rate = json_read(CONFIG_FILENAME)['exchange_rate']
    return start_rate


def rate_update():
    data_config = json_read(CONFIG_FILENAME)
    rate = data_config['exchange_rate']
    delta = data_config['delta']
    new_rate = round(uniform((rate - delta), (rate + delta)), 2)

    if os.path.exists(TMP_CONFIG_FILENAME):
        data_up_config = json_read(TMP_CONFIG_FILENAME)
        dif = {"exchange_rate": new_rate,
               "uah": data_up_config['uah'],
               "usd": data_up_config['usd'],
               "delta": delta}
        json_write(dif)
    else:
        dif = {"exchange_rate": new_rate, "uah": data_config['uah'], "usd": data_config['usd'], "delta": delta}
        json_write(dif)

    return new_rate


def availble_balance():
    if os.path.exists(TMP_CONFIG_FILENAME):
        data_up_config = json_read(TMP_CONFIG_FILENAME)
        bal_uah = float(data_up_config['uah'])
        bal_usd = float(data_up_config['usd'])
        result = [bal_uah, bal_usd]

    else:
        data_config = json_read(CONFIG_FILENAME)
        bal_uah = float(data_config['uah'])
        bal_usd = float(data_config['usd'])
        result = [bal_uah, bal_usd]

    return result


all_balance = availble_balance()
data_config = json_read(CONFIG_FILENAME)
data_up_config = json_read(TMP_CONFIG_FILENAME)


def buy_usd(how_many_usd):
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


def buy_usd_all():
    uah_bal = float(all_balance[0])
    usd_bal = float(all_balance[1])
    rate = data_up_config['exchange_rate']

    if uah_bal > 0:
        usd_can_buy = ((uah_bal*100) // rate) / 100
        usd_bal += round(usd_can_buy, 2)
        uah_bal_new = round(uah_bal - (usd_can_buy * rate), 2)

        new_params = {"exchange_rate": rate, "uah": uah_bal_new, "usd": usd_bal, 'delta': 0.5}
        json_write(new_params)


def sell_usd_all():
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
    if args2.amount.isdigit():
        buy_usd(args2.amount)
    else:
        buy_usd_all()

elif args2.command == "SELL":
    if args2.amount.isdigit():
        sell_usd(args2.amount)
    else:
        sell_usd_all()

elif args2.command == "NEXT":
    rate_update()

elif args2.command == "RESTART":
    load_start_config()
