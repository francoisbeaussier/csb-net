import glob
import os
import json
import subprocess
import math
from dataclasses import dataclass

player_name = 'reCurse' # reCurse
agent_id = 2843387

input_path = f'converted/{player_name}/{agent_id}'
output_path = f'extracted/{player_name}/{agent_id}'
if not os.path.exists(output_path):
    os.makedirs(output_path)

from collections import namedtuple
# Point = namedtuple('Point', 'x y')
# Pod = namedtuple('Pod', 'id position speed angle waypoint total_waypoints team_is_first pod_is_first')
Action = namedtuple('Action', 'aim power')
Frame = namedtuple('Frame', 'pods actions')

@dataclass
class Point:
    x: int
    y: int

@dataclass
class Pod:
    id: int
    position: Point
    speed: Point
    angle: int
    waypoint: Point
    total_waypoints: int
    team_is_first: int
    pod_is_first: int

frames = []

def dist(a: Point, b: Point):
    return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)

def extract_frames(filepath, player_name):
    with open(filepath) as fp:
        for i in range(2):
            line = fp.readline()
            tokens = line.strip().split(' ')
            # print(tokens)
            if tokens[2].lower() == player_name.lower():
                target_player_index = int(tokens[1])
                print(f'Found target player {player_name} at index {target_player_index}')

        line = fp.readline()
        tokens = line.strip().split(' ')
        waypoints = []
        for waypoint_index in range(int(tokens[1])):
            line = fp.readline()
            tokens = line.strip().split(' ')
            # print(tokens)
            waypoints.append(Point(int(tokens[1]), int(tokens[2])))
            
        read_turns(fp, waypoints, target_player_index)

def read_turns(fp, waypoints, target_player_index):
    last_waypoints = [0, 0, 0, 0]
    total_waypoints = [0, 0, 0, 0]
    while True:
        for player_index in range(2):
            pods = []
            for pod_id in range(4):
                line = fp.readline()
                if not line:
                    return
                if player_index != target_player_index:
                    continue
                t = line.strip().split(' ')
                # print(t)
                position = Point(int(t[1]), int(t[2]))
                speed = Point(int(t[3]), int(t[4]))
                angle = int(t[5])
                waypoint_index = int(t[6])
                if waypoint_index != last_waypoints[pod_id]:
                   # we detected the pod just cleared a waypoint!
                   total_waypoints[pod_id] = total_waypoints[pod_id] + 1
                   last_waypoints[pod_id] = waypoint_index
                waypoint = waypoints[waypoint_index]
                pod = Pod(pod_id, position, speed, angle, waypoint, total_waypoints[pod_id], -1, -1)
                # print(pod)
                pods.append(pod)

            actions = []
            skip = False
            for podId in range(2):
                line = fp.readline()
                if not line:
                    return
                t = line.strip().split(' ')
                aim = Point(int(t[1]), int(t[2]))
                power = t[3]
                if not power.isdigit():
                    # power = int(power)
                    skip = True
                else:
                    action = Action(aim, int(power))
                    # print(action)
                    actions.append(action)
            if player_index == target_player_index and not skip:
                # Keep track of the leading team and pod
                # This is very likely to be a useful feature
                first = min(pods, key=lambda p: p.total_waypoints * -100000 + dist(p.position, p.waypoint))
                # if pods[0].position.x == 12140:
                #     print(f'First pod is ', first)
                for pod in pods:
                    target_player_pods = (0, 1) if pod.id in (0, 1) else (2, 3)
                    pod.team_is_first = 1 if first.id in target_player_pods else 0
                    pod.pod_is_first = 1 if first.id == pod.id else 0
                    # if pods[0].position.x == 12140:
                    #     print(f'pod[{pod.id}] ', pod.team_is_first, pod.pod_is_first)
                frames.append(Frame(pods, actions))

files = glob.glob(f'{input_path}/*.txt')

# files = files[:1]

print(f'Found {len(files)} converted games')

# extract

for idx, file in enumerate(files):
    extract_frames(file, player_name)

# write output
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