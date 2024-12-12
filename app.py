from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd
from werkzeug.utils import secure_filename
from fpdf import FPDF
from math import sqrt, pi
import tempfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store results for download
latest_results = []

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calc', methods=['GET', 'POST'])
def calc():
    if request.method == 'POST':
        try:
            # Get input data from the form
            Qg = float(request.form['Qg'])
            Qo = float(request.form['Qo']) 
            Qw = float(request.form['Qw'])  
            Po = float(request.form['P'])  # psia
            To = float(request.form['T']) + 459.67  # Convert °F to °R
            Sg = float(request.form['Sg'])  # Specific gravity of gas
            SG_o = float(request.form['SG_o'])  # Specific gravity of Oil
            SG_w = float(request.form['SG_w'])  # Specific gravity of water
            Z = float(request.form['Z'])  # Gas compressibility factor
            mu = float(request.form['M']) # mu
            # liquid_d_m = float(request.form['liquid_d_m']) # in micro
            # water_d_m = float(request.form['water_d_m'])# in micro
            # oil_d_m = float(request.form['oil_d_m'])# in micro
            tr_o = float(request.form['tr_o'])
            tr_w = float(request.form['tr_w'])
            B = float(request.form['B'])
            # retention_time = float(request.form['retention_time']) * 60  # Convert minutes to seconds
            separator_type = request.form['separator_type']  # Vertical or Horizontal

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
                D_l = 5040 * (T * Z * Qg / Po) * ((gas_density_pg / (liquid_density_pl - gas_density_pg)) * (0.25 / liquid_d_m)) if 5040 * (T * Z * Qg / Po) * ((gas_density_pg / (liquid_density_pl - gas_density_pg)) * (0.25 / liquid_d_m)) > 0 else 0 ** 0.25
                D_o = 6690 * (Qo * mu) / (dSG * (oil_d_m ** 2)) if 6690 * (Qo * mu) / (dSG * (oil_d_m ** 2)) > 0 else 0 ** 0.5
                D_w = 6690 * (Qo * mu) / (dSG * (water_d_m ** 2)) if 6690 * (Qo * mu) / (dSG * (water_d_m ** 2)) > 0 else 0 ** 0.5
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
                    "slenderness_ratio": round(SR, 2),
                    "liquid_density": round(liquid_density_pl, 2),
                    "gas_density": round(gas_density_pg, 2),
                    "settling_velocity": round(Vt, 2),
                    "Reynolds_number": round(Re, 2),
                    "drag_coefficient": round(Cd, 2)
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
                    "Lss_liquid": Lss_liquid,
                    "d": d,
                    "Leff": Leff,
                    "SR_liquid": SR_liquid
                }
            return render_template('calc.html', results=results)

        except ValueError:
            return "Invalid input, please check your values."
    return render_template('calc.html')

# Handle File Upload and Processing
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file uploaded!", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file!", 400

    # Use a temporary directory for file uploads
    with tempfile.TemporaryDirectory() as tmpdirname:
        file_path = os.path.join(tmpdirname, secure_filename(file.filename))
        file.save(file_path)

        try:
            result = process_file(file_path)
            global latest_results
            latest_results = result
        except KeyError as e:
            return f"Error: Missing expected column(s): {str(e)} in the file.", 400
        except ValueError as e:
            return f"Error: {str(e)}", 400
        except Exception as e:
            return f"Error processing file: {str(e)}", 400

        return render_template('result.html', result=result)

