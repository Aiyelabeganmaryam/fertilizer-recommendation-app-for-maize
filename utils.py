
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import requests
import json

class NutrientCalculator:
    """Advanced nutrient calculation utilities"""

    @staticmethod
    def assess_nutrient_status(n_percent: float, p_ppm: float, k_ppm: float) -> Dict[str, str]:
        """Assess nutrient limitation status"""

        n_status = "High" if n_percent < 1.0 else "Medium" if n_percent < 1.5 else "Low"
        p_status = "High" if p_ppm < 15 else "Medium" if p_ppm < 25 else "Low"
        k_status = "High" if k_ppm < 120 else "Medium" if k_ppm < 200 else "Low"

        return {"N": n_status, "P": p_status, "K": k_status}

    @staticmethod
    def calculate_fertilizer_needs(n_rate: float, p_rate: float, k_rate: float, 
                                 farm_size: float) -> Dict[str, float]:
        """Calculate actual fertilizer product requirements"""

        urea_needed = (n_rate / 0.46) * farm_size
        dap_needed = (p_rate / 0.46) * farm_size
        mop_needed = (k_rate / 0.60) * farm_size

        return {
            "urea_kg": urea_needed,
            "dap_kg": dap_needed,
            "mop_kg": mop_needed
        }

    @staticmethod
    def estimate_yield_response(current_yield: float, n_rate: float, 
                              p_rate: float, k_rate: float) -> float:
        """Estimate yield response to fertilizer application"""

        # Simplified Mitscherlich response function
        max_yield = current_yield * 2.5  # Assume potential is 2.5x current

        # Response coefficients (derived from field data)
        n_response = 1 - np.exp(-0.015 * n_rate)
        p_response = 1 - np.exp(-0.020 * p_rate)
        k_response = 1 - np.exp(-0.012 * k_rate)

        # Combined response (multiplicative)
        total_response = n_response * p_response * k_response

        return current_yield + (max_yield - current_yield) * total_response

class WeatherIntegration:
    """Weather data integration for timing recommendations"""

    @staticmethod
    def get_rainfall_forecast(latitude: float, longitude: float) -> Dict:
        """Get rainfall forecast for location"""
        # Placeholder for weather API integration
        return {
            "next_7_days": 45,  # mm
            "next_14_days": 78,  # mm
            "recommendation": "Good conditions for fertilizer application"
        }

    @staticmethod
    def get_planting_calendar(latitude: float) -> Dict:
        """Get optimal planting dates for location"""
        # Simplified based on latitude
        if latitude > 12:
            return {"wet_season": "May-June", "dry_season": "November-December"}
        else:
            return {"wet_season": "April-May", "dry_season": "October-November"}

class MarketIntegration:
    """Market price integration for economic analysis"""

    @staticmethod
    def get_current_prices() -> Dict[str, float]:
        """Get current market prices"""
        # Placeholder for market API integration
        return {
            "maize_naira_kg": 180,
            "maize_usd_kg": 0.45,
            "urea_naira_kg": 480,
            "dap_naira_kg": 1000,
            "mop_naira_kg": 400
        }

    @staticmethod
    def calculate_profitability(yield_increase: float, fertilizer_cost: float,
                              farm_size: float) -> Dict[str, float]:
        """Calculate economic profitability"""

        prices = MarketIntegration.get_current_prices()

        revenue_increase = yield_increase * farm_size * prices["maize_usd_kg"]
        net_profit = revenue_increase - fertilizer_cost
        roi = (net_profit / fertilizer_cost * 100) if fertilizer_cost > 0 else 0

        return {
            "revenue_increase": revenue_increase,
            "net_profit": net_profit,
            "roi_percent": roi,
            "breakeven_yield": fertilizer_cost / prices["maize_usd_kg"] / farm_size
        }

class SpatialAnalysis:
    """Spatial analysis utilities"""

    @staticmethod
    def calculate_spatial_similarity(lat1: float, lon1: float, 
                                   lat2: float, lon2: float) -> float:
        """Calculate spatial similarity between locations"""

        # Haversine distance
        from math import radians, cos, sin, asin, sqrt

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        distance_km = 6371 * c

        # Convert to similarity (closer = more similar)
        similarity = max(0, 1 - distance_km / 100)  # 100km = 0 similarity
        return similarity

    @staticmethod
    def find_similar_farms(target_lat: float, target_lon: float, 
                          farm_database: pd.DataFrame) -> pd.DataFrame:
        """Find farms with similar conditions"""

        if farm_database.empty:
            return pd.DataFrame()

        similarities = []
        for _, farm in farm_database.iterrows():
            sim = SpatialAnalysis.calculate_spatial_similarity(
                target_lat, target_lon, farm['latitude'], farm['longitude']
            )
            similarities.append(sim)

        farm_database['similarity'] = similarities
        return farm_database.sort_values('similarity', ascending=False).head(10)
