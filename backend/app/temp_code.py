import os

REPLACEMENTS = [
    ("SERIAL", "INT AUTO_INCREMENT"),
    ("BOOLEAN", "TINYINT(1)"),
    ("::", ""),  # Remove PostgreSQL casting
    ("RETURNING id", "-- RETURNING removed (MySQL unsupported)"),
    ("CREATE EXTENSION IF NOT EXISTS", "-- PostgreSQL EXTENSION removed"),
    ("jsonb", "JSON"),
]

def convert_sql(content):
    for old, new in REPLACEMENTS:
        content = content.replace(old, new)
    return content

def convert_all_sql_files(folder):
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".sql"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    original = f.read()
                converted = convert_sql(original)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(converted)
                print(f"✅ Converted: {path}")

if __name__ == "__main__":
    convert_all_sql_files(".")
