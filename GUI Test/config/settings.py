"""
Configuration settings for the Classroom Assistant application.
"""

# Window settings
WINDOW = {
    'main': {
        'title': "Classroom Assistant",
        'width': 400,
        'height': 500,
        'padding': 20,
    },
    'module': {
        'default_width': 400,
        'default_height': 300,
        'padding': 20,
        'random_student': {
            'width': 400,
            'height': 500
        },
        'tournament_generator': {
            'width': 600,
            'height': 700
        },
        'timer': {
            'width': 400,
            'height': 300
        },
        'module4': {
            'width': 400,
            'height': 300
        },
        'module5': {
            'width': 400,
            'height': 300
        },
        'module6': {
            'width': 400,
            'height': 300
        }
    }
}

# Color scheme
COLORS = {
    'primary': '#ADD8E6',    # Light blue background
    'secondary': '#F0F8FF',  # Alice blue for frames
    'text': '#2C3E50',      # Dark blue-gray for text
    'button': '#E8F4F8',    # Very light blue for buttons
    'button_hover': '#CCE5FF',  # Slightly darker blue for button hover
    'highlight': '#4A90E2',  # Bright blue for highlights
    'exit_bg': '#FFE4E1',   # Misty rose for exit button
    'exit_hover': '#FFD0CC'  # Lighter red for exit hover
}

# Font settings
FONTS = {
    'title': ('Helvetica', 16, 'bold'),
    'large': ('Helvetica', 24, 'normal'),
    'clock': ('Helvetica', 24, 'normal'),
    'date': ('Helvetica', 12, 'normal'),
    'button': ('Helvetica', 10, 'normal'),
    'text': ('Helvetica', 10, 'normal'),
    'code': ('Courier', 10, 'normal')
}

# Time format settings
TIME_FORMATS = {
    'clock': "%H:%M:%S",
    'date': "%B %d, %Y",
    'short_time': "%H:%M",
    'short_date': "%Y-%m-%d"
}

# Button settings
BUTTONS = {
    'width': 20,
    'padding': 10,
    'spacing': {
        'padx': 10,
        'pady': 5,
        'sticky': "ew"
    }
}

# Grid settings
GRID = {
    'padding': {
        'padx': 10,
        'pady': 10
    },
    'button_columns': 2
}

# Module names and titles
MODULES = {
    'random_student': {
        'title': "Random Student Selector",
    },
    'tournament_generator': {
        'title': "Tournament Generator",
    },
    'timer': {
        'title': "Timer",
    },
    'module4': {
        'title': "Module 4",
    },
    'module5': {
        'title': "Module 5",
    },
    'module6': {
        'title': "Module 6",
    }
}

# Sound settings
SOUNDS = {
    'timer_complete': {
        'frequency': 1000,  # Hz
        'duration': 1000    # milliseconds
    }
} 