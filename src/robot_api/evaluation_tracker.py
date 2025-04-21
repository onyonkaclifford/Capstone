"""
Simple evaluation tracker for the RobotAPI
"""
import json
import os
from datetime import datetime

# Global evaluation record
current_record = {
    "user_input": None,
    "model_output": None,
    "correct_command": None,
    "correct_params": None,
    "timestamp": None,
}

# List to store all evaluations
evaluation_records = []

def reset_record():
    """Reset the current evaluation record"""
    global current_record
    current_record = {
        "user_input": None,
        "model_output": None,
        "correct_command": None,
        "correct_params": None,
        "timestamp": None,
    }

def set_user_input(input_text):
    """Store the user's input"""
    global current_record
    current_record["user_input"] = input_text
    current_record["timestamp"] = datetime.now().isoformat()

def set_model_output(command, params):
    """Store the model's parsed output"""
    global current_record
    current_record["model_output"] = {"command": command, **params}

def set_command_validity(is_valid):
    """Store whether the command is valid"""
    global current_record
    current_record["correct_command"] = is_valid

def set_params_validity(is_valid):
    """Store whether the parameters are valid"""
    global current_record
    current_record["correct_params"] = is_valid

def finalize_record():
    """Finalize the current record and prepare for a new one"""
    global current_record, evaluation_records
    
    # Only add complete records
    if (current_record["user_input"] is not None and 
        current_record["model_output"] is not None and
        current_record["correct_command"] is not None):
        evaluation_records.append(current_record.copy())
    
    # Save to file with each finalization
    save_records()
    
    # Reset for next record
    reset_record()

def save_records(filepath="evaluation_results.json"):
    """Save all evaluation records to a JSON file"""
    global evaluation_records
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    
    # Load existing records if the file exists
    existing_records = []
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                existing_records = json.load(f)
        except json.JSONDecodeError:
            existing_records = []
    
    # Combine with new records
    all_records = existing_records + evaluation_records
    
    # Write to file
    with open(filepath, "w") as f:
        json.dump(all_records, f, indent=2)
    
    return filepath