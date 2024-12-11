import tkinter as tk
from tkinter import ttk, messagebox
from math import sqrt, pi

def calculate(separator_type="Vertical"):
    try:
        # Input values
        Qg = float(entry_Qg.get()) * 1_000_000 / 86400  # Convert MMSCFD to ft³/s
        Qo = float(entry_Qo.get()) * 5.615 / 86400  # Convert BOPD to ft³/s
        Qw = float(entry_Qw.get()) * 5.615 / 86400  # Convert BWPD to ft³/s
        P = float(entry_P.get())  # psia
        T = float(entry_T.get()) + 459.67  # Convert °F to °R
        Sg = float(entry_Sg.get())  # Specific gravity of gas
        API = float(entry_API.get())  # Oil API gravity
        SG_w = float(entry_SG_w.get())  # Specific gravity of water
        retention_time = float(entry_retention_time.get()) * 60  # Convert minutes to seconds

        # Constants
        droplet_size = 1.07e-7  # Droplet size removal in feet
        g = 32.17  # Gravity constant (ft/s^2)
        mu_g = 0.000012  # Gas viscosity (lb/ft-s)
        density_constant = 62.4  # lb/ft³

        # Calculations
        rho_g = (28.97 * Sg * P) / (10.73 * T)  # Gas density
        SG_o = 141.5 / (API + 131.5)  # Specific gravity of oil
        rho_o = SG_o * density_constant  # Density of oil
        rho_w = SG_w * density_constant  # Density of water
        rho_L = (Qo * rho_o + Qw * rho_w) / (Qo + Qw)  # Average liquid density

        V_liquid = (Qo + Qw) * retention_time  # Volume of liquid
        v = (droplet_size * (rho_L - rho_g) * g) / (18 * mu_g)  # Droplet velocity
        A = Qg / v  # Cross-sectional area
        D = sqrt((4 * A) / pi)  # Separator diameter

        # Calculate separator length for Vertical or Horizontal
        if separator_type == "Vertical":
            length = V_liquid / (pi * (D / 2) ** 2)  # Length for vertical separator
        elif separator_type == "Horizontal":
            length = V_liquid / (D / 2)  # Length for horizontal separator
        else:
            raise ValueError("Invalid separator type")

        # Update results
        result_density_gas.set(f"{rho_g:.2f} lb/ft³")
        result_sg_oil.set(f"{SG_o:.3f}")
        result_density_oil.set(f"{rho_o:.2f} lb/ft³")
        result_density_water.set(f"{rho_w:.2f} lb/ft³")
        result_volume_liquid.set(f"{V_liquid:.2f} ft³")
        result_velocity.set(f"{v:.3f} ft/s")
        result_area.set(f"{A:.2f} ft²")
        result_diameter.set(f"{D:.2f} ft")
        result_length.set(f"{length:.2f} ft")

    except ValueError:
        messagebox.showerror("Error", "Please enter valid inputs!")

# GUI Setup
root = tk.Tk()
root.title("Three-Phase Separator Calculator")
root.geometry("500x800")
root.configure(bg="#f2f2f7")

# Style Configuration
style = ttk.Style()
style.configure("TLabel", font=("San Francisco", 14), background="#f2f2f7", foreground="#000")
style.configure("TButton", font=("San Francisco", 14), foreground="#ffffff", background="#007aff", borderwidth=0)

# Input Frame
frame_input = ttk.LabelFrame(root, text="Input Parameters", padding=(10, 10))
frame_input.pack(fill="both", padx=10, pady=5)

# Input Fields
inputs = [
    ("Gas flow rate (Qg, MMSCFD):", "Qg"),
    ("Oil flow rate (Qo, BOPD):", "Qo"),
    ("Water flow rate (Qw, BWPD):", "Qw"),
    ("Pressure (P, psia):", "P"),
    ("Temperature (T, °F):", "T"),
    ("Specific gravity of gas (Sg):", "Sg"),
    ("Oil API gravity (°API):", "API"),
    ("Specific gravity of water (Sg_w):", "SG_w"),
    ("Retention time (minutes):", "retention_time"),
]

entries = {}
for label_text, key in inputs:
    frame_field = ttk.Frame(frame_input)
    frame_field.pack(fill="both", pady=2)
    ttk.Label(frame_field, text=label_text).pack(side="left", anchor="w", padx=5)
    entry = ttk.Entry(frame_field, font=("San Francisco", 12), width=12)
    entry.pack(side="right", padx=5)
    entries[key] = entry

entry_Qg = entries["Qg"]
entry_Qo = entries["Qo"]
entry_Qw = entries["Qw"]
entry_P = entries["P"]
entry_T = entries["T"]
entry_Sg = entries["Sg"]
entry_API = entries["API"]
entry_SG_w = entries["SG_w"]
entry_retention_time = entries["retention_time"]

# Output Frame
frame_output = ttk.LabelFrame(root, text="Output Results", padding=(10, 10))
frame_output.pack(fill="both", padx=10, pady=5)

outputs = [
    ("Gas density:", "density_gas"),
    ("Specific gravity of oil:", "sg_oil"),
    ("Density of oil:", "density_oil"),
    ("Density of water:", "density_water"),
    ("Volume of liquid:", "volume_liquid"),
    ("Droplet velocity:", "velocity"),
    ("Cross-sectional area:", "area"),
    ("Separator diameter:", "diameter"),
    ("Separator length:", "length"),
]

results = {}
for label_text, key in outputs:
    frame_field = ttk.Frame(frame_output)
    frame_field.pack(fill="both", pady=2)
    ttk.Label(frame_field, text=label_text).pack(side="left", anchor="w", padx=5)
    result_var = tk.StringVar(value="N/A")
    ttk.Label(frame_field, textvariable=result_var, anchor="e").pack(side="right", padx=5)
    results[key] = result_var

result_density_gas = results["density_gas"]
result_sg_oil = results["sg_oil"]
result_density_oil = results["density_oil"]
result_density_water = results["density_water"]
result_volume_liquid = results["volume_liquid"]
result_velocity = results["velocity"]
result_area = results["area"]
result_diameter = results["diameter"]
result_length = results["length"]

# Buttons for calculation
btn_vertical = tk.Button(
    root,
    text="Calculate Vertical Separator",
    command=lambda: calculate(separator_type="Vertical"),
    font=("San Francisco", 14),
    fg="white",
    bg="#007aff",
    activebackground="#005fcb",
    bd=0,
    padx=20,
    pady=10,
)
btn_vertical.pack(pady=10)

btn_horizontal = tk.Button(
    root,
    text="Calculate Horizontal Separator",
    command=lambda: calculate(separator_type="Horizontal"),
    font=("San Francisco", 14),
    fg="white",
    bg="#007aff",
    activebackground="#005fcb",
    bd=0,
    padx=20,
    pady=10,
)
btn_horizontal.pack(pady=10)

# Run Application
root.mainloop()
