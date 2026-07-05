import os
import shutil
import subprocess
import sys

def run_command(command, cwd=None):
    print(f"Executing: {command} in {cwd or os.getcwd()}")
    result = subprocess.run(command, shell=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error: Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(root_dir, "frontend")
    dist_source = os.path.join(frontend_dir, "dist")
    dist_target = os.path.join(root_dir, "backend", "app", "dist")

    # 1. Build frontend
    print("--- 1. Building Vite React Frontend ---")
    run_command("npm run build", cwd=frontend_dir)

    # 2. Clean old target dist folder
    print("--- 2. Cleaning old package dist assets ---")
    if os.path.exists(dist_target):
        shutil.rmtree(dist_target)

    # 3. Copy dist folder to backend/app/dist
    print("--- 3. Copying compiled assets to backend/app/dist ---")
    shutil.copytree(dist_source, dist_target)

    # 4. Build python package
    print("--- 4. Building Python Wheel & Source Dist ---")
    run_command("python -m pip install --upgrade setuptools wheel build")
    run_command("python -m build", cwd=root_dir)

    print("\nPackage build completed successfully!")
    print("Check the 'dist/' directory in the workspace root for the generated package files.")

if __name__ == "__main__":
    main()
