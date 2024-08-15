# -*- coding: utf-8 -*-

import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from pybit.unified_trading import HTTP

def set_buy_order(BYBIT_API_KEY, BYBIT_API_SECRET, ORDER_SIZE_DEFAULT):
    session = HTTP(
        testnet=False,
        api_key=BYBIT_API_KEY,
        api_secret=BYBIT_API_SECRET,
    )

    try:
        # Realizar el pedido de compra
        response = session.place_order(
            category="spot",
            symbol="BTCUSDT",
            side="Buy",
            orderType="Market",
            qty=ORDER_SIZE_DEFAULT,
        )

        # Imprimir la respuesta del pedido de compra
        print("Respuesta del pedido de compra:")
        print(response)

        # Verificar si la orden se ejecutó con éxito
        if response['retCode'] == 0:
            return True
        else:
            print(f"Error en la respuesta de la API: {response['retMsg']} (Código: {response['retCode']})")
            return False
    except Exception as e:
        print(f"Error al realizar el pedido de compra: {e}")
        return False

def set_sell_order(BYBIT_API_KEY, BYBIT_API_SECRET, ORDER_SIZE_DEFAULT):
    session = HTTP(
        testnet=False,
        api_key=BYBIT_API_KEY,
        api_secret=BYBIT_API_SECRET,
    )

    try:
        # Realizar el pedido de venta
        response = session.place_order(
            category="spot",
            symbol="BTCUSDT",
            side="Sell",
            orderType="Market",
            qty=ORDER_SIZE_DEFAULT,
        )

        # Imprimir la respuesta del pedido de venta
        print("Respuesta del pedido de venta:")
        print(response)

        # Verificar si la orden se ejecutó con éxito
        if response['retCode'] == 0:
            return True
        else:
            print(f"Error en la respuesta de la API: {response['retMsg']} (Código: {response['retCode']})")
            return False
    except Exception as e:
        print(f"Error al realizar el pedido de venta: {e}")
        return False

if __name__ == '__main__':
    print('------------------------------------')
