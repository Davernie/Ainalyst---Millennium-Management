import os
import shutil

# 🧠 PostgreSQL → MySQL replacements
REPLACEMENTS = [
    ("SERIAL", "INT AUTO_INCREMENT"),
    ("BOOLEAN", "TINYINT(1)"),
    ("::", ""),  # Remove PostgreSQL casting
    ("RETURNING id", "-- RETURNING removed (MySQL unsupported)"),
    ("CREATE EXTENSION IF NOT EXISTS", "-- PostgreSQL EXTENSION removed"),
    ("jsonb", "JSON"),
]

# 🔁 Replace PostgreSQL syntax with MySQL-compatible code
def convert_sql(content):
    for old, new in REPLACEMENTS:
        content = content.replace(old, new)
    return content

# 📁 Recursively find .sql files and convert
def convert_all_sql_files(root_folder):
    backup_folder = os.path.join(root_folder, "backup_sql")
    os.makedirs(backup_folder, exist_ok=True)

    for root, _, files in os.walk(root_folder):
        for file in files:
            if file.endswith(".sql"):
                original_path = os.path.join(root, file)

                # 🆗 Backup original
                relative_path = os.path.relpath(original_path, root_folder)
                backup_path = os.path.join(backup_folder, relative_path)
                os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                shutil.copy2(original_path, backup_path)
                print(f"📄 Backed up: {original_path} → {backup_path}")

                # 🛠 Convert and overwrite original
                with open(original_path, "r", encoding="utf-8") as f:
                    original = f.read()
                converted = convert_sql(original)
                with open(original_path, "w", encoding="utf-8") as f:
                    f.write(converted)
                print(f"✅ Converted: {original_path}")

if __name__ == "__main__":
    convert_all_sql_files(".")
