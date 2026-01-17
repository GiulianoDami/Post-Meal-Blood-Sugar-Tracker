import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from jsonschema import validate, ValidationError
from typing import List, Dict, Any, Optional


class MealData:
    """Data structure for storing meal information"""
    
    def __init__(self, 
                 timestamp: str,
                 food_items: List[str],
                 serving_sizes: List[float],
                 nutritional_info: Dict[str, float],
                 blood_sugar_before: float,
                 blood_sugar_after: float,
                 duration_minutes: int = 0):
        """
        Initialize MealData object
        
        Args:
            timestamp: ISO format timestamp of meal
            food_items: List of food item names
            serving_sizes: List of serving sizes corresponding to food items
            nutritional_info: Dictionary with nutritional values (carbs, protein, fat)
            blood_sugar_before: Blood sugar level before meal (mg/dL)
            blood_sugar_after: Blood sugar level after meal (mg/dL)
            duration_minutes: Time elapsed between meal and blood sugar measurement
        """
        self.timestamp = timestamp
        self.food_items = food_items
        self.serving_sizes = serving_sizes
        self.nutritional_info = nutritional_info
        self.blood_sugar_before = blood_sugar_before
        self.blood_sugar_after = blood_sugar_after
        self.duration_minutes = duration_minutes
        
        # Validate inputs
        self._validate_inputs()
    
    def _validate_inputs(self):
        """Validate the input parameters"""
        if len(self.food_items) != len(self.serving_sizes):
            raise ValueError("Food items and serving sizes must have the same length")
        
        if self.blood_sugar_before < 0 or self.blood_sugar_after < 0:
            raise ValueError("Blood sugar values must be non-negative")
        
        if self.duration_minutes < 0:
            raise ValueError("Duration must be non-negative")
    
    def get_glucose_spike(self) -> float:
        """Calculate glucose spike (after - before)"""
        return max(0, self.blood_sugar_after - self.blood_sugar_before)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'timestamp': self.timestamp,
            'food_items': self.food_items,
            'serving_sizes': self.serving_sizes,
            'nutritional_info': self.nutritional_info,
            'blood_sugar_before': self.blood_sugar_before,
            'blood_sugar_after': self.blood_sugar_after,
            'duration_minutes': self.duration_minutes,
            'glucose_spike': self.get_glucose_spike()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create MealData instance from dictionary"""
        return cls(
            timestamp=data['timestamp'],
            food_items=data['food_items'],
            serving_sizes=data['serving_sizes'],
            nutritional_info=data['nutritional_info'],
            blood_sugar_before=data['blood_sugar_before'],
            blood_sugar_after=data['blood_sugar_after'],
            duration_minutes=data['duration_minutes']
        )


class GeneticData:
    """Data structure for storing genetic risk information"""
    
    def __init__(self, 
                 gene_variants: Dict[str, str],
                 risk_factors: Dict[str, float],
                 family_history: Dict[str, bool],
                 ethnicity: str = "",
                 age: int = 0):
        """
        Initialize GeneticData object
        
        Args:
            gene_variants: Dictionary mapping gene names to variant types
            risk_factors: Dictionary mapping risk factors to their scores (0-1)
            family_history: Dictionary mapping conditions to family history presence
            ethnicity: Patient's ethnicity
            age: Patient's age
        """
        self.gene_variants = gene_variants
        self.risk_factors = risk_factors
        self.family_history = family_history
        self.ethnicity = ethnicity
        self.age = age
        
        # Validate inputs
        self._validate_inputs()
    
    def _validate_inputs(self):
        """Validate the input parameters"""
        for key, value in self.risk_factors.items():
            if not isinstance(value, (int, float)) or value < 0 or value > 1:
                raise ValueError(f"Risk factor {key} must be a value between 0 and 1")
        
        if self.age < 0:
            raise ValueError("Age must be non-negative")
    
    def get_overall_risk_score(self) -> float:
        """Calculate overall genetic risk score"""
        if not self.risk_factors:
            return 0.0
        
        # Simple average of all risk factors
        return sum(self.risk_factors.values()) / len(self.risk_factors)
    
    def get_alzheimers_risk_factor(self) -> float:
        """Get Alzheimer's specific risk factor"""
        return self.risk_factors.get('alzheimers', 0.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'gene_variants': self.gene_variants,
            'risk_factors': self.risk_factors,
            'family_history': self.family_history,
            'ethnicity': self.ethnicity,
            'age': self.age,
            'overall_risk_score': self.get_overall_risk_score(),
            'alzheimers_risk_factor': self.get_alzheimers_risk_factor()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create GeneticData instance from dictionary"""
        return cls(
            gene_variants=data['gene_variants'],
            risk_factors=data['risk_factors'],
            family_history=data['family_history'],
            ethnicity=data['ethnicity'],
            age=data['age']
        )