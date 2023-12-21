import json

def save(obj: dict, designation: str):
  with open(designation, "w") as f:
    f.write(json.dumps)
