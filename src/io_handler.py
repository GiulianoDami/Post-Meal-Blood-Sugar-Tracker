import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import jsonschema
from typing import Dict, Any, Tuple

def load_genetic_data(file_path: str) -> Dict[str, Any]:
    """
    Load genetic data from a JSON file.
    
    Args:
        file_path (str): Path to the genetic data file
        
    Returns:
        Dict[str, Any]: Genetic data as dictionary
    """
    try:
        with open(file_path, 'r') as f:
            genetic_data = json.load(f)
        
        # Validate schema if needed
        schema = {
            "type": "object",
            "properties": {
                "genetic_risk_factors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "gene": {"type": "string"},
                            "variant": {"type": "string"},
                            "risk_level": {"type": "number"}
                        },
                        "required": ["gene", "variant", "risk_level"]
                    }
                }
            },
            "required": ["genetic_risk_factors"]
        }
        
        jsonschema.validate(genetic_data, schema)
        return genetic_data
        
    except FileNotFoundError:
        print(f"Error: Genetic data file not found at {file_path}")
        return {}
    except jsonschema.ValidationError as e:
        print(f"Error: Invalid genetic data format - {e}")
        return {}
    except Exception as e:
        print(f"Error loading genetic data: {e}")
        return {}

def export_results(results: Dict[str, Any], output_file: str, format_type: str = 'csv') -> bool:
    """
    Export analysis results to various formats.
    
    Args:
        results (Dict[str, Any]): Analysis results to export
        output_file (str): Output file path
        format_type (str): Export format ('csv', 'json', 'excel')
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if format_type == 'csv':
            df = pd.DataFrame(results)
            df.to_csv(output_file, index=False)
            
        elif format_type == 'json':
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
                
        elif format_type == 'excel':
            df = pd.DataFrame(results)
            df.to_excel(output_file, index=False)
            
        else:
            raise ValueError(f"Unsupported format: {format_type}")
            
        return True
        
    except Exception as e:
        print(f"Error exporting results: {e}")
        return False