# Process the uploaded file and return recommendations
def process_file(file_path):
    try:
        data = pd.read_excel(file_path)
    except Exception as e:
        raise Exception("Unable to read the file. Please ensure it is a valid Excel file.")

    # Normalize column names to avoid issues
    data.columns = [col.strip() for col in data.columns]

    # Required columns
    required_columns = ['Gas Flow', 'Oil Flow', 'Water Flow', 'Sand Content', 'Operating Pressure',
                        'Operating Temperature', 'Oil API Gravity', 'Gas Specific Gravity', 'Field Type']
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        raise KeyError(f"Missing columns: {', '.join(missing_columns)}")

    # Calculate GOR (Gas-to-Oil Ratio) and Water Cut
    data['GOR (scf/bbl)'] = data.apply(lambda row: row['Gas Flow'] / row['Oil Flow'] if row['Oil Flow'] != 0 else 0, axis=1)

    data['Water Cut'] = data.apply(lambda row: row['Water Flow'] / (row['Oil Flow'] + row['Gas Flow'] + row['Water Flow']) if (row['Oil Flow'] + row['Gas Flow'] + row['Water Flow']) != 0 else 0, axis=1)

    # Convert Gas Specific Gravity to Molar Mass
    data['Molar Mass of Gas (kg/mol)'] = data['Gas Specific Gravity'] * 28.97 / 1000

    # Define constants for calculations
    API_CONVERSION = 141.5
    GAS_CONSTANT = 8.314

    # Function to calculate oil density
    def api_to_density(api_gravity):
        return API_CONVERSION / (api_gravity + 131.5)

    # Function to calculate gas density
    def gas_density(pressure, temperature, molar_mass):
        return (pressure * molar_mass) / (GAS_CONSTANT * temperature)

    # Perform calculations for each row
    recommendations = []
    for _, row in data.iterrows():
        # Oil density
        oil_density = api_to_density(row['Oil API Gravity'])

        # Gas density
        gas_density_value = gas_density(row['Operating Pressure'], row['Operating Temperature'], row['Molar Mass of Gas (kg/mol)'])

        # Volumes
        oil_volume = row['Oil Flow'] * 0.159
        GOR_in_m3_m3 = row['GOR (scf/bbl)'] * 0.0283168 / 5.6146
        gas_volume = oil_volume * GOR_in_m3_m3
        total_volume = oil_volume + gas_volume
        if row['Water Cut'] >= 1:
            raise ValueError("Water Cut cannot be 100% or more.")
        total_fluid_volume = total_volume / max(1 - row['Water Cut'], 0.0001)  # Prevent division by zero
        # total_fluid_volume = total_volume / (1 - row['Water Cut'])

        water_volume = total_fluid_volume * row['Water Cut']

        # Fractions
        oil_fraction = oil_volume / total_fluid_volume
        gas_fraction = gas_volume / total_fluid_volume
        water_fraction = water_volume / total_fluid_volume

        # Separator logic
        if row['Gas Flow'] > 15 or row['Water Flow'] > 8000:
            separator_type = "Horizontal Separator"
            reason = "Handles high gas and water flow efficiently due to a larger settling area."
        elif row['Sand Content'] > 5:
            separator_type = "Vertical Separator"
            reason = "Recommended for high sand content to minimize clogging."
        elif row['Gas Flow'] > 10 and row['Water Flow'] > 5000 and row['Sand Content'] < 5:
            separator_type = "Horizontal Separator"
            reason = "High gas, water, and sand content; suitable for managing multiphase flows."
        elif row['Gas Specific Gravity'] > 0.8:
            separator_type = "Horizontal Separator"
            reason = "Better suited for gases with higher specific gravity, offering sufficient retention time."
        elif row['Field Type'] == "Offshore" and row['Oil Flow'] > 1000:
            separator_type = "Vertical Separator"
            reason = "Compact design suitable for installations with high oil flow, where space is limited."
        elif row['Oil API Gravity'] < 25 and row['Water Flow'] > 4000:
            separator_type = "Horizontal Separator"
            reason = "Heavy oil and significant water flow require efficient separation."
        elif row['Gas Flow'] > 20 and row['Oil Flow'] < 500:
            separator_type = "Horizontal Separator"
            reason = "High gas-to-oil ratio; better suited for gas-dominant conditions."
        elif row['Gas Flow'] < 5 and row['Water Flow'] < 3000:
            separator_type = "Vertical Separator"
            reason = "Suitable for low GOR."
        elif row['Oil API Gravity'] > 40:
            separator_type = "Vertical Separator"
            reason = "Optimal for light oil with high API gravity."
        else:
            separator_type = "Vertical Separator"
            reason = "Default choice for general conditions."


        # separator_type, reason = determine_separator_type(row)

        recommendations.append({
            "Separator Type": separator_type,
            "Reason": reason,
            "Oil Flow (BOPD)": row['Oil Flow'],
            "Water Flow (BWPD)": row['Water Flow'],
            "Gas Flow (MMscfd)": row['Gas Flow'],
            "Sand Content (%)": row['Sand Content'],
            "Separated Oil (BOPD)": oil_volume * 1000,  # Adjusted for scaling
            "Separated Water (BWPD)": water_volume * 1000,
            "Separated Gas (MMscfd)": gas_volume * 35.315,  # Convert m^3 to MMscfd
            "Flash Oil Fraction (%)": oil_fraction * 100,
            "Flash Water Fraction (%)": water_fraction * 100,
            "Flash Gas Fraction (%)": gas_fraction * 100
        })

    return recommendations

