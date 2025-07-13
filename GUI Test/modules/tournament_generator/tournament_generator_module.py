import tkinter as tk
from tkinter import ttk, messagebox
import random
from ..common_styles import apply_module_style
from config.settings import COLORS, WINDOW, GRID, MODULES, FONTS

class TournamentGenerator:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title(MODULES['tournament_generator']['title'])
        
        # Apply common styles
        apply_module_style(self.window, 'tournament_generator')
        
        # Participants list
        self.participants = []
        
        # Create main frame
        main_frame = ttk.Frame(
            self.window,
            padding=WINDOW['module']['padding'],
            style='Main.TFrame'
        )
        main_frame.grid(sticky="nsew", **GRID['padding'])
        
        # Configure window grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        
        # Participant entry section
        entry_frame = ttk.LabelFrame(main_frame, text="Add Participants", padding="10")
        entry_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        self.participant_entry = ttk.Entry(entry_frame, style='TEntry')
        self.participant_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        add_button = ttk.Button(entry_frame, text="Add", command=self.add_participant)
        add_button.grid(row=0, column=1, padx=5, pady=5)
        
        # Participants list
        list_frame = ttk.LabelFrame(main_frame, text="Participants", padding="10")
        list_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        
        self.participants_listbox = tk.Listbox(
            list_frame,
            height=8,
            bg=COLORS['button'],
            fg=COLORS['text'],
            selectbackground=COLORS['highlight'],
            selectforeground='white'
        )
        self.participants_listbox.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=5)
        
        remove_button = ttk.Button(list_frame, text="Remove Selected", command=self.remove_participant)
        remove_button.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Tournament controls
        controls_frame = ttk.Frame(main_frame, style='Main.TFrame')
        controls_frame.grid(row=2, column=0, pady=(0, 20))
        
        generate_button = ttk.Button(controls_frame, text="Generate Tournament", command=self.generate_tournament)
        generate_button.grid(row=0, column=0, padx=5)
        
        clear_button = ttk.Button(controls_frame, text="Clear All", command=self.clear_all)
        clear_button.grid(row=0, column=1, padx=5)
        
        # Tournament display
        self.tournament_frame = ttk.LabelFrame(main_frame, text="Tournament Bracket", padding="10")
        self.tournament_frame.grid(row=3, column=0, sticky="nsew")
        
        self.bracket_text = tk.Text(
            self.tournament_frame,
            height=15,
            width=50,
            bg=COLORS['button'],
            fg=COLORS['text'],
            font=FONTS['code']
        )
        self.bracket_text.grid(sticky="nsew", pady=5)
        self.bracket_text.config(state='disabled')
        
    def add_participant(self):
        name = self.participant_entry.get().strip()
        if name:
            self.participants.append(name)
            self.participants_listbox.insert(tk.END, name)
            self.participant_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Please enter a participant name")
            
    def remove_participant(self):
        selection = self.participants_listbox.curselection()
        if selection:
            index = selection[0]
            self.participants_listbox.delete(index)
            self.participants.pop(index)
        else:
            messagebox.showwarning("Warning", "Please select a participant to remove")
            
    def clear_all(self):
        self.participants = []
        self.participants_listbox.delete(0, tk.END)
        self.bracket_text.config(state='normal')
        self.bracket_text.delete(1.0, tk.END)
        self.bracket_text.config(state='disabled')
        
    def generate_tournament(self):
        if len(self.participants) < 2:
            messagebox.showwarning("Warning", "Need at least 2 participants")
            return
            
        # Shuffle participants
        tournament_participants = self.participants.copy()
        random.shuffle(tournament_participants)
        
        # Generate bracket display
        self.bracket_text.config(state='normal')
        self.bracket_text.delete(1.0, tk.END)
        
        # Create rounds
        round_num = 1
        current_round = tournament_participants
        while len(current_round) > 1:
            self.bracket_text.insert(tk.END, f"\nRound {round_num}:\n")
            next_round = []
            
            # Create matches
            for i in range(0, len(current_round), 2):
                if i + 1 < len(current_round):
                    self.bracket_text.insert(tk.END, f"{current_round[i]} vs {current_round[i+1]}\n")
                    next_round.append(f"Winner of ({current_round[i]} vs {current_round[i+1]})")
                else:
                    self.bracket_text.insert(tk.END, f"{current_round[i]} (Bye)\n")
                    next_round.append(current_round[i])
            
            current_round = next_round
            round_num += 1
        
        self.bracket_text.config(state='disabled')

def open_window(parent):
    TournamentGenerator(parent) 