import PyInstaller.__main__
import os
import site
import sys
import pkg_resources

# Get the current directory and site-packages
current_dir = os.path.dirname(os.path.abspath(__file__))
venv_site_packages = os.path.join(current_dir, 'venv', 'Lib', 'site-packages')

# Get all installed packages
installed_packages = [f"{dist.key}=={dist.version}" for dist in pkg_resources.working_set]

# Build command
cmd = [
    'markitdown_gui.py',
    '--name=MarkItDown_Converter',
    '--onefile',
    '--windowed',
    f'--add-data={os.path.join(venv_site_packages, "customtkinter")};customtkinter',
    f'--add-data={os.path.join(venv_site_packages, "magika", "models")};magika/models',
    '--hidden-import=magika',
    '--hidden-import=markitdown',
    '--hidden-import=PIL',
    '--hidden-import=customtkinter',
    '--hidden-import=tkinter',
    '--hidden-import=darkdetect',
    '--hidden-import=packaging',
    '--hidden-import=charset_normalizer',
    '--hidden-import=defusedxml',
    '--hidden-import=markdownify',
    '--hidden-import=requests',
    '--hidden-import=azure.ai.documentintelligence',
    '--hidden-import=azure.identity',
    '--hidden-import=lxml',
    '--collect-all=markitdown',
    '--collect-all=magika',
    '--collect-all=customtkinter',
    '--collect-all=PIL',
    '--clean',
    '--noconfirm'
]

# Add all installed packages as hidden imports
for package in installed_packages:
    cmd.append(f'--hidden-import={package.split("==")[0]}')

PyInstaller.__main__.run(cmd) 