import os

dirs = ["app", "app/services", "app/models", "app/utils", "tests"]
for d in dirs:
    os.makedirs(d, exist_ok=True)
print("Directories created")
