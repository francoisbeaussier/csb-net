import glob
import os
import json
import subprocess

player_name = 'recurse' # reCurse
agent_id = 2843387

input_path = f'downloads/{player_name}/{agent_id}'
output_path = f'converted/{player_name}/{agent_id}'

if not os.path.exists(output_path):
    os.makedirs(output_path)

files = glob.glob(f'{input_path}/*_vs_*.json')

# files = files[:2]

print(f'Found {len(files)} games')

for idx, file in enumerate(files):
    f = open(file, 'r')
    content = json.load(f)

    # print(f'> {file}')

    output_file = file.replace('downloads', 'converted').replace('.json', '.txt')
    subprocess.call(['python', 'simulator/csbref/validate.py', 'simulator/csbref/csbref.exe', file, output_file])

    f.close()
