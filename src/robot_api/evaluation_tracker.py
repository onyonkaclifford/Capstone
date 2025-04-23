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


def set_user_input(input_text, verbose=True):
    """Store the user's input"""
    current_record["user_input"] = input_text
    current_record["timestamp"] = datetime.now().isoformat()
    (
        print(f"Evaluation tracker: Recorded user input: {input_text[:50]}...")
        if verbose
        else "No print"
    )


def set_model_output(command, params, verbose=True):
    """Store the model's parsed output"""
    current_record["model_output"] = {"command": command, **params}
    (
        print(f"Evaluation tracker: Recorded model output - command: {command}")
        if verbose
        else "No print"
    )


def set_command_validity(is_valid, verbose=True):
    """Store whether the command is valid"""
    current_record["correct_command"] = is_valid
    print(f"Evaluation tracker: Command valid: {is_valid}") if verbose else "No print"


def set_params_validity(is_valid, verbose=True):
    """Store whether the parameters are valid"""
    current_record["correct_params"] = is_valid
    (
        print(f"Evaluation tracker: Parameters valid: {is_valid}")
        if verbose
        else "No print"
    )


def finalize_record(verbose=True):
    """Finalize the current record and prepare for a new one"""
    print("Evaluation tracker: Finalizing record...") if verbose else "No print"

    # Only add complete records
    if (
        current_record["user_input"] is not None
        and current_record["model_output"] is not None
        and current_record["correct_command"] is not None
    ):

        evaluation_records.append(current_record.copy())
        (
            print(
                f"Evaluation tracker: Added record to batch (total: {len(evaluation_records)})"
            )
            if verbose
            else "No print"
        )

        # Save to file with each finalization
        filepath = save_records()
        (
            print(f"Evaluation tracker: Saved records to {filepath}")
            if verbose
            else "No print"
        )
    else:
        (
            print("Evaluation tracker: Incomplete record, not saving")
            if verbose
            else "No print"
        )
        missing = []
        if current_record["user_input"] is None:
            missing.append("user_input")
        if current_record["model_output"] is None:
            missing.append("model_output")
        if current_record["correct_command"] is None:
            missing.append("correct_command")
        (
            print(f"Evaluation tracker: Missing fields: {', '.join(missing)}")
            if verbose
            else "No print"
        )

    # Reset for next record
    reset_record()


def save_records(filepath="evaluation_results.json", verbose=True):
    """Save all evaluation records to a JSON file"""
    # Use absolute path for clarity - save in the project root
    if not os.path.isabs(filepath):
        # Get the absolute path to the Capstone directory
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../..")
        )
        filepath = os.path.join(project_root, filepath)

    (
        print(
            f"Evaluation tracker: Saving {len(evaluation_records)} records to {filepath}"
        )
        if verbose
        else "No print"
    )

    # Create parent directory only if filepath has a parent directory
    parent_dir = os.path.dirname(filepath)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    # Load existing records if the file exists
    existing_records = []
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                existing_records = json.load(f)
            (
                print(
                    f"Evaluation tracker: Loaded {len(existing_records)} existing records"
                )
                if verbose
                else "No print"
            )
        except (json.JSONDecodeError, FileNotFoundError) as e:
            (
                print(f"Evaluation tracker: Error loading existing records: {e}")
                if verbose
                else "No print"
            )
            existing_records = []

    # Combine with new records
    all_records = existing_records + evaluation_records

    # Write to file
    with open(filepath, "w") as f:
        json.dump(all_records, f, indent=2)

    (
        print(f"Evaluation tracker: Successfully saved {len(all_records)} records")
        if verbose
        else "No print"
    )

    # Clear processed records
    evaluation_records.clear()

    return filepath
