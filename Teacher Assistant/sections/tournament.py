import tkinter as tk
from tkinter import ttk, messagebox
import random
import math

class TournamentWindow:
    def __init__(self, parent, config):
        self.window = tk.Toplevel(parent)
        self.window.title("Tournament Tracker")
        self.window.geometry("800x600")
        self.window.configure(bg=config["theme"]["background"])
        
        self.config = config
        self.teams = []
        self.matches = []
        self.current_round = 1
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.window, bg=self.config["theme"]["background"])
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left side - Team Management
        left_frame = tk.Frame(main_frame, bg=self.config["theme"]["background"])
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # Team List
        team_list_frame = tk.LabelFrame(
            left_frame,
            text="Teams",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        )
        team_list_frame.pack(fill='both', expand=True, pady=5)
        
        self.team_listbox = tk.Listbox(
            team_list_frame,
            selectmode='extended',
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            selectbackground=self.config["theme"]["button_active_bg"],
            selectforeground=self.config["theme"]["button_active_fg"]
        )
        self.team_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Team Controls
        team_controls = tk.Frame(left_frame, bg=self.config["theme"]["background"])
        team_controls.pack(fill='x', pady=5)
        
        tk.Button(
            team_controls,
            text="Add Team",
            command=self.add_team,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='left', padx=5)
        
        tk.Button(
            team_controls,
            text="Generate Teams",
            command=self.generate_teams,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='left', padx=5)
        
        tk.Button(
            team_controls,
            text="Remove Team",
            command=self.remove_team,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='left', padx=5)
        
        # Right side - Tournament Management
        right_frame = tk.Frame(main_frame, bg=self.config["theme"]["background"])
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        # Tournament Controls
        tournament_controls = tk.LabelFrame(
            right_frame,
            text="Tournament Controls",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        )
        tournament_controls.pack(fill='x', pady=5)
        
        tk.Button(
            tournament_controls,
            text="Start Tournament",
            command=self.start_tournament,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(fill='x', padx=5, pady=5)
        
        tk.Button(
            tournament_controls,
            text="Next Round",
            command=self.next_round,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(fill='x', padx=5, pady=5)
        
        # Tournament Display
        self.tournament_frame = tk.LabelFrame(
            right_frame,
            text="Tournament Bracket",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        )
        self.tournament_frame.pack(fill='both', expand=True, pady=5)
        
        # Match Display
        match_frame = tk.LabelFrame(
            right_frame,
            text="Current Matches",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        )
        match_frame.pack(fill='both', expand=True, pady=5)
        
        self.match_text = tk.Text(
            match_frame,
            height=10,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            insertbackground=self.config["theme"]["button_fg"]
        )
        self.match_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Results Entry
        results_frame = tk.LabelFrame(
            right_frame,
            text="Enter Results",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        )
        results_frame.pack(fill='x', pady=5)
        
        tk.Label(
            results_frame,
            text="Match Number:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(side='left', padx=5)
        
        self.match_number = tk.Entry(
            results_frame,
            width=5,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            insertbackground=self.config["theme"]["button_fg"]
        )
        self.match_number.pack(side='left', padx=5)
        
        tk.Label(
            results_frame,
            text="Winner:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(side='left', padx=5)
        
        self.winner_entry = tk.Entry(
            results_frame,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            insertbackground=self.config["theme"]["button_fg"]
        )
        self.winner_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        tk.Button(
            results_frame,
            text="Submit Result",
            command=self.submit_result,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(side='right', padx=5)
        
        # Status Bar
        self.status_label = tk.Label(
            main_frame,
            text="",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        )
        self.status_label.pack(fill='x', pady=5)

    def update_team_list(self):
        self.team_listbox.delete(0, tk.END)
        for team in self.teams:
            self.team_listbox.insert(tk.END, team)

    def add_team(self):
        dialog = tk.Toplevel(self.window)
        dialog.title("Add Team")
        dialog.geometry("300x100")
        dialog.configure(bg=self.config["theme"]["background"])
        
        tk.Label(
            dialog,
            text="Enter team name:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(pady=5)
        
        team_entry = tk.Entry(
            dialog,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            insertbackground=self.config["theme"]["button_fg"]
        )
        team_entry.pack(pady=5)
        
        def add():
            team_name = team_entry.get().strip()
            if team_name:
                self.teams.append(team_name)
                self.update_team_list()
                dialog.destroy()
        
        tk.Button(
            dialog,
            text="Add",
            command=add,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(pady=5)
    
    def remove_team(self):
        selected = self.team_listbox.curselection()
        if selected:
            team_name = self.team_listbox.get(selected[0])
            self.teams.remove(team_name)
            self.update_team_list()
    
    def start_tournament(self):
        try:
            num_teams = len(self.teams)
            if num_teams < self.config["tournament"]["min_teams"]:
                raise ValueError(f"Number of teams must be at least {self.config['tournament']['min_teams']}")
            if num_teams > self.config["tournament"]["max_teams"]:
                raise ValueError(f"Number of teams must be at most {self.config['tournament']['max_teams']}")
            
            # Shuffle teams for random matchups
            random.shuffle(self.teams)
            
            # Initialize matches
            self.matches = []
            self.current_round = 1
            
            # Create first round matches
            for i in range(0, len(self.teams), 2):
                if i + 1 < len(self.teams):
                    self.matches.append({
                        'round': 1,
                        'team1': self.teams[i],
                        'team2': self.teams[i + 1],
                        'winner': None
                    })
            
            self.update_display()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def update_display(self):
        # Clear previous display
        for widget in self.tournament_frame.winfo_children():
            widget.destroy()
        
        # Calculate number of rounds
        num_rounds = math.ceil(math.log2(len(self.teams)))
        
        # Create a frame for all rounds
        rounds_frame = tk.Frame(
            self.tournament_frame,
            bg=self.config["theme"]["background"]
        )
        rounds_frame.pack(fill='both', expand=True)
        
        # Create round frames
        for round_num in range(1, num_rounds + 1):
            round_frame = tk.LabelFrame(
                rounds_frame,
                text=f"Round {round_num}",
                bg=self.config["theme"]["background"],
                fg=self.config["theme"]["foreground"]
            )
            round_frame.pack(side='left', fill='both', expand=True, padx=5)
            
            # Get matches for this round
            round_matches = [m for m in self.matches if m['round'] == round_num]
            
            for match in round_matches:
                match_frame = tk.Frame(
                    round_frame,
                    bg=self.config["theme"]["background"],
                    relief='solid',
                    borderwidth=1
                )
                match_frame.pack(fill='x', pady=5, padx=5)
                
                # Team 1
                tk.Label(
                    match_frame,
                    text=match['team1'],
                    bg=self.config["theme"]["background"],
                    fg=self.config["theme"]["foreground"],
                    font=('Helvetica', 10, 'bold')
                ).pack(fill='x', padx=5, pady=2)
                
                # VS separator
                tk.Label(
                    match_frame,
                    text="vs",
                    bg=self.config["theme"]["background"],
                    fg=self.config["theme"]["foreground"]
                ).pack(fill='x', padx=5)
                
                # Team 2
                tk.Label(
                    match_frame,
                    text=match['team2'],
                    bg=self.config["theme"]["background"],
                    fg=self.config["theme"]["foreground"],
                    font=('Helvetica', 10, 'bold')
                ).pack(fill='x', padx=5, pady=2)
                
                # Winner section
                if not match['winner'] and round_num == self.current_round:
                    tk.Button(
                        match_frame,
                        text="Select Winner",
                        command=lambda m=match: self.select_winner(m),
                        bg=self.config["theme"]["button_bg"],
                        fg=self.config["theme"]["button_fg"],
                        activebackground=self.config["theme"]["button_active_bg"],
                        activeforeground=self.config["theme"]["button_active_fg"],
                        font=('Helvetica', 9),
                        relief='raised',
                        padx=5,
                        pady=2
                    ).pack(fill='x', padx=5, pady=2)
                elif match['winner']:
                    winner_frame = tk.Frame(
                        match_frame,
                        bg=self.config["theme"]["background"]
                    )
                    winner_frame.pack(fill='x', padx=5, pady=2)
                    
                    tk.Label(
                        winner_frame,
                        text="Winner:",
                        bg=self.config["theme"]["background"],
                        fg=self.config["theme"]["foreground"]
                    ).pack(side='left')
                    
                    tk.Label(
                        winner_frame,
                        text=match['winner'],
                        bg=self.config["theme"]["background"],
                        fg="#00FF00",  # Green color for winner
                        font=('Helvetica', 10, 'bold')
                    ).pack(side='left', padx=5)
        
        # Update status
        if self.current_round > num_rounds:
            final_match = [m for m in self.matches if m['round'] == num_rounds][0]
            self.status_label.config(text=f"Tournament Complete! Winner: {final_match['winner']}")
        else:
            self.status_label.config(text=f"Current Round: {self.current_round}")
            
        # Update match text display
        self.update_match_display()
    
    def update_match_display(self):
        self.match_text.delete('1.0', tk.END)
        current_matches = [m for m in self.matches if m['round'] == self.current_round]
        
        for i, match in enumerate(current_matches, 1):
            self.match_text.insert(tk.END, f"Match {i}:\n")
            self.match_text.insert(tk.END, f"{match['team1']} vs {match['team2']}\n")
            if match['winner']:
                self.match_text.insert(tk.END, f"Winner: {match['winner']}\n")
            self.match_text.insert(tk.END, "\n")
    
    def select_winner(self, match):
        dialog = tk.Toplevel(self.window)
        dialog.title("Select Winner")
        dialog.geometry("300x150")
        dialog.configure(bg=self.config["theme"]["background"])
        
        tk.Label(
            dialog,
            text="Select the winner:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(pady=10)
        
        def set_winner(winner):
            match['winner'] = winner
            dialog.destroy()
            
            # Check if round is complete
            round_matches = [m for m in self.matches if m['round'] == self.current_round]
            if all(m['winner'] for m in round_matches):
                self.current_round += 1
                self.create_next_round()
            
            self.update_display()
        
        tk.Button(
            dialog,
            text=match['team1'],
            command=lambda: set_winner(match['team1']),
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(fill='x', padx=20, pady=5)
        
        tk.Button(
            dialog,
            text=match['team2'],
            command=lambda: set_winner(match['team2']),
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(fill='x', padx=20, pady=5)
    
    def create_next_round(self):
        # Get winners from current round
        current_winners = [
            m['winner'] for m in self.matches
            if m['round'] == self.current_round - 1 and m['winner'] is not None
        ]
        
        # Create matches for next round
        for i in range(0, len(current_winners), 2):
            if i + 1 < len(current_winners):
                self.matches.append({
                    'round': self.current_round,
                    'team1': current_winners[i],
                    'team2': current_winners[i + 1],
                    'winner': None
                })
            else:
                # If odd number of winners, the last team automatically advances
                self.matches.append({
                    'round': self.current_round,
                    'team1': current_winners[i],
                    'team2': "BYE",
                    'winner': current_winners[i]
                })
    
    def next_round(self):
        round_matches = [m for m in self.matches if m['round'] == self.current_round]
        if not round_matches:
            messagebox.showwarning("Warning", "No matches in current round")
            return
        
        if not all(m['winner'] for m in round_matches):
            messagebox.showwarning("Warning", "Please complete all matches in the current round first")
            return
        
        # Check if tournament is complete
        num_rounds = math.ceil(math.log2(len(self.teams)))
        if self.current_round >= num_rounds:
            messagebox.showinfo("Tournament Complete", f"Winner: {round_matches[0]['winner']}")
            return
        
        self.current_round += 1
        self.create_next_round()
        self.update_display()
    
    def submit_result(self):
        try:
            match_num = int(self.match_number.get()) - 1
            winner = self.winner_entry.get().strip()
            
            current_matches = [m for m in self.matches if m['round'] == self.current_round]
            if not (0 <= match_num < len(current_matches)):
                raise ValueError("Invalid match number")
            
            match = current_matches[match_num]
            if winner not in [match['team1'], match['team2']]:
                raise ValueError("Winner must be one of the teams in the match")
            
            match['winner'] = winner
            self.match_number.delete(0, tk.END)
            self.winner_entry.delete(0, tk.END)
            
            # Check if round is complete
            if all(m['winner'] for m in current_matches):
                self.current_round += 1
                self.create_next_round()
            
            self.update_display()
            
        except (ValueError, IndexError) as e:
            messagebox.showerror("Error", str(e))

    def generate_teams(self):
        dialog = tk.Toplevel(self.window)
        dialog.title("Generate Teams")
        dialog.geometry("300x150")
        dialog.configure(bg=self.config["theme"]["background"])
        
        tk.Label(
            dialog,
            text="Enter number of teams:",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(pady=5)
        
        num_teams_entry = tk.Entry(
            dialog,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            insertbackground=self.config["theme"]["button_fg"]
        )
        num_teams_entry.pack(pady=5)
        num_teams_entry.insert(0, str(self.config["tournament"]["default_teams"]))
        
        tk.Label(
            dialog,
            text=f"(Min: {self.config['tournament']['min_teams']}, Max: {self.config['tournament']['max_teams']})",
            bg=self.config["theme"]["background"],
            fg=self.config["theme"]["foreground"]
        ).pack(pady=5)
        
        def generate():
            try:
                num_teams = int(num_teams_entry.get())
                if num_teams < self.config["tournament"]["min_teams"]:
                    raise ValueError(f"Number of teams must be at least {self.config['tournament']['min_teams']}")
                if num_teams > self.config["tournament"]["max_teams"]:
                    raise ValueError(f"Number of teams must be at most {self.config['tournament']['max_teams']}")
                
                # Generate team names
                self.teams = [f"Team {i+1}" for i in range(num_teams)]
                self.update_team_list()
                dialog.destroy()
                
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        tk.Button(
            dialog,
            text="Generate",
            command=generate,
            bg=self.config["theme"]["button_bg"],
            fg=self.config["theme"]["button_fg"],
            activebackground=self.config["theme"]["button_active_bg"],
            activeforeground=self.config["theme"]["button_active_fg"],
            font=('Helvetica', 10),
            relief='raised',
            padx=10,
            pady=5
        ).pack(pady=10) 