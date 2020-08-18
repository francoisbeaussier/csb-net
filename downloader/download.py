import requests
import json
import time
import os.path
from os import path

player_id = 2354166 # reCurse
player_name = 'recurse'

game_list_url = 'https://www.codingame.com/services/gamesPlayersRanking/findLastBattlesByAgentId'

content = f'[{player_id}, null]'

response = requests.post(game_list_url, data=content)

game_list = json.loads(response.content)

game_url = 'https://www.codingame.com/services/gameResult/findByGameId'

# game_list = game_list[:2]

for idx, game in enumerate(game_list):
    game_id = game['gameId']
    content = f'[{game_id}, null]'
    response = requests.post(game_url, data = content)
    
    player1_id = game['players'][0]['userId']
    player1_name = game['players'][0]['nickname']
    player2_id = game['players'][1]['userId']
    player2_name = game['players'][1]['nickname']

    output_file = f'{player_name}/{game_id} {player1_id}-{player2_id} {player1_name} vs {player2_name}'

    game_info = json.loads(response.content)

    if not path.exists(output_file):
        print(f'[{idx}/{len(game_list)}] + {output_file}')

        f = open(output_file, 'w', encoding="utf8")    
        json.dump(game_info, f, indent = 4)
        f.close()
    else:
        print(f'[{idx}/{len(game_list)}] - {output_file}')

    time.sleep(1)
