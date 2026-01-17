import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from jsonschema import validate, ValidationError

class BloodSugarTracker:
    def __init__(self):
        self.meals = []
        self.blood_sugar_readings = []
        self.schema = {
            "type": "object",
            "properties": {
                "meal_name": {"type": "string"},
                "carbohydrate_content": {"type": "number", "minimum": 0},
                "timestamp": {"type": "string", "format": "date-time"}
            },
            "required": ["meal_name", "carbohydrate_content", "timestamp"]
        }
    
    def add_meal(self, meal_name, carbohydrate_content, timestamp=None):
        """
        Add a meal to the tracker
        
        Args:
            meal_name (str): Name of the meal
            carbohydrate_content (float): Carbohydrate content in grams
            timestamp (str, optional): ISO format timestamp. Defaults to now.
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        meal_data = {
            "meal_name": meal_name,
            "carbohydrate_content": carbohydrate_content,
            "timestamp": timestamp
        }
        
        try:
            validate(instance=meal_data, schema=self.schema)
            self.meals.append(meal_data)
        except ValidationError as e:
            raise ValueError(f"Invalid meal data: {e.message}")
    
    def record_blood_sugar(self, level, timestamp=None):
        """
        Record a blood sugar reading
        
        Args:
            level (float): Blood sugar level
            timestamp (str, optional): ISO format timestamp. Defaults to now.
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
            
        self.blood_sugar_readings.append({
            "level": level,
            "timestamp": timestamp
        })
    
    def generate_report(self):
        """
        Generate a comprehensive report of blood sugar tracking
        
        Returns:
            dict: Report containing analysis and insights
        """
        if not self.meals or not self.blood_sugar_readings:
            return {"error": "No data available for reporting"}
        
        # Convert to DataFrames for easier analysis
        meals_df = pd.DataFrame(self.meals)
        readings_df = pd.DataFrame(self.blood_sugar_readings)
        
        # Convert timestamps to datetime
        meals_df['timestamp'] = pd.to_datetime(meals_df['timestamp'])
        readings_df['timestamp'] = pd.to_datetime(readings_df['timestamp'])
        
        # Basic statistics
        avg_blood_sugar = readings_df['level'].mean()
        max_blood_sugar = readings_df['level'].max()
        min_blood_sugar = readings_df['level'].min()
        
        # Calculate average carb intake
        avg_carbs = meals_df['carbohydrate_content'].mean()
        
        # Identify high spike meals (assuming > 180 mg/dL is a spike)
        high_spike_meals = meals_df[meals_df['carbohydrate_content'] > 50]
        
        # Create summary report
        report = {
            "summary": {
                "average_blood_sugar": round(avg_blood_sugar, 2),
                "highest_blood_sugar": max_blood_sugar,
                "lowest_blood_sugar": min_blood_sugar,
                "average_carb_intake": round(avg_carbs, 2),
                "total_meals_tracked": len(self.meals),
                "total_readings": len(self.blood_sugar_readings)
            },
            "insights": {
                "high_spike_meals": high_spike_meals.to_dict('records') if not high_spike_meals.empty else [],
                "recommendation": self._generate_recommendation(avg_blood_sugar, avg_carbs)
            }
        }
        
        return report
    
    def _generate_recommendation(self, avg_blood_sugar, avg_carbs):
        """
        Generate personalized recommendation based on tracked data
        
        Args:
            avg_blood_sugar (float): Average blood sugar level
            avg_carbs (float): Average carbohydrate intake
            
        Returns:
            str: Personalized recommendation
        """
        recommendations = []
        
        if avg_blood_sugar > 140:
            recommendations.append("Consider reducing high-carb meals to help manage blood sugar levels.")
        
        if avg_carbs > 60:
            recommendations.append("Try incorporating more fiber-rich foods to slow glucose absorption.")
        
        if not recommendations:
            return "Your blood sugar management looks good! Continue with your current healthy habits."
        
        return ". ".join(recommendations) + "."