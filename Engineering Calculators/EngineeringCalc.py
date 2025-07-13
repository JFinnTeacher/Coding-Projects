import tkinter as tk
from tkinter import ttk
import math

class EngineeringCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Engineering Calculators")
        self.root.geometry("600x400")
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create calculator selection
        self.calc_var = tk.StringVar()
        self.calc_var.set("Select Calculator")
        
        calculators = [
            "Select Calculator",
            "Ohm's Law Calculator",
            "Resistor Calculator",
            "Potential Dividers Calculator",
            "Series/Parallel Calculator",
            "LED/Resistor Calculator"
        ]
        
        self.calc_menu = ttk.Combobox(self.main_frame, textvariable=self.calc_var, values=calculators)
        self.calc_menu.grid(row=0, column=0, columnspan=2, pady=10)
        self.calc_menu.bind('<<ComboboxSelected>>', self.show_calculator)
        
        # Create frame for calculator inputs
        self.calc_frame = ttk.Frame(self.main_frame)
        self.calc_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Initialize calculator widgets
        self.init_calculator_widgets()
        
    def init_calculator_widgets(self):
        # Clear existing widgets
        for widget in self.calc_frame.winfo_children():
            widget.destroy()
            
        # Create result label
        self.result_label = ttk.Label(self.calc_frame, text="")
        self.result_label.grid(row=10, column=0, columnspan=2, pady=10)
        
    def show_calculator(self, event=None):
        calculator = self.calc_var.get()
        self.init_calculator_widgets()
        
        if calculator == "Ohm's Law Calculator":
            self.setup_ohms_law_calculator()
        elif calculator == "Resistor Calculator":
            self.setup_resistor_calculator()
        elif calculator == "Potential Dividers Calculator":
            self.setup_potential_dividers_calculator()
        elif calculator == "Series/Parallel Calculator":
            self.setup_series_parallel_calculator()
        elif calculator == "LED/Resistor Calculator":
            self.setup_led_resistor_calculator()
            
    def setup_ohms_law_calculator(self):
        # Create input fields
        ttk.Label(self.calc_frame, text="Voltage (V):").grid(row=0, column=0, pady=5)
        self.voltage = ttk.Entry(self.calc_frame)
        self.voltage.grid(row=0, column=1, pady=5)
        
        ttk.Label(self.calc_frame, text="Current (A):").grid(row=1, column=0, pady=5)
        self.current = ttk.Entry(self.calc_frame)
        self.current.grid(row=1, column=1, pady=5)
        
        ttk.Label(self.calc_frame, text="Resistance (Ω):").grid(row=2, column=0, pady=5)
        self.resistance = ttk.Entry(self.calc_frame)
        self.resistance.grid(row=2, column=1, pady=5)
        
        ttk.Button(self.calc_frame, text="Calculate", command=self.calculate_ohms_law).grid(row=3, column=0, columnspan=2, pady=10)
        
    def calculate_ohms_law(self):
        try:
            v = float(self.voltage.get() or 0)
            i = float(self.current.get() or 0)
            r = float(self.resistance.get() or 0)
            
            if v == 0 and i != 0 and r != 0:
                v = i * r
                self.result_label.config(text=f"Voltage = {v:.2f} V")
            elif i == 0 and v != 0 and r != 0:
                i = v / r
                self.result_label.config(text=f"Current = {i:.2f} A")
            elif r == 0 and v != 0 and i != 0:
                r = v / i
                self.result_label.config(text=f"Resistance = {r:.2f} Ω")
            else:
                self.result_label.config(text="Please enter any two values")
        except ValueError:
            self.result_label.config(text="Please enter valid numbers")
            
    def setup_resistor_calculator(self):
        # Create input fields for resistor color code
        colors = ['Black', 'Brown', 'Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Violet', 'Grey', 'White']
        
        ttk.Label(self.calc_frame, text="First Band:").grid(row=0, column=0, pady=5)
        self.first_band = ttk.Combobox(self.calc_frame, values=colors)
        self.first_band.grid(row=0, column=1, pady=5)
        
        ttk.Label(self.calc_frame, text="Second Band:").grid(row=1, column=0, pady=5)
        self.second_band = ttk.Combobox(self.calc_frame, values=colors)
        self.second_band.grid(row=1, column=1, pady=5)
        
        ttk.Label(self.calc_frame, text="Multiplier:").grid(row=2, column=0, pady=5)
        multipliers = ['Black', 'Brown', 'Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Violet', 'Grey', 'White', 'Gold', 'Silver']
        self.multiplier = ttk.Combobox(self.calc_frame, values=multipliers)
        self.multiplier.grid(row=2, column=1, pady=5)
        
        ttk.Label(self.calc_frame, text="Tolerance:").grid(row=3, column=0, pady=5)
        tolerances = ['Brown', 'Red', 'Gold', 'Silver']
        self.tolerance = ttk.Combobox(self.calc_frame, values=tolerances)
        self.tolerance.grid(row=3, column=1, pady=5)
        
        ttk.Button(self.calc_frame, text="Calculate", command=self.calculate_resistor).grid(row=4, column=0, columnspan=2, pady=10)
        
    def calculate_resistor(self):
        try:
            color_values = {'Black': 0, 'Brown': 1, 'Red': 2, 'Orange': 3, 'Yellow': 4,
                          'Green': 5, 'Blue': 6, 'Violet': 7, 'Grey': 8, 'White': 9}
            multiplier_values = {'Black': 1, 'Brown': 10, 'Red': 100, 'Orange': 1000,
                              'Yellow': 10000, 'Green': 100000, 'Blue': 1000000,
                              'Violet': 10000000, 'Grey': 100000000, 'White': 1000000000,
                              'Gold': 0.1, 'Silver': 0.01}
            tolerance_values = {'Brown': '±1%', 'Red': '±2%', 'Gold': '±5%', 'Silver': '±10%'}
            
            first = color_values[self.first_band.get()]
            second = color_values[self.second_band.get()]
            mult = multiplier_values[self.multiplier.get()]
            tol = tolerance_values[self.tolerance.get()]
            
            resistance = (first * 10 + second) * mult
            self.result_label.config(text=f"Resistance = {resistance:.2f} Ω {tol}")
        except KeyError:
            self.result_label.config(text="Please select all color bands")
            
    def setup_potential_dividers_calculator(self):
        ttk.Label(self.calc_frame, text="Input Voltage (V):").grid(row=0, column=0, pady=5)
        self.vin = ttk.Entry(self.calc_frame)
        self.vin.grid(row=0, column=1, pady=5)
        
        ttk.Label(self.calc_frame, text="R1 (Ω):").grid(row=1, column=0, pady=5)
        self.r1 = ttk.Entry(self.calc_frame)
        self.r1.grid(row=1, column=1, pady=5)
        
        ttk.Label(self.calc_frame, text="R2 (Ω):").grid(row=2, column=0, pady=5)
        self.r2 = ttk.Entry(self.calc_frame)
        self.r2.grid(row=2, column=1, pady=5)
        
        ttk.Button(self.calc_frame, text="Calculate", command=self.calculate_potential_divider).grid(row=3, column=0, columnspan=2, pady=10)
        
    def calculate_potential_divider(self):
        try:
            vin = float(self.vin.get())
            r1 = float(self.r1.get())
            r2 = float(self.r2.get())
            
            vout = vin * (r2 / (r1 + r2))
            self.result_label.config(text=f"Output Voltage = {vout:.2f} V")
        except ValueError:
            self.result_label.config(text="Please enter valid numbers")
            
    def setup_series_parallel_calculator(self):
        ttk.Label(self.calc_frame, text="Number of Resistors:").grid(row=0, column=0, pady=5)
        self.num_resistors = ttk.Entry(self.calc_frame)
        self.num_resistors.grid(row=0, column=1, pady=5)
        
        ttk.Label(self.calc_frame, text="Connection Type:").grid(row=1, column=0, pady=5)
        self.connection_type = ttk.Combobox(self.calc_frame, values=['Series', 'Parallel'])
        self.connection_type.grid(row=1, column=1, pady=5)
        
        ttk.Button(self.calc_frame, text="Add Resistors", command=self.add_resistor_inputs).grid(row=2, column=0, columnspan=2, pady=10)
        
    def add_resistor_inputs(self):
        try:
            num = int(self.num_resistors.get())
            for i in range(num):
                ttk.Label(self.calc_frame, text=f"R{i+1} (Ω):").grid(row=i+3, column=0, pady=5)
                entry = ttk.Entry(self.calc_frame)
                entry.grid(row=i+3, column=1, pady=5)
                if not hasattr(self, 'resistor_entries'):
                    self.resistor_entries = []
                self.resistor_entries.append(entry)
            
            ttk.Button(self.calc_frame, text="Calculate", command=self.calculate_series_parallel).grid(row=num+3, column=0, columnspan=2, pady=10)
        except ValueError:
            self.result_label.config(text="Please enter a valid number")
            
    def calculate_series_parallel(self):
        try:
            resistors = [float(entry.get()) for entry in self.resistor_entries]
            if self.connection_type.get() == 'Series':
                total = sum(resistors)
                self.result_label.config(text=f"Total Resistance (Series) = {total:.2f} Ω")
            else:
                total = 1 / sum(1/r for r in resistors)
                self.result_label.config(text=f"Total Resistance (Parallel) = {total:.2f} Ω")
        except ValueError:
            self.result_label.config(text="Please enter valid numbers")
            
    def setup_led_resistor_calculator(self):
        ttk.Label(self.calc_frame, text="Supply Voltage (V):").grid(row=0, column=0, pady=5)
        self.supply_voltage = ttk.Entry(self.calc_frame)
        self.supply_voltage.grid(row=0, column=1, pady=5)
        
        ttk.Label(self.calc_frame, text="LED Forward Voltage (V):").grid(row=1, column=0, pady=5)
        self.led_voltage = ttk.Entry(self.calc_frame)
        self.led_voltage.grid(row=1, column=1, pady=5)
        
        ttk.Label(self.calc_frame, text="LED Current (mA):").grid(row=2, column=0, pady=5)
        self.led_current = ttk.Entry(self.calc_frame)
        self.led_current.grid(row=2, column=1, pady=5)
        
        ttk.Button(self.calc_frame, text="Calculate", command=self.calculate_led_resistor).grid(row=3, column=0, columnspan=2, pady=10)
        
    def calculate_led_resistor(self):
        try:
            vs = float(self.supply_voltage.get())
            vf = float(self.led_voltage.get())
            i = float(self.led_current.get()) / 1000  # Convert mA to A
            
            r = (vs - vf) / i
            self.result_label.config(text=f"Required Resistor = {r:.2f} Ω")
        except ValueError:
            self.result_label.config(text="Please enter valid numbers")

if __name__ == "__main__":
    root = tk.Tk()
    app = EngineeringCalculator(root)
    root.mainloop()