# Generate and Download PDF
@app.route('/download-pdf')
def download_pdf():
    from flask import send_file
    class PDF(FPDF):
        def __init__(self, orientation='L', unit='mm', format='A3'):
            super().__init__(orientation, unit, format)

        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'Separator Calculation Results', align='C', ln=True)
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', align='C')

    pdf = PDF('L')  # 'L' for landscape orientation
    pdf.add_page()
    pdf.set_font('Arial', '', 8)

    # Table header
    headers = [
        "Separator Type", "Reason", "Oil Flow (BOPD)", "Water Flow (BWPD)",
        "Gas Flow (MMscfd)", "Sand Content (%)", "Separated Oil (BOPD)",
        "Separated Water (BWPD)", "Separated Gas (MMscfd)",
        "Flash Oil Fraction (%)", "Flash Water Fraction (%)", "Flash Gas Fraction (%)"
    ]
    
    # Column width settings
    col_width = 34  # Standard column width for most columns
    row_height = 20  # Standard row height
    reason_col_width = 34  # Wider width for the 'Reason' column

    # Add table headers
    for header in headers:
        pdf.cell(col_width, row_height, header, border=1, align='C')
    pdf.ln()

    # Add rows for each result
    for result in latest_results:
        row = [
            result['Separator Type'],
            result['Reason'],  # This will be handled with multi_cell for text wrapping
            str(result['Oil Flow (BOPD)']), str(result['Water Flow (BWPD)']),
            str(result['Gas Flow (MMscfd)']), str(result['Sand Content (%)']),
            str(result['Separated Oil (BOPD)']),
            str(result['Separated Water (BWPD)']), str(result['Separated Gas (MMscfd)']),
            f"{result['Flash Oil Fraction (%)']:.5f}",
            f"{result['Flash Water Fraction (%)']:.5f}",
            f"{result['Flash Gas Fraction (%)']:.5f}"
        ]

        # First column ("Separator Type")
        pdf.cell(col_width, row_height, row[0], border=1, align='C')

        # Save current X and Y for later use
        x_before = pdf.get_x()
        y_before = pdf.get_y()

        # Reason column - Use multi_cell for wrapping text
        pdf.multi_cell(reason_col_width, 5, row[1], border=1, align='C')

        # Restore X and move Y to match the height of the tallest cell in this row
        pdf.set_xy(x_before + reason_col_width, y_before)

        # Add remaining cells
        for i in range(2, len(row)):
            pdf.cell(col_width, row_height, row[i], border=1, align='C')

        pdf.ln() 


    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        pdf.output(temp_pdf.name)
        temp_pdf.seek(0)
        return send_file(temp_pdf.name, as_attachment=True, download_name="results.pdf")

if __name__ == "__main__":
    app.run(debug=True, port=5001)
