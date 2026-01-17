import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from jsonschema import validate, ValidationError
from typing import Dict, List, Any

class AnalysisEngine:
    def __init__(self, data: pd.DataFrame):
        """
        Initialize the AnalysisEngine with blood sugar data
        
        Args:
            data (pd.DataFrame): DataFrame containing blood sugar measurements
        """
        self.data = data
        self._validate_data()
        
    def _validate_data(self):
        """Validate that the data meets required schema"""
        schema = {
            "type": "object",
            "properties": {
                "timestamp": {"type": "string"},
                "blood_sugar": {"type": "number"},
                "meal_type": {"type": "string"},
                "glucose_level": {"type": "number"}
            },
            "required": ["timestamp", "blood_sugar"]
        }
        
        try:
            # Validate each row against schema
            for _, row in self.data.iterrows():
                validate(instance=row.to_dict(), schema=schema)
        except ValidationError as e:
            raise ValueError(f"Data validation error: {e.message}")
    
    def analyze_trends(self) -> Dict[str, Any]:
        """
        Analyze blood sugar trends and return statistical insights
        
        Returns:
            Dict containing trend analysis results
        """
        if self.data.empty:
            return {}
            
        # Calculate basic statistics
        stats = {
            'mean_blood_sugar': float(self.data['blood_sugar'].mean()),
            'max_blood_sugar': float(self.data['blood_sugar'].max()),
            'min_blood_sugar': float(self.data['blood_sugar'].min()),
            'std_blood_sugar': float(self.data['blood_sugar'].std()),
            'median_blood_sugar': float(self.data['blood_sugar'].median())
        }
        
        # Calculate time-based trends
        if 'timestamp' in self.data.columns:
            self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
            self.data = self.data.sort_values('timestamp')
            
            # Calculate rate of change
            if len(self.data) > 1:
                time_diff = self.data['timestamp'].diff().dt.total_seconds() / 3600  # hours
                sugar_diff = self.data['blood_sugar'].diff()
                rate_of_change = (sugar_diff / time_diff).dropna()
                stats['avg_rate_of_change'] = float(rate_of_change.mean())
        
        # Meal type analysis
        if 'meal_type' in self.data.columns:
            meal_stats = self.data.groupby('meal_type')['blood_sugar'].agg([
                'mean', 'max', 'min', 'std'
            ]).to_dict('index')
            stats['meal_analysis'] = meal_stats
            
        # Risk assessment based on thresholds
        high_spikes = len(self.data[self.data['blood_sugar'] > 140])
        normal_range = len(self.data[(self.data['blood_sugar'] >= 70) & 
                                   (self.data['blood_sugar'] <= 140)])
        low_spikes = len(self.data[self.data['blood_sugar'] < 70])
        
        stats['risk_assessment'] = {
            'high_spike_count': int(high_spikes),
            'normal_range_count': int(normal_range),
            'low_spike_count': int(low_spikes),
            'risk_level': self._assess_risk(high_spikes, normal_range, low_spikes)
        }
        
        return stats
    
    def _assess_risk(self, high_spikes: int, normal_range: int, low_spikes: int) -> str:
        """Assess overall risk level based on blood sugar patterns"""
        total = high_spikes + normal_range + low_spikes
        
        if total == 0:
            return "unknown"
            
        high_spike_ratio = high_spikes / total
        
        if high_spike_ratio > 0.3:
            return "high"
        elif high_spike_ratio > 0.15:
            return "moderate"
        else:
            return "low"
    
    def generate_report(self) -> str:
        """
        Generate a comprehensive report of blood sugar analysis
        
        Returns:
            Formatted string report
        """
        analysis = self.analyze_trends()
        
        if not analysis:
            return "No data available for analysis."
            
        report_lines = [
            "POST-MEAL BLOOD SUGAR ANALYSIS REPORT",
            "=" * 40,
            "",
            f"Overall Statistics:",
            f"  Average Blood Sugar: {analysis.get('mean_blood_sugar', 0):.1f} mg/dL",
            f"  Maximum Blood Sugar: {analysis.get('max_blood_sugar', 0):.1f} mg/dL",
            f"  Minimum Blood Sugar: {analysis.get('min_blood_sugar', 0):.1f} mg/dL",
            f"  Standard Deviation: {analysis.get('std_blood_sugar', 0):.1f} mg/dL",
            "",
            f"Risk Assessment:",
            f"  Risk Level: {analysis.get('risk_assessment', {}).get('risk_level', 'unknown').title()}",
            f"  High Spikes: {analysis.get('risk_assessment', {}).get('high_spike_count', 0)}",
            f"  Normal Range: {analysis.get('risk_assessment', {}).get('normal_range_count', 0)}",
            f"  Low Spikes: {analysis.get('risk_assessment', {}).get('low_spike_count', 0)}",
            ""
        ]
        
        # Add meal analysis if available
        if 'meal_analysis' in analysis:
            report_lines.append("Meal Type Analysis:")
            for meal_type, stats in analysis['meal_analysis'].items():
                report_lines.append(f"  {meal_type}:")
                report_lines.append(f"    Mean: {stats['mean']:.1f} mg/dL")
                report_lines.append(f"    Max: {stats['max']:.1f} mg/dL")
                report_lines.append(f"    Min: {stats['min']:.1f} mg/dL")
                report_lines.append(f"    Std Dev: {stats['std']:.1f} mg/dL")
            report_lines.append("")
        
        # Add recommendations based on risk level
        risk_level = analysis.get('risk_assessment', {}).get('risk_level', 'unknown')
        recommendations = self._get_recommendations(risk_level)
        
        report_lines.extend(["Recommendations:", recommendations])
        
        return "\n".join(report_lines)
    
    def _get_recommendations(self, risk_level: str) -> str:
        """Generate recommendations based on risk level"""
        recommendations = {
            "high": (
                "Your blood sugar patterns indicate a high risk of spikes. "
                "Consider consulting with a healthcare provider immediately. "
                "Focus on reducing refined carbohydrates and increasing fiber intake. "
                "Monitor blood sugar more frequently."
            ),
            "moderate": (
                "Your blood sugar patterns show moderate risk. "
                "Consider dietary modifications such as smaller portion sizes "
                "and choosing complex carbohydrates over simple sugars. "
                "Regular monitoring is recommended."
            ),
            "low": (
                "Your blood sugar patterns appear well-managed. "
                "Continue maintaining healthy eating habits and regular monitoring. "
                "Consider tracking your diet to identify patterns that support stable blood sugar."
            ),
            "unknown": (
                "Insufficient data to assess risk level. "
                "Ensure consistent data collection for accurate analysis."
            )
        }
        
        return recommendations.get(risk_level, recommendations["unknown"])