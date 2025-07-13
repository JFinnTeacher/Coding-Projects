import tkinter as tk
from tkinter import messagebox
import math
from utils import ModernWindow, ModernFrame, RoundedButton, ModernEntry
from tournament_display import TournamentDisplay

class TournamentWindow(ModernWindow):
    def __init__(self, parent):
        super().__init__(parent, "Tournament Tracker", "800x600")
        self.parent = parent  # Store reference to parent window
        
        self.teams = []
        self.matches = []
        self.current_round = 0
        self.display_window = None
        self.create_widgets()
        
    def create_widgets(self):
        # Team count frame
        count_frame = ModernFrame(self.content)
        count_frame.pack(pady=20, fill='x', padx=20)
        
        tk.Label(
            count_frame,
            text="Number of Teams:",
            font=("Helvetica", 12),
            bg=self.theme['bg_color'],
            fg=self.theme['text_color']
        ).pack(side=tk.LEFT, padx=5)
        
        self.team_count = tk.StringVar(value="4")
        team_count_entry = ModernEntry(count_frame, textvariable=self.team_count, width=5)
        team_count_entry.pack(side=tk.LEFT, padx=5)
        
        RoundedButton(
            count_frame,
            text="Auto Generate",
            command=self.auto_generate_teams,
            width=120,
            height=30
        ).pack(side=tk.LEFT, padx=5)
        
        # Team entry frame
        entry_frame = ModernFrame(self.content)
        entry_frame.pack(pady=20, fill='x', padx=20)
        
        tk.Label(
            entry_frame,
            text="Team Name:",
            font=("Helvetica", 12),
            bg=self.theme['bg_color'],
            fg=self.theme['text_color']
        ).pack(side=tk.LEFT, padx=5)
        
        self.team_entry = ModernEntry(entry_frame)
        self.team_entry.pack(side=tk.LEFT, expand=True, fill='x', padx=5)
        
        RoundedButton(
            entry_frame,
            text="Add Team",
            command=self.add_team,
            width=100,
            height=30
        ).pack(side=tk.LEFT, padx=5)
        
        # Teams list frame
        list_frame = ModernFrame(self.content)
        list_frame.pack(pady=20, expand=True, fill='both', padx=20)
        
        tk.Label(
            list_frame,
            text="Teams",
            font=("Helvetica", 14, "bold"),
            bg=self.theme['bg_color'],
            fg=self.theme['text_color']
        ).pack(pady=(0, 10))
        
        # Create listbox with scrollbar
        listbox_frame = ModernFrame(list_frame)
        listbox_frame.pack(fill='both', expand=True)
        
        self.teams_listbox = tk.Listbox(
            listbox_frame,
            font=("Helvetica", 12),
            bg=self.theme['input_bg'],
            fg=self.theme['text_color'],
            selectmode=tk.SINGLE,
            relief='flat',
            highlightthickness=0
        )
        self.teams_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
        # Connect scrollbar to listbox
        self.teams_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.teams_listbox.yview)
        
        # Tournament controls frame
        controls_frame = ModernFrame(self.content)
        controls_frame.pack(pady=20, padx=20)
        
        self.start_button = RoundedButton(
            controls_frame,
            text="Start Tournament",
            command=self.start_tournament,
            width=150,
            height=40
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        RoundedButton(
            controls_frame,
            text="Clear Teams",
            command=self.clear_teams,
            width=120,
            height=40
        ).pack(side=tk.LEFT, padx=5)
        
        RoundedButton(
            controls_frame,
            text="Back",
            command=self.close_window,
            width=120,
            height=40
        ).pack(side=tk.LEFT, padx=5)
        
        # Tournament bracket frame
        self.bracket_frame = ModernFrame(self.content)
        self.bracket_frame.pack(pady=20, expand=True, fill='both', padx=20)
        
        # Create a canvas with scrollbar for the bracket
        self.canvas = tk.Canvas(
            self.bracket_frame,
            bg=self.theme['bg_color'],
            highlightthickness=0
        )
        scrollbar = tk.Scrollbar(self.bracket_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a frame inside the canvas for the bracket content
        self.bracket_content = ModernFrame(self.canvas)
        self.canvas.create_window((0, 0), window=self.bracket_content, anchor="nw")
        
        # Configure the canvas scroll region when the bracket content changes size
        self.bracket_content.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        ))
    
    def auto_generate_teams(self):
        try:
            num_teams = int(self.team_count.get())
            if num_teams < 2:
                messagebox.showwarning("Warning", "Need at least 2 teams")
                return
            if num_teams > 32:
                messagebox.showwarning("Warning", "Maximum 32 teams allowed")
                return
            
            # Clear existing teams
            self.clear_teams()
            
            # Generate team names
            for i in range(1, num_teams + 1):
                team_name = f"Team {i}"
                self.teams.append(team_name)
                self.teams_listbox.insert(tk.END, team_name)
            
            messagebox.showinfo("Success", f"Generated {num_teams} teams")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
    
    def add_team(self):
        team_name = self.team_entry.get().strip()
        if team_name:
            if team_name not in self.teams:
                self.teams.append(team_name)
                self.teams_listbox.insert(tk.END, team_name)
                self.team_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Warning", "Team already exists")
        else:
            messagebox.showwarning("Warning", "Please enter a team name")
    
    def clear_teams(self):
        self.teams = []
        self.teams_listbox.delete(0, tk.END)
        self.clear_bracket()
    
    def clear_bracket(self):
        for widget in self.bracket_content.winfo_children():
            widget.destroy()
        self.matches = []
        self.current_round = 0
    
    def start_tournament(self):
        if len(self.teams) < 2:
            messagebox.showwarning("Warning", "Need at least 2 teams to start")
            return
        
        # Calculate number of rounds needed
        self.num_rounds = math.ceil(math.log2(len(self.teams)))
        num_teams = 2 ** self.num_rounds
        
        # Create a copy of teams list to avoid modifying the original
        tournament_teams = self.teams.copy()
        
        # Add byes if needed
        while len(tournament_teams) < num_teams:
            tournament_teams.append("BYE")
        
        # Create first round matches
        self.matches = []
        for i in range(0, len(tournament_teams), 2):
            match = {
                'team1': tournament_teams[i],
                'team2': tournament_teams[i + 1],
                'winner': None,
                'round': 0
            }
            # Automatically advance if there's a BYE
            if match['team2'] == "BYE":
                match['winner'] = match['team1']
            elif match['team1'] == "BYE":
                match['winner'] = match['team2']
            self.matches.append(match)
        
        self.current_round = 0
        
        # Open display window
        if self.display_window:
            self.display_window.destroy()
        self.display_window = TournamentDisplay(self, self.matches, self.num_rounds, self.on_display_close)
        self.withdraw()  # Hide the main tournament window
        
        # Check if any first round matches were automatically decided (BYEs)
        self.check_round_completion()
    
    def check_round_completion(self):
        current_matches = [m for m in self.matches if m['round'] == self.current_round]
        if all(m['winner'] for m in current_matches):
            # Create next round matches
            winners = [m['winner'] for m in current_matches]
            next_round = self.current_round + 1
            
            # Only create next round if we haven't reached the final
            if next_round < self.num_rounds:
                for i in range(0, len(winners), 2):
                    if i + 1 < len(winners):
                        self.matches.append({
                            'team1': winners[i],
                            'team2': winners[i + 1],
                            'winner': None,
                            'round': next_round
                        })
                
                self.current_round = next_round
            
            # Update the display
            if self.display_window:
                self.display_window.draw_bracket()
    
    def advance_team(self, match, winner):
        # Set the winner for this match
        match['winner'] = winner
        
        # Check if the round is complete and create next round if needed
        self.check_round_completion()
        
        # Update the display
        if self.display_window:
            self.display_window.draw_bracket()
    
    def on_display_close(self):
        self.deiconify()  # Show the main tournament window
        self.display_window = None
    
    def close_window(self):
        if self.display_window:
            self.display_window.destroy()
        self.destroy()
        self.parent.lift()  # Bring main window to front
        self.parent.focus_force()  # Give focus to main window 