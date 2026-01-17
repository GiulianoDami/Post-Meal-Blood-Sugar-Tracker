import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from jsonschema import validate, ValidationError
from typing import Dict, List, Any

class RecommendationEngine:
    """
    A class to provide dietary recommendations based on blood sugar tracking data
    """
    
    def __init__(self):
        """Initialize the recommendation engine with default parameters"""
        self.recommendation_rules = {
            "high_spike_threshold": 40,
            "moderate_spike_threshold": 20,
            "low_carb_meals": ["vegetables", "lean proteins", "healthy fats"],
            "avoid_meals": ["sugary snacks", "white bread", "processed foods"],
            "recommended_foods": ["leafy greens", "berries", "nuts", "fish"]
        }
        
        # Schema for validating input data
        self.data_schema = {
            "type": "object",
            "properties": {
                "blood_sugar_readings": {
                    "type": "array",
                    "items": {"type": "number"}
                },
                "meal_types": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "genetic_risk_factor": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                },
                "activity_level": {
                    "type": "string",
                    "enum": ["sedentary", "light", "moderate", "active"]
                }
            },
            "required": ["blood_sugar_readings", "meal_types", "genetic_risk_factor", "activity_level"]
        }
    
    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data against the defined schema
        
        Args:
            data (Dict[str, Any]): Input data to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            validate(instance=data, schema=self.data_schema)
            return True
        except ValidationError:
            return False
    
    def _calculate_spike_metrics(self, readings: List[float]) -> Dict[str, float]:
        """
        Calculate blood sugar spike metrics from readings
        
        Args:
            readings (List[float]): Blood sugar readings
            
        Returns:
            Dict[str, float]: Spike metrics including average spike and max spike
        """
        if len(readings) < 2:
            return {"average_spike": 0, "max_spike": 0}
            
        # Calculate differences between consecutive readings
        differences = np.diff(readings)
        positive_differences = [diff for diff in differences if diff > 0]
        
        if not positive_differences:
            return {"average_spike": 0, "max_spike": 0}
            
        return {
            "average_spike": float(np.mean(positive_differences)),
            "max_spike": float(max(positive_differences))
        }
    
    def _get_activity_multiplier(self, activity_level: str) -> float:
        """
        Get activity level multiplier for recommendation adjustment
        
        Args:
            activity_level (str): User's activity level
            
        Returns:
            float: Multiplier value
        """
        multipliers = {
            "sedentary": 1.2,
            "light": 1.0,
            "moderate": 0.8,
            "active": 0.6
        }
        return multipliers.get(activity_level, 1.0)
    
    def get_recommendations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate dietary recommendations based on blood sugar data
        
        Args:
            data (Dict[str, Any]): Input data containing blood sugar readings and meal types
            
        Returns:
            Dict[str, Any]: Recommendations including dietary advice and risk assessment
        """
        # Validate input data
        if not self._validate_data(data):
            raise ValueError("Invalid input data format")
        
        # Extract data
        readings = data["blood_sugar_readings"]
        meal_types = data["meal_types"]
        genetic_risk = data["genetic_risk_factor"]
        activity_level = data["activity_level"]
        
        # Calculate spike metrics
        spike_metrics = self._calculate_spike_metrics(readings)
        avg_spike = spike_metrics["average_spike"]
        max_spike = spike_metrics["max_spike"]
        
        # Determine risk level
        risk_level = "low"
        if avg_spike >= self.recommendation_rules["high_spike_threshold"]:
            risk_level = "high"
        elif avg_spike >= self.recommendation_rules["moderate_spike_threshold"]:
            risk_level = "moderate"
        
        # Adjust recommendations based on genetic risk and activity
        activity_multiplier = self._get_activity_multiplier(activity_level)
        adjusted_risk = min(1.0, genetic_risk * activity_multiplier)
        
        # Generate recommendations
        recommendations = []
        
        # General dietary advice
        if risk_level == "high":
            recommendations.append("Consider reducing carbohydrate intake, especially refined carbs")
            recommendations.append("Increase consumption of fiber-rich vegetables and lean proteins")
        elif risk_level == "moderate":
            recommendations.append("Monitor your carbohydrate intake and meal timing")
            recommendations.append("Include more omega-3 rich foods like fish and nuts")
        else:
            recommendations.append("Maintain current healthy eating patterns")
        
        # Activity-based recommendations
        if activity_level in ["sedentary", "light"]:
            recommendations.append("Incorporate light physical activity after meals to help manage blood sugar")
        
        # Genetic risk adjustments
        if adjusted_risk > 0.7:
            recommendations.append("Given your genetic risk factors, consider consulting with a healthcare provider about personalized dietary strategies")
        
        # Specific food recommendations
        food_advice = {
            "foods_to_include": self.recommendation_rules["recommended_foods"],
            "foods_to_avoid": self.recommendation_rules["avoid_meals"],
            "general_tips": [
                "Eat smaller, more frequent meals to prevent large spikes",
                "Pair carbohydrates with protein or fiber to slow absorption",
                "Stay hydrated throughout the day"
            ]
        }
        
        return {
            "risk_assessment": {
                "risk_level": risk_level,
                "average_spike": round(avg_spike, 2),
                "max_spike": round(max_spike, 2),
                "adjusted_risk_factor": round(adjusted_risk, 2)
            },
            "dietary_recommendations": recommendations,
            "food_advice": food_advice
        }