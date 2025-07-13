# Teacher Assistant

A Python-based desktop application designed to help teachers with various classroom management tasks.

## Features

1. **Countdown Timer**
   - Visual countdown display
   - Customizable time settings
   - Audio cue when timer ends
   - Pause/Resume functionality

2. **Name Selector**
   - Import names from CSV file
   - Manual name entry
   - Random name selection
   - Option to remove selected names
   - Random group assignment with customizable group sizes

3. **Tournament Tracker**
   - Create tournaments with any number of teams
   - Visual bracket display
   - Easy winner selection
   - Automatic progression through rounds
   - Tournament completion tracking

4. **Configuration**
   - Customizable color scheme
   - Default settings for all features
   - Settings persistence between sessions

## Requirements

- Python 3.8 or higher
- Required packages (install using `pip install -r requirements.txt`):
  - tkinter (usually comes with Python)
  - pillow
  - playsound
  - pandas

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Teacher-Assistant.git
   cd Teacher-Assistant
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Directory Structure

```
Teacher-Assistant/
├── main.py              # Main application file
├── requirements.txt     # Python package dependencies
├── config/             # Configuration files
│   └── settings.json   # Application settings
├── sections/           # Feature modules
│   ├── config_window.py
│   ├── timer.py
│   ├── name_selector.py
│   └── tournament.py
└── sounds/            # Sound files for timer
    └── timer_end.wav
```

## Usage

1. **Countdown Timer**
   - Set time using minutes and seconds
   - Start/Pause/Reset functionality
   - Audio cue plays when timer ends

2. **Name Selector**
   - Import names from CSV file (first column should contain names)
   - Add names manually
   - Select random names
   - Create random groups with specified size

3. **Tournament Tracker**
   - Enter number of teams
   - View tournament bracket
   - Select winners for each match
   - Track tournament progress

4. **Configuration**
   - Customize application theme
   - Set default values for features
   - Save settings for future use

## Contributing

Feel free to submit issues and enhancement requests!
