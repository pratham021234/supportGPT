import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class TrendAnalysisService:
    def calculate_trend_percentage(self, current_val: float, previous_val: float) -> str:
        """
        Calculates the percentage difference between two values and formats it as a string.
        """
        if previous_val == 0:
            if current_val > 0:
                return "+100.0% from last period"
            return "0.0% from last period"
            
        diff = current_val - previous_val
        percentage = (diff / previous_val) * 100
        
        sign = "+" if percentage > 0 else ""
        return f"{sign}{round(percentage, 1)}% from last period"

    def detect_anomalies(self, data_series: List[float]) -> List[Dict[str, Any]]:
        """
        Detects anomalies in a time series using a simple Z-score / Standard Deviation approach.
        """
        if len(data_series) < 3:
            return []
            
        mean = sum(data_series) / len(data_series)
        variance = sum([((x - mean) ** 2) for x in data_series]) / len(data_series)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return []
            
        anomalies = []
        for i, val in enumerate(data_series):
            z_score = abs(val - mean) / std_dev
            if z_score > 2.0: # simplistic threshold for anomaly
                anomalies.append({
                    "index": i,
                    "value": val,
                    "deviation": round(z_score, 2)
                })
                
        return anomalies

trend_analysis_service = TrendAnalysisService()
