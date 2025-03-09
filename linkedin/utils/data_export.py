import dataclasses
import json
import csv
import os
from datetime import datetime

from linkedin.targets.types import Connection

def save_to_json(data: list[dict], filename=None, output_dir="output"):
    """
    Save data to a JSON file
    
    Args:
        data: List of dictionaries containing the data to save
        filename: Name of the output file (without extension)
        output_dir: Directory to save the file in
    
    Returns:
        Path to the saved file
    """
    if not data:
        print("No data to save to JSON.")
        return None
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"linkedin_data_{timestamp}"
    
    # Ensure filename has .json extension
    if not filename.endswith('.json'):
        filename += '.json'
    
    # Full path to the output file
    output_path = os.path.join(output_dir, filename)
    
    # Save data to JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Data saved to JSON file: {output_path}")
    return output_path

def save_to_csv(data: list[dict], filename=None, output_dir="output"):
    """
    Save data to a CSV file
    
    Args:
        data: List of dictionaries containing the data to save
        filename: Name of the output file (without extension)
        output_dir: Directory to save the file in
    
    Returns:
        Path to the saved file
    """
    if not data:
        print("No data to save to CSV.")
        return None
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"linkedin_data_{timestamp}"
    
    # Ensure filename has .csv extension
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    # Full path to the output file
    output_path = os.path.join(output_dir, filename)
    
    # Get all possible keys from all dictionaries
    all_keys = set()
    for item in data:
        all_keys.update(item.keys())
    
    # Sort keys for consistent column order
    # fieldnames = sorted(all_keys)
    fieldnames = all_keys
    
    # Save data to CSV file
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Data saved to CSV file: {output_path}")
    return output_path

def export_data(data: list[dict], base_filename=None, formats=None, output_dir="output"):
    """
    Export data to multiple formats
    
    Args:
        data: List of Connection objects to save
        base_filename: Base name for the output files (without extension)
        formats: List of formats to export to (e.g., ["json", "csv"])
        output_dir: Directory to save the files in
    
    Returns:
        Dictionary mapping format to output file path
    """
    if not data:
        print("No data to export.")
        return {}
    
    if formats is None:
        formats = ["json", "csv"]
    
    if not base_filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"linkedin_data_{timestamp}"
    
    # Convert Connection objects to dictionaries once
    
    results = {}
    
    if "json" in formats:
        json_path = save_to_json(data, f"{base_filename}.json", output_dir)
        results["json"] = json_path
    
    if "csv" in formats:
        csv_path = save_to_csv(data, f"{base_filename}.csv", output_dir)
        results["csv"] = csv_path
    
    return results