import logging
import os

from binance.lib.utils import config_logging
from binance.spot import Spot
from dotenv import load_dotenv

# Configure logging
config_logging(logging, logging.INFO)
load_dotenv()

# Set up API keys
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Validate API keys
if not API_KEY or not API_SECRET:
    raise ValueError("Binance API credentials are missing. Please check your .env file.")

# Initialize the Binance client
client = Spot(api_key=API_KEY, api_secret=API_SECRET)
