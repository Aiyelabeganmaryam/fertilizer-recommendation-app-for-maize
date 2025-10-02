
# Configuration for Northern Nigeria Fertilizer Advisor
import os
from dataclasses import dataclass

@dataclass
class AppConfig:
    # Application settings
    APP_NAME = "Northern Nigeria Smart Fertilizer Advisor"
    VERSION = "2.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # Database settings
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///fertilizer_advisor.db")

    # API settings
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
    MARKET_API_KEY = os.getenv("MARKET_API_KEY", "")

    # Regional settings
    DEFAULT_LATITUDE = 11.5
    DEFAULT_LONGITUDE = 8.5
    SUPPORTED_STATES = ["Kaduna", "Kano", "Katsina", "Sokoto", "Kebbi", "Zamfara", "Jigawa"]

    # Nutrient thresholds
    N_THRESHOLDS = {"low": 1.0, "medium": 1.5, "high": 2.5}
    P_THRESHOLDS = {"low": 15, "medium": 25, "high": 35}
    K_THRESHOLDS = {"low": 120, "medium": 200, "high": 300}

    # Economic parameters
    MAIZE_PRICE_USD_KG = 0.45
    FERTILIZER_PRICES = {
        "urea_usd_kg": 1.2,
        "dap_usd_kg": 2.5,
        "mop_usd_kg": 1.0
    }

    # Language support
    SUPPORTED_LANGUAGES = {
        "English": "en",
        "Hausa": "ha", 
        "Fulfulde": "ff"
    }
