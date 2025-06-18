import json

with open("firebase_key.json") as f:
    cred = json.load(f)

cred["private_key"] = cred["private_key"].replace("\n", "\\n")
print("FIREBASE_JSON=" + json.dumps(cred))
