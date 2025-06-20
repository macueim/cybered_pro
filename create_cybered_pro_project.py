#!/usr/bin/env python3
import os
import sys

def create_file(path):
    """Create empty file and its parent directories if they don't exist."""
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # Create the file if it doesn't exist
    if not os.path.exists(path):
        with open(path, 'w') as f:
            pass  # Create empty file
        print(f"Created file: {path}")
    else:
        print(f"File already exists: {path}")

def create_directory(path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")
    else:
        print(f"Directory already exists: {path}")

def setup_cybered_pro_project():
    """Set up the entire CyberEd Pro project structure."""
    # Project root
    project_root = "cybered_pro"
    create_directory(project_root)

    # Backend structure
    backend_files = [
        "backend/app/api/endpoints/auth.py",
        "backend/app/api/endpoints/users.py",
        "backend/app/api/endpoints/courses.py",
        "backend/app/api/dependencies.py",
        "backend/app/core/config.py",
        "backend/app/core/security.py",
        "backend/app/core/events.py",
        "backend/app/db/base.py",
        "backend/app/db/session.py",
        "backend/app/db/init_db.py",
        "backend/app/models/user.py",
        "backend/app/models/course.py",
        "backend/app/schemas/user.py",
        "backend/app/schemas/course.py",
        "backend/app/services/user.py",
        "backend/app/services/course.py",
        "backend/app/main.py",
        "backend/tests/api/__init__.py",
        "backend/tests/services/__init__.py",
        "backend/tests/conftest.py",
        "backend/alembic/versions/.gitkeep",
        "backend/alembic/env.py",
        "backend/Dockerfile",
        "backend/requirements.txt",
        "backend/alembic.ini",
    ]

    # Frontend structure
    frontend_files = [
        "frontend/public/index.html",
        "frontend/public/favicon.ico",
        "frontend/src/components/.gitkeep",
        "frontend/src/pages/.gitkeep",
        "frontend/src/services/.gitkeep",
        "frontend/src/styles/main.css",
        "frontend/src/main.js",
        "frontend/package.json",
        "frontend/Dockerfile",
    ]

    # Root files
    root_files = [
        "docker-compose.yml",
        "README.md",
    ]

    # Create all files
    for file_path in backend_files + frontend_files + root_files:
        create_file(os.path.join(project_root, file_path))

    # Create any empty directories needed
    empty_dirs = [
        "frontend/public/assets",
        "frontend/public/images",
    ]

    for dir_path in empty_dirs:
        create_directory(os.path.join(project_root, dir_path))

    print("\nProject structure for CyberEd Pro has been created successfully!")
    print(f"Project root: {os.path.abspath(project_root)}")

if __name__ == "__main__":
    setup_cybered_pro_project()