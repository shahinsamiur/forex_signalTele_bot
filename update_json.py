import json

def update_json(data, file_path="data.json"):
    try:
        # Step 1: Read the existing JSON content
        try:
            with open(file_path, "r") as file:
                current_data = json.load(file)
        except FileNotFoundError:
            current_data = {}

        # Step 2: Update only the provided keys
        current_data.update(data)

        # Step 3: Write back the updated JSON
        with open(file_path, "w") as file:
            json.dump(current_data, file, indent=4)

        return "done"

    except Exception as e:
        return f"Error: {e}"
