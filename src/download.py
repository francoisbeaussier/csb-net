import requests
import json
import time
import os.path
from os import path

player_name = 'recurse'

# We download using the agent_id, so we learn from the same bot version
agent_id = 2843387 # reCurse
agent_id = 2697232 # Aelyanne

game_list_url = 'https://www.codingame.com/services/gamesPlayersRanking/findLastBattlesByAgentId'

content = f'[{agent_id}, null]'

response = requests.post(game_list_url, data=content)

game_list = json.loads(response.content)

game_url = 'https://www.codingame.com/services/gameResult/findByGameId'

# Uncomment to test on just a few requests
# game_list = game_list[:2]

print(f'found {len(game_list)} games')

output_path = f'downloads/{player_name}/{agent_id}'
if not os.path.exists(output_path):
    print('Creating folder ', output_path)
    os.makedirs(output_path)

for idx, game in enumerate(game_list):
    game_id = game['gameId']
    content = f'[{game_id}, null]'
    response = requests.post(game_url, data = content)
    
    player1_id = game['players'][0]['userId']
    player1_name = game['players'][0]['nickname']
    player2_id = game['players'][1]['userId']
    player2_name = game['players'][1]['nickname']

    output_file = f'{output_path}/{game_id}.{player1_id}.{player2_id}.{player1_name}_vs_{player2_name}.json'

    game_info = json.loads(response.content)

    if not path.exists(output_file):
        print(f'[{idx}/{len(game_list)}] + {output_file}')

        f = open(output_file, 'w', encoding="utf8")    
        json.dump(game_info, f, indent = 4)
        f.close()
    else:
        print(f'[{idx}/{len(game_list)}] - {output_file}')

    # Let's not overload the CG servers
    time.sleep(1)
