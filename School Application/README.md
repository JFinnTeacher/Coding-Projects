# School Application

A Python-based application with various classroom management tools built using Tkinter.

## Features

1. **Countdown Timer**
   - Set custom time duration
   - Visual progress bar
   - Audio alert when timer ends
   - Pause/Resume functionality

2. **Random Name Picker**
   - Add names manually or import from CSV
   - Randomly select names
   - Option to remove selected names
   - Create random groups of specified size

3. **Tournament Tracker**
   - Create tournament brackets
   - Support for any number of teams
   - Automatic handling of byes
   - Visual bracket display
   - Track tournament progress

## Installation

1. Make sure you have Python 3.7+ installed on your system.

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Configuration

The application settings are stored in `config.ini`. You can modify this file to:
- Change the UI theme colors
- Set default timer duration
- Enable/disable sound alerts
- Configure other application settings

## File Structure

- `main.py` - Main application entry point
- `timer_module.py` - Countdown timer functionality
- `name_picker_module.py` - Random name selection and grouping
- `tournament_module.py` - Tournament bracket system
- `config.ini` - Application configuration
- `requirements.txt` - Python dependencies

## Usage Tips

1. **Timer**
   - Enter time in minutes (decimals allowed)
   - Click Start/Pause to control the timer
   - Reset button returns to initial state

2. **Name Picker**
   - CSV files should have names in the first column
   - Groups are created by randomly shuffling names
   - Names can be kept or removed after selection

3. **Tournament**
   - Enter the number of teams
   - Input team names or use default names
   - Click on winning team to advance them
   - Tournament automatically handles brackets

## Requirements

- Python 3.7+
- tkinter (usually comes with Python)
- pygame (for audio)
- pandas (for CSV handling)
- configparser (for settings management) 