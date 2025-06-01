import json


def readjson():
    # Open the JSON file for reading
    with open("data.json", "r") as file:
        # Load the JSON data into a Python dictionary
        data = json.load(file)
        return data





