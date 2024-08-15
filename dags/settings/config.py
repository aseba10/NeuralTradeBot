from dotenv import load_dotenv
import os

load_dotenv()

BYBIT_API_KEY= os.getenv('BYBIT_API_KEY')
BYBIT_API_SECRET= os.getenv('BYBIT_API_SECRET')

host = os.getenv('DB_HOST')
database = os.getenv('DB_DATABASE')
port = os.getenv('DB_PORT')
user = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')

ORDER_SIZE_DEFAULT = 10
PROFIT_MARGIN = 1.03
