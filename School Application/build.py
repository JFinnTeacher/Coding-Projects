import os
import shutil
import subprocess
import sys

def create_executable():
    # Create build and dist directories if they don't exist
    os.makedirs('build', exist_ok=True)
    os.makedirs('dist', exist_ok=True)
    
    # Clean up previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # List of all Python files
    python_files = [f for f in os.listdir('.') if f.endswith('.py') and f != 'build.py']
    
    # Create the PyInstaller command
    cmd = [
        'pyinstaller',
        '--name=SchoolApp',
        '--windowed',
        '--icon=icon.ico',
        '--clean',
        '--add-data', 'timer_tick.wav;.',
        '--add-data', 'timer_end.wav;.',
    ]
    
    # Add all Python files as data
    for py_file in python_files:
        if py_file != 'main.py':
            cmd.extend(['--add-data', f'{py_file};.'])
    
    # Add hidden imports
    cmd.extend(['--hidden-import', 'pandas'])
    cmd.extend(['--hidden-import', 'pygame'])
    
    # Add the main script
    cmd.append('main.py')
    
    # Run PyInstaller
    subprocess.run(cmd, check=True)
    
    print("\nBuild completed! The executable can be found in the 'dist' folder.")

if __name__ == '__main__':
    create_executable() 