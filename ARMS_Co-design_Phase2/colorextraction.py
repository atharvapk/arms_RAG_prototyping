import subprocess
import json

exe_path = r"C:\Users\athar\Documents\arms_da-team\verification\bin\Debug\net10.0\verification.exe"

def rgb_to_hex(r, g, b):
    return f'{r:02x}{g:02x}{b:02x}'

target_face = "cylindrical_face"

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
    
    r, g, b = map(int, color_values)
    hex = rgb_to_hex(r, g, b)
    print(f"Python received! Red: {r}, Green: {g}, Blue: {b}")
    print(hex)

    data = {
        "target_face": target_face, 
        "hex": hex
    }

    with open('color_output.json', 'w') as json_file:
        json.dump(data, json_file)
else:
    print("No color data found in output.")