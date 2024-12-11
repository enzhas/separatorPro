# @app.route('/calc', methods=['GET', 'POST'])
# def calc():
#     if request.method == 'POST':
#         try:
#             # Get input data from the form
#             Qg = float(request.form['Qg']) * 1_000_000 / 86400  # Convert MMSCFD to ft³/s
#             Qo = float(request.form['Qo']) * 5.615 / 86400  # Convert BOPD to ft³/s
#             Qw = float(request.form['Qw']) * 5.615 / 86400  # Convert BWPD to ft³/s
#             P = float(request.form['P'])  # psia
#             T = float(request.form['T']) + 459.67  # Convert °F to °R
#             Sg = float(request.form['Sg'])  # Specific gravity of gas
#             API = float(request.form['API'])  # Oil API gravity
#             SG_w = float(request.form['SG_w'])  # Specific gravity of water
#             retention_time = float(request.form['retention_time']) * 60  # Convert minutes to seconds
#             separator_type = request.form['separator_type']  # Vertical or Horizontal

#             # Constants
#             droplet_size = 1.07e-7  # Droplet size removal in feet
#             g = 32.17  # Gravity constant (ft/s^2)
#             mu_g = 0.000012  # Gas viscosity (lb/ft-s)
#             density_constant = 62.4  # lb/ft³

#             # Calculations
#             rho_g = (28.97 * Sg * P) / (10.73 * T)  # Gas density
#             SG_o = 141.5 / (API + 131.5)  # Specific gravity of oil
#             rho_o = SG_o * density_constant  # Density of oil
#             rho_w = SG_w * density_constant  # Density of water
#             rho_L = (Qo * rho_o + Qw * rho_w) / (Qo + Qw)  # Average liquid density

#             V_liquid = (Qo + Qw) * retention_time  # Volume of liquid
#             v = (droplet_size * (rho_L - rho_g) * g) / (18 * mu_g)  # Droplet velocity
#             A = Qg / v  # Cross-sectional area
#             D = sqrt((4 * A) / pi)  # Separator diameter

#             # Calculate separator length for Vertical or Horizontal
#             if separator_type == "Vertical":
#                 length = V_liquid / (pi * (D / 2) ** 2)  # Length for vertical separator
#             elif separator_type == "Horizontal":
#                 length = V_liquid / (D / 2)  # Length for horizontal separator
#             else:
#                 raise ValueError("Invalid separator type")

#             # Results to display
#             results = {
#                 "density_gas": f"{rho_g:.2f}",
#                 "sg_oil": f"{SG_o:.3f}",
#                 "density_oil": f"{rho_o:.2f}",
#                 "density_water": f"{rho_w:.2f}",
#                 "volume_liquid": f"{V_liquid:.2f}",
#                 "velocity": f"{v:.3f}",
#                 "area": f"{A:.2f}",
#                 "diameter": f"{D:.2f}",
#                 "length": f"{length:.2f}"
#             }

#             return render_template('calc.html', results=results)

#         except ValueError:
#             return "Invalid input, please check your values."
#     return render_template('calc.html')