import subprocess
import json

exe_path = r"C:\Users\athar\Documents\arms_da-team\verification\bin\Debug\net10.0\verification.exe"

def rgb_to_hex(r, g, b):
    return f'{r:02x}{g:02x}{b:02x}'

target_face = "cylindrical_face"
fitdict = {
    "ffc0c0": "Locational Clearance",  # red
    "c0ffc0": "Close Running",  # green
    "c0c0ff": "Free Running"  # blue
}

result = subprocess.run(
    [exe_path, "colorcheck", target_face], 
    capture_output=True, 
    text=True
)

print(result.stdout)
output = result.stdout
if "COLOR_DATA:" in output:
    data_line = [line for line in output.split('\n') if "COLOR_DATA:" in line][0]
    color_values = data_line.replace("COLOR_DATA:", "").split(',')

    data_line = [line for line in output.split('\n') if "BASIC_SIZE:" in line][0]
    basic_size = data_line.replace("BASIC_SIZE:", "").strip()
    
    r, g, b = map(int, color_values)
    hex = rgb_to_hex(r, g, b)
    fit_category = fitdict.get(hex, "Unknown Fit Category")
    print(f"Python received! Red: {r}, Green: {g}, Blue: {b}")
    print(hex)

    if target_face == "cylindrical_face":
        data = {
            "target_face": target_face, 
            "hex": hex,
            "basic_size": basic_size,
            "fit_category": fit_category
        }

    with open('color_output.json', 'w') as json_file:
        json.dump(data, json_file)
else:
    print("No color data found in output.")