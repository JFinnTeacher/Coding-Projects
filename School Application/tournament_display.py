import tkinter as tk
from utils import ModernWindow, ModernFrame, RoundedButton
import random

class TournamentDisplay(ModernWindow):
    def __init__(self, parent, matches, num_rounds, on_close_callback):
        super().__init__(parent, "Tournament Bracket", "1200x800")
        
        # Randomize initial team positions
        self.randomize_initial_matches(matches)
        
        self.matches = matches
        self.num_rounds = num_rounds
        self.on_close_callback = on_close_callback
        self.parent = parent
        
        # Constants for layout
        self.match_width = 200
        self.match_height = 80
        self.round_spacing = 250
        self.match_spacing = 120
        
        # Team colors for visual interest
        self.team_colors = {}
        self.generate_team_colors()
        
        self.create_widgets()
        self.draw_bracket()
    
    def randomize_initial_matches(self, matches):
        # Get all first round matches
        first_round_matches = [m for m in matches if m['round'] == 0]
        # Get all teams from first round
        teams = []
        for match in first_round_matches:
            if match['team1'] != "BYE":
                teams.append(match['team1'])
            if match['team2'] != "BYE":
                teams.append(match['team2'])
        
        # Shuffle teams
        random.shuffle(teams)
        
        # Redistribute teams to matches
        team_idx = 0
        for match in first_round_matches:
            if team_idx < len(teams):
                match['team1'] = teams[team_idx]
                team_idx += 1
            else:
                match['team1'] = "BYE"
            
            if team_idx < len(teams):
                match['team2'] = teams[team_idx]
                team_idx += 1
            else:
                match['team2'] = "BYE"
    
    def generate_team_colors(self):
        # Generate unique colors for each team
        for match in self.matches:
            if match['team1'] not in self.team_colors and match['team1'] != "BYE":
                hue = random.random()  # Random hue
                self.team_colors[match['team1']] = self.hsv_to_hex(hue, 0.3, 0.95)  # Light version for background
            if match['team2'] not in self.team_colors and match['team2'] != "BYE":
                hue = random.random()  # Random hue
                self.team_colors[match['team2']] = self.hsv_to_hex(hue, 0.3, 0.95)  # Light version for background
    
    def hsv_to_hex(self, h, s, v):
        # Convert HSV to RGB then to hex
        i = int(h * 6)
        f = h * 6 - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        
        i = i % 6
        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q
        
        return f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
    
    def create_widgets(self):
        # Create main frame
        self.main_frame = ModernFrame(self.content)
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Add title
        title_frame = ModernFrame(self.main_frame)
        title_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            title_frame,
            text="Tournament Bracket",
            font=("Helvetica", 24, "bold"),
            bg=self.theme['bg_color'],
            fg=self.theme['accent_color']
        ).pack(pady=10)
        
        # Create canvas frame
        canvas_frame = ModernFrame(self.main_frame)
        canvas_frame.pack(expand=True, fill='both')
        
        # Create canvas with scrollbars
        self.canvas = tk.Canvas(
            canvas_frame,
            bg=self.theme['bg_color'],
            highlightthickness=0
        )
        v_scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        h_scrollbar = tk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        
        # Configure scrolling
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and canvas
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        # Create close button
        self.close_button = RoundedButton(
            self.content,
            text="Close",
            command=self.close_window,
            width=120,
            height=40
        )
        self.close_button.pack(pady=10)
    
    def draw_bracket(self):
        self.canvas.delete('all')  # Clear canvas
        
        # Calculate total width and height
        total_width = (self.num_rounds * self.round_spacing) + 100
        max_matches_in_round = 2 ** (self.num_rounds - 1)
        total_height = (max_matches_in_round * self.match_spacing) + 100
        
        # Configure canvas scrolling
        self.canvas.configure(scrollregion=(0, 0, total_width, total_height))
        
        # Draw round labels
        for round_num in range(self.num_rounds):
            x = round_num * self.round_spacing + self.match_width/2 + 50
            self.canvas.create_text(
                x, 30,
                text=f"Round {round_num + 1}",
                font=("Helvetica", 14, "bold"),
                fill=self.theme['accent_color']
            )
        
        # Draw matches for each round
        for round_num in range(self.num_rounds):
            matches_in_round = [m for m in self.matches if m['round'] == round_num]
            matches_count = len(matches_in_round)
            
            # Handle odd number of matches
            if matches_count > 0:
                spacing = total_height / (matches_count + 1)
                
                for i, match in enumerate(matches_in_round):
                    x = round_num * self.round_spacing + 50
                    y = (i + 1) * spacing - self.match_height/2
                    
                    # Draw match box
                    self.draw_match_box(x, y, match)
                    
                    # Draw connection lines to next round if not final round
                    if round_num < self.num_rounds - 1:
                        next_matches = len([m for m in self.matches if m['round'] == round_num + 1])
                        if next_matches > 0:  # Only draw connections if there are matches in the next round
                            next_spacing = total_height / (next_matches + 1)
                            next_y = ((i//2) + 1) * next_spacing - self.match_height/2
                            self.draw_connection(x, y, next_y)
    
    def draw_match_box(self, x, y, match):
        # Draw match container
        self.canvas.create_rectangle(
            x, y,
            x + self.match_width, y + self.match_height,
            fill=self.theme['bg_color'],
            outline=self.theme['accent_color'],
            width=2,
            tags='match'
        )
        
        # Draw separator line
        mid_y = y + self.match_height/2
        self.canvas.create_line(
            x + 10, mid_y,
            x + self.match_width - 10, mid_y,
            fill=self.theme['accent_color']
        )
        
        # Draw team backgrounds
        if match['team1'] != "BYE":
            color1 = self.team_colors.get(match['team1'], self.theme['bg_color'])
            self.canvas.create_rectangle(
                x + 5, y + 5,
                x + self.match_width - 5, mid_y - 2,
                fill=color1 if match['winner'] != match['team1'] else self.theme['accent_color'],
                outline='',
                tags='team_bg'
            )
        
        if match['team2'] != "BYE":
            color2 = self.team_colors.get(match['team2'], self.theme['bg_color'])
            self.canvas.create_rectangle(
                x + 5, mid_y + 2,
                x + self.match_width - 5, y + self.match_height - 5,
                fill=color2 if match['winner'] != match['team2'] else self.theme['accent_color'],
                outline='',
                tags='team_bg'
            )
        
        # Draw team names
        team1_text = match['team1'] if match['team1'] != "BYE" else "BYE"
        team2_text = match['team2'] if match['team2'] != "BYE" else "BYE"
        
        self.canvas.create_text(
            x + 15, y + self.match_height/4,
            text=team1_text,
            anchor='w',
            font=("Helvetica", 12, "bold" if match['winner'] == match['team1'] else "normal"),
            fill=self.theme['bg_color'] if match['winner'] == match['team1'] else self.theme['text_color']
        )
        
        self.canvas.create_text(
            x + 15, y + 3*self.match_height/4,
            text=team2_text,
            anchor='w',
            font=("Helvetica", 12, "bold" if match['winner'] == match['team2'] else "normal"),
            fill=self.theme['bg_color'] if match['winner'] == match['team2'] else self.theme['text_color']
        )
        
        # Add win buttons if no winner and not BYE
        if match['winner'] is None:
            if match['team1'] != "BYE":
                button1 = RoundedButton(
                    self.canvas,
                    text="Win",
                    command=lambda m=match, t=match['team1']: self.advance_team(m, t),
                    width=40,
                    height=20
                )
                self.canvas.create_window(
                    x + self.match_width - 50, y + self.match_height/4,
                    window=button1
                )
            
            if match['team2'] != "BYE":
                button2 = RoundedButton(
                    self.canvas,
                    text="Win",
                    command=lambda m=match, t=match['team2']: self.advance_team(m, t),
                    width=40,
                    height=20
                )
                self.canvas.create_window(
                    x + self.match_width - 50, y + 3*self.match_height/4,
                    window=button2
                )
            
            # Auto-advance if one team is BYE
            if match['team1'] == "BYE" and match['team2'] != "BYE":
                self.advance_team(match, match['team2'])
            elif match['team2'] == "BYE" and match['team1'] != "BYE":
                self.advance_team(match, match['team1'])
    
    def draw_connection(self, x, y, next_y):
        # Draw curved connection line
        start_x = x + self.match_width
        start_y = y + self.match_height/2
        end_x = start_x + self.round_spacing
        end_y = next_y + self.match_height/2
        
        # Calculate control points for curve
        ctrl_x = start_x + (end_x - start_x)/2
        
        # Draw Bezier curve
        self.canvas.create_line(
            start_x, start_y,
            ctrl_x, start_y,
            ctrl_x, end_y,
            end_x, end_y,
            smooth=True,
            fill=self.theme['accent_color'],
            width=2
        )
    
    def advance_team(self, match, winner):
        self.parent.advance_team(match, winner)
        self.draw_bracket()
        
        # Check if tournament is complete
        final_match = next((m for m in self.matches if m['round'] == self.num_rounds - 1), None)
        if final_match and final_match['winner']:
            self.show_winner(final_match['winner'])
    
    def show_winner(self, winner):
        # Create celebration effect
        self.canvas.delete('all')
        
        # Draw trophy
        trophy_text = "🏆"
        self.canvas.create_text(
            self.canvas.winfo_width()/2, self.canvas.winfo_height()/3,
            text=trophy_text,
            font=("Helvetica", 72),
            fill=self.theme['accent_color']
        )
        
        # Draw winner text with animation
        self.canvas.create_text(
            self.canvas.winfo_width()/2, self.canvas.winfo_height()/2,
            text="Tournament Champion",
            font=("Helvetica", 36, "bold"),
            fill=self.theme['accent_color']
        )
        
        winner_color = self.team_colors.get(winner, self.theme['accent_color'])
        self.canvas.create_text(
            self.canvas.winfo_width()/2, self.canvas.winfo_height()/2 + 80,
            text=winner,
            font=("Helvetica", 48, "bold"),
            fill=winner_color
        )
    
    def close_window(self):
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy() 