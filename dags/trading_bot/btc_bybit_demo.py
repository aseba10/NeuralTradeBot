import os
import sys
import logging
import joblib
import pandas as pd
import numpy as np
import csv
from pathlib import Path
from datetime import datetime
from tensorflow.keras.models import load_model
from settings.config import BYBIT_API_KEY, BYBIT_API_SECRET, ORDER_SIZE_DEFAULT, PROFIT_MARGIN
from api.postgres import insert_order, get_orders_today
from api.bybit_data import download_30last_candles
from api.bybit_orders import set_buy_order, set_sell_order
from indicators.indicators import calculate_indicators
from indicators.not_tecnical_indicators import notTecnicalIndicators 

# Setting up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adjust the base path
BASE_DIR = os.getcwd()
sys.path.insert(0, BASE_DIR)

def load_model_and_scaler(model_path, scaler_path):
    try:
        model = load_model(model_path)
        scaler = joblib.load(scaler_path)
        return model, scaler
    except Exception as e:
        logger.error(f"Error loading model or scaler: {e}")
        return None, None

def read_buys_from_csv(filename):
    if os.path.exists(filename):
        buys_df = pd.read_csv(filename, header=None)
        buys = buys_df[0].sort_values(ascending=False).tolist()
        logger.info('buys.csv file loaded')
        logger.info(f'Total active buys: {len(buys)}')
        return buys
    else:
        logger.info('buys.csv file not yet created')
        return []

def save_buys_to_csv(buys, filename):
    buys_df = pd.DataFrame(buys)
    buys_df.to_csv(filename, header=False, index=False)
    logger.info(f'{filename} file created')

def CNN_strategy():
    STRATEGY = "CNN Bybit"

    # Load data and calculate indicators
    data = download_30last_candles()
    if data.empty:
        logger.warning('No data loaded')
        return

    logger.info('Data loaded')

    df = calculate_indicators(data)
    if df.empty:
        logger.warning('Indicators not generated')
        return

    logger.info('Indicators generated')
    
    logger.debug(f'Data columns: {df.columns}')

    # Obtain the absolute path to the current directory
    current_dir = Path(__file__).resolve().parent
    model_path = current_dir / 'models' / 'mi_modelo.keras'
    scaler_path = current_dir / 'models' / 'scaler.pkl'

    # Load model and scaler
    modeld, scaler = load_model_and_scaler(model_path, scaler_path)
    if modeld is None or scaler is None:
        return

    # Prepare data for prediction
    X_test_new = df.select_dtypes(include=[np.number])

    X_test_new.replace([np.inf, -np.inf], np.nan, inplace=True)
    X_test_new.fillna(X_test_new.mean(), inplace=True)

    X_test_new = X_test_new.astype(float)
    X_test_new_scaled = scaler.transform(X_test_new)
    X_test_last_record = X_test_new_scaled[-1].reshape(1, -1)

    X_test_last_record = X_test_last_record.reshape((1, 1, 1, X_test_last_record.shape[1]))

    # Perform prediction
    y_pred_last_record = modeld.predict(X_test_last_record)
    signal = np.argmax(y_pred_last_record, axis=1)
    
    logger.info(f"Prediction for the last record: {signal[0]}")

    last_close = df.iloc[-1]['close']
    order_size_buy = ORDER_SIZE_DEFAULT
    order_size_sell = round((ORDER_SIZE_DEFAULT / last_close), 6)
    
    # CSV filename
    filename = 'buys.csv'
    buys = read_buys_from_csv(filename)
    
    # Place Orders
    if signal == 1:
        message = (datetime.now(), 'LONG', last_close, order_size_buy, STRATEGY, "False")
        if len(buys) < 10:
            buy_today = get_orders_today('LONG', STRATEGY)
            if not buy_today:
                if set_buy_order(BYBIT_API_KEY, BYBIT_API_SECRET, order_size_buy):
                    message = (datetime.now(), 'LONG', last_close, order_size_buy, STRATEGY, "True")
                    logger.info("--------- LONG ORDER PLACED ----------")
                    buys.append(last_close)
                    save_buys_to_csv(buys, filename)
                else:
                    logger.error("Error placing buy order")
            else:
                logger.info("Buy order not placed because a buy order was already executed today")
        else:
            logger.info("Buy order not placed because there are more than 10 active buys")
    
    elif signal == 0:
        message = (datetime.now(), 'SHORT', last_close, order_size_sell, STRATEGY, "False")
        sell_today = get_orders_today('SHORT', STRATEGY)
        if not sell_today:
            profit_buy = next((i for i, buy in enumerate(buys) if buy * PROFIT_MARGIN < last_close), None)
            if profit_buy is not None:
                if set_sell_order(BYBIT_API_KEY, BYBIT_API_SECRET, order_size_sell):
                    message = (datetime.now(), 'SHORT', last_close, order_size_sell, STRATEGY, "True")
                    logger.info("--------- SHORT ORDER PLACED ----------")
                    del buys[profit_buy]
                    save_buys_to_csv(buys, filename)
                else:
                    logger.error("Error placing sell order")
            else:
                logger.info("Sell order not placed due to insufficient profit margin")
        else:
            logger.info("Sell order not placed because a sell order was already executed today")

    else:
        message = (datetime.now(), 'None', last_close, 0, STRATEGY, None)

    # Insert into PostgreSQL
    response = insert_order(message)
    logger.info("--------- DATA INSERTED INTO POSTGRES ----------")
    logger.info(f"Final message: {message}")

if __name__ == '__main__':
    CNN_strategy()
    logger.info('------------------------------------')
