# -*- coding: utf-8 -*-

import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import ccxt
import datetime
import time
import pandas as pd

def download_30last_candles():
        
    exchange = ccxt.bybit()
    exchange.load_markets()
    
    timeframe = '30m'
    limit = 10000  # Máximo número de filas por solicitud
    total_limit = 2000000  # Límite total de filas
    
    now = datetime.datetime.now()

    new_date = now - datetime.timedelta(hours=56)

    start_date = int(new_date.timestamp() * 1000)

    since = start_date  # Convertir fecha a milisegundos
    end = time.time() * 1000  # Fecha final es la actual
    
    data = []
    current_limit = 0
    symbol = 'BTCUSD'
    while since < end and current_limit < total_limit:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
            if len(ohlcv) == 0:
                break
            data.extend(ohlcv)
            since = ohlcv[-1][0] + 60 * 1000  # Increment since to the end of last fetched data
            current_limit += len(ohlcv)
            time.sleep(1)  # Respetar el límite de solicitudes
        except ccxt.NetworkError as e:
            print('Network error while fetching data:', e)
            time.sleep(1)
        except ccxt.ExchangeError as e:
            print('Exchange error while fetching data:', e)
            break
    
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')  # Convertir el timestamp a formato de fecha y hora
    return df


if __name__ == "__main__":
    print("ByBit Data")
