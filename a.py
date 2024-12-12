def calculate_separator(Qg, Qo, Qw, Po, To, Sg, SG_o, SG_w, Z, mu, tr_o, tr_w, B, separator_type):
    """
    Automates separator calculations for vertical and horizontal separators.

    Parameters:
        Qg (float): Gas flow rate in MMscfd.
        Qo (float): Oil flow rate in BOPD.
        Qw (float): Water flow rate in BWPD.
        Po (float): Operating pressure in psia.
        To (float): Operating temperature in °F.
        Sg (float): Specific gravity of gas.
        SG_o (float): Specific gravity of oil.
        SG_w (float): Specific gravity of water.
        Z (float): Gas compressibility factor.
        mu (float): Viscosity in cp.
        tr_o (float): Oil retention time in minutes.
        tr_w (float): Water retention time in minutes.
        B (float): Proportionality constant for horizontal separators.
        separator_type (str): 'Vertical' or 'Horizontal'.

    Returns:
        dict: Results of the separator calculations.
    """
    # Convert temperature to Rankine
    T = To + 459.67

    # Convert retention times to seconds
    tr_o_sec = tr_o * 60
    tr_w_sec = tr_w * 60

    # Calculate liquid density (lb/ft³)
    liquid_density_pl = 62.4 * (141.5 / (131.5 + SG_o))

    # Calculate gas density (lb/ft³)
    gas_density_pg = (2.7 * Sg * Po) / (T * Z)

    # Initialize constants
    Cd = 0.25
    liquid_d_m = 100  # droplet diameter for liquid in microns
    water_d_m = 500
    oil_d_m = 200

    # Settling velocity and drag coefficient iteration
    for _ in range(5):
        Vt = 0.0119 * ((liquid_density_pl - gas_density_pg) / gas_density_pg * liquid_d_m / Cd)
        Re = 0.0049 * (gas_density_pg * liquid_d_m * Vt) / mu
        Cd = 24 / Re + 3 / (Re ** 0.5) + 0.34

    # Gravity difference for oil-water separation
    dSG = SG_w - (141.5 / (131.5 + SG_o))

    if separator_type.lower() == "vertical":
        D_l = 5040 * (T * Z * Qg / Po) * ((gas_density_pg / (liquid_density_pl - gas_density_pg)) * (0.25 / liquid_d_m)) ** 0.25
        D_o = 6690 * (Qo * mu) / (dSG * (oil_d_m ** 2)) ** 0.5
        D_w = 6690 * (Qo * mu) / (dSG * (water_d_m ** 2)) ** 0.5
        D = max(D_l, D_o, D_w)
        H = (tr_o_sec * Qo + tr_w_sec * Qw) / (0.12 * D ** 2)  # Height for retention
        if D <= 36:
            Lss = (H + 76) / 12
        else:
            Lss = (H + D + 40) / 12
        SR = (12 * Lss) / D  # Slenderness Ratio

        results = {
            "diameter": round(D, 2),
            "height": round(H, 2),
            "length": round(Lss, 2),
            "slenderness_ratio": round(SR, 2)
        }

    elif separator_type.lower() == "horizontal":
        H = (1.28 * (10 ** (-3)) * (tr_o_sec * dSG * (water_d_m ** 2))) / mu # Max oil pad thickness
        AA = 0.5 * Qw * tr_w / (tr_o_sec * Qo + tr_w_sec * Qw)

        D = H / B
      
        # Step 6: Calculate dLeff based on gas capacity constraint
        dLeff = 420 * (T * Z * Qg / Po) * (((gas_density_pg / (liquid_density_pl - gas_density_pg)) * (Cd / liquid_d_m)) ** 0.5)

        # Step 7: Calculate dLeff based on oil and water retention time constraints
        d2Leff_retention = 1.42 * (Qw * tr_w_sec + Qo * tr_o_sec)

        dLeff_retention = (d2Leff_retention ** 0.5) / 12

        d = []
        d.append(dLeff / 2)
        Leff = []
        Leff.append(d2Leff_retention / (d[0] / 2))
        # Lss_gas = []
        # Lss_gas.append(Leff[0] + d[0] / 12)
        Lss_liquid = []
        Lss_liquid.append(4/3 * Leff[0])
        # SR_gas = []
        SR_liquid = []
        SR_liquid.append((12 * Lss_liquid[0])/d[0])


        for i in range(1, 9):
            d.append(d[-1] + 15)
            Leff.append(d2Leff_retention / (d[i] / 2))
            # Lss_gas.append(Leff[i] + d[i] / 12)
            Lss_liquid.append(4/3 * Leff[i])

            SR_liquid.append((12 * Lss_liquid[i])/d[i])



        results = {
            "diameter": round(D, 2),
            "dLeff_gas": round(dLeff, 2),
            "dLeff_retention": round(dLeff_retention, 2),
            "Lss_liquid": Lss_liquid
        }
    else:
        raise ValueError("Invalid separator type")

    return results

# Example usage
if __name__ == "__main__":
    # Replace these values with actual inputs
    example_inputs = {
        "Qg": 6.6,
        "Qo": 5000,
        "Qw": 6000,
        "Po": 65,
        "To": 90,
        "Sg": 0.6,
        "SG_o": 30,
        "SG_w": 1.07,
        "Z": 0.85,
        "mu": 10,
        "tr_o": 5,
        "tr_w": 10,
        "B": 0.5,
        "separator_type": "Horizontal"
    }

    results = calculate_separator(**example_inputs)
    print("Calculation Results:", results)
