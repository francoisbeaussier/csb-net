import glob
import os
import json
import math

# player_name = 'recurse' # reCurse
# agent_id = 2843387

player_name = 'aelyanne' # Aelyanne
agent_id = 2697232 # Aelyanne, simpler bot, top of gold league, only try to reach the next waypoint

input_path = f'downloads/{player_name}/{agent_id}'
output_path = f'parsed/{player_name}/{agent_id}'

if not os.path.exists(output_path):
    os.makedirs(output_path)

files = glob.glob(f'{input_path}/*_vs_*.json')

# files = files[:1]

print(f'Found {len(files)} games')

from dataclasses import dataclass
from typing import List

@dataclass
class Point:
    x: int
    y: int

@dataclass
class Pod:
    id: int
    position: Point
    speed: Point
    angle: float
    waypoint: Point
    total_waypoints: int
    team_is_first: int
    pod_is_first: int

@dataclass
class Action:
    aim: Point
    power: int

@dataclass
class Frame:
    pods: List[Pod]
    actions: List[Action]

frames = []

def dist(a: Point, b: Point):
    return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)

last_waypoints = [-1, -1, -1, -1]
total_waypoints = [0, 0, 0, 0]

def parse_pod(pod_id, line):
    t = line.strip().split(' ')
    # print(t)
    position = Point(int(float(t[0])), int(float(t[1])))
    speed = Point(int(t[2]), int(t[3]))
    angle = float(t[8])
    waypoint_index = int(t[10])
    rank = int(t[11])
    if waypoint_index != last_waypoints[pod_id]:
        # we detected the pod just cleared a waypoint!
        total_waypoints[pod_id] = total_waypoints[pod_id] + 1
        last_waypoints[pod_id] = waypoint_index
    waypoint = waypoints[waypoint_index]
    pod = Pod(pod_id, position, speed, angle, waypoint, total_waypoints[pod_id], -1, -1)
    return pod

def parse_action(line):
    t = line.strip().split(' ')
    aim = Point(int(t[0]), int(t[1]))
    power = t[2]
    if not power.isdigit():
        return None
    action = Action(aim, int(power))
    return action


for idx, file in enumerate(files):
    f = open(file, 'r')
    game = json.load(f)

    game_id = game['gameId']

    # Find the id and index of our target agent 
    agent = next(x for x in game['agents'] if x['codingamer']['pseudo'].lower() == player_name.lower())
    agent_id = agent['agentId']
    agent_index = agent['index']

    print(f'> Game {game_id} {player_name} is agent index {agent_index}')

    # Find the waypoints
    waypoints = []
    for line in game['refereeInput'].split('\n'):
        if line.startswith('map='):
            map = line[4:].split(' ')
            for c in range(0, len(map), 2):                
                waypoints.append(Point(int(map[c]), int(map[c+1])))
    print(waypoints)

    view, next_view = (None, None)
    for turn_id in range(1+2, len(game['frames']), 2):
        frame = game['frames'][turn_id]
        keyframe = game['frames'][turn_id+1]
        viewkeyframe = game['frames'][turn_id-1]

        # Quick validation - we assume frames comes in a specific order: 
        if frame['agentId'] != 0:
            print('Expected frame with agent_id 0')
        if keyframe['agentId'] != 1:
            print('Expected keyframe with agent_id 1')
        if frame['keyframe'] == True:
            print('Did not expect keyframe')
        if keyframe['keyframe'] == False:
            print('Expected keyframe')

        stdout = frame['stdout'] if agent_index == 0 else keyframe['stdout']

        lines = viewkeyframe['view'].split('\n')
        turn_id = int(int(lines[0]) / 2)

        pods = []
        pods.append(parse_pod(0, lines[1]))
        pods.append(parse_pod(1, lines[3]))
        pods.append(parse_pod(2, lines[5]))
        pods.append(parse_pod(3, lines[7]))
        timeout = lines[9] # TODO: Add to inputs
        
        lines = stdout.split('\n')
        actions = []
        actions.append(parse_action(lines[0]))
        actions.append(parse_action(lines[1]))

        if actions[0] == None or actions[1] == None:
            # Skip frame for now (used BOOST or SHIELD)
            continue

        # Adding new features: team_is_first and pod_is_first
        first = min(pods, key=lambda p: p.total_waypoints * -100000 + dist(p.position, p.waypoint))
        for pod in pods:
            target_player_pods = (0, 1) if pod.id in (0, 1) else (2, 3)
            pod.team_is_first = 1 if first.id in target_player_pods else 0
            pod.pod_is_first = 1 if first.id == pod.id else 0

        frames.append(Frame(pods, actions))

        # print(frames)

    f.close()

print('Writing frames to disk...')

output_file = f'{output_path}/frames_{player_name}_{agent_id}.csv'

fp = open(output_file, 'w', encoding = 'utf-8')

cols = [
    'p1x', 'p1y', 'p1sx', 'p1sy', 'p1a', 'p1wx', 'p1wy', 'tf1', 'pf1',
    'p2x', 'p2y', 'p2sx', 'p2sy', 'p2a', 'p2wx', 'p2wy', 'tf2', 'pf2',
    'p3x', 'p3y', 'p3sx', 'p3sy', 'p3a', 'p3wx', 'p3wy', 'tf3', 'pf3',
    'p4x', 'p4y', 'p4sx', 'p4sy', 'p4a', 'p4wx', 'p4wy', 'tf4', 'pf4',
    'p1tx', 'p1ty', 'p1t',
    'p2tx', 'p2ty', 'p2t']
fp.write(','.join([str(c) for c in cols]))
fp.write('\n')

for frame in frames:
    data = []
    [data.append(v) for i in range(4) for v in [
        frame.pods[i].position.x,
        frame.pods[i].position.y,
        frame.pods[i].speed.x,
        frame.pods[i].speed.y,
        frame.pods[i].angle,
        frame.pods[i].waypoint.x,
        frame.pods[i].waypoint.y,
        frame.pods[i].team_is_first,
        frame.pods[i].pod_is_first]]
    [data.append(v) for i in range(2) for v in [
        frame.actions[i].aim.x,
        frame.actions[i].aim.y,
        frame.actions[i].power]]
    # print(data)
    fp.write(','.join([str(v) for v in data]))
    fp.write('\n')

fp.close()

print('Done')