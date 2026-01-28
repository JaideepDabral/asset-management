"""
Script to fix absolute imports to relative imports in the backend app
"""
import os
import re
from pathlib import Path

# Base directory
base_dir = Path(r"c:\Users\Deepak bisht\OneDrive - CACHE DIGITECH\Desktop\III\ITSM\backend\app")

# Mapping of absolute imports to relative imports based on file location
def get_relative_import(file_path, import_line):
    """Convert absolute import to relative import based on file location"""
    file_path = Path(file_path)
    
    # Determine the depth from app directory
    relative_to_app = file_path.relative_to(base_dir)
    depth = len(relative_to_app.parts) - 1  # -1 because we don't count the file itself
    
    # Patterns to match
    patterns = {
        r'^from database import (.+)$': f'from {"." * (depth + 1)}database.database import \\1',
        r'^from models import (.+)$': f'from {"." * (depth + 1)}models.models import \\1',
        r'^from services import (.+)$': f'from {"." * (depth + 1)}services import \\1',
        r'^from routers import (.+)$': f'from {"." * (depth + 1)}routers import \\1',
        r'^from schemas\.(.+) import (.+)$': f'from {"." * (depth + 1)}schemas.\\1 import \\2',
        r'^from utils import (.+)$': f'from {"." * (depth + 1)}utils import \\1',
    }
    
    for pattern, replacement in patterns.items():
        match = re.match(pattern, import_line.strip())
        if match:
            return re.sub(pattern, replacement, import_line.strip())
    
    return None

def fix_imports_in_file(file_path):
    """Fix imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        modified = False
        new_lines = []
        
        for line in lines:
            new_import = get_relative_import(file_path, line)
            if new_import:
                new_lines.append(new_import + '\n')
                modified = True
                print(f"  {file_path.name}: {line.strip()} -> {new_import}")
            else:
                new_lines.append(line)
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

# Find all Python files
python_files = list(base_dir.rglob("*.py"))
print(f"Found {len(python_files)} Python files")

fixed_count = 0
for py_file in python_files:
    if "__pycache__" in str(py_file):
        continue
    if fix_imports_in_file(py_file):
        fixed_count += 1

print(f"\nFixed imports in {fixed_count} files")
