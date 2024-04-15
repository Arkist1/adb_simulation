import json
import numpy as np
import matplotlib.pyplot as plt

classes = ['EntitySpawn', 'AgentDetection', 'EntityDeath', 'EntityPositionUpdate', 'EnemyDetection', 'EnemyChangeState', 'AgentHealthUpdate']
graphs = {cls: [(0,0)] for cls in classes}
counts = {cls: 0 for cls in classes}

with open("log.json", 'r') as f:
    data = json.load(f)
    
    for event in data:
        cls = event["class"]
        counts[cls] += 1
        graphs[cls].append((event["ticks"], counts[cls]))
        last_tick = event["ticks"]
        
    for cls in classes:
        graphs[cls].append((last_tick, graphs[cls][-1][1]))
        
    plt.plot(*np.array(graphs["EntitySpawn"]).T, drawstyle="steps-post", label="EntitySpawn")
    plt.plot(*np.array(graphs["EntityDeath"]).T, drawstyle="steps-post", label="EntityDeath")
    plt.plot(*np.array(graphs["EntityPositionUpdate"]).T, drawstyle="steps-post", label="EntityPositionUpdate")
    plt.plot(*np.array(graphs["EnemyChangeState"]).T, drawstyle="steps-post", label="EnemyChangeState")
    plt.xlabel("ticks")
    plt.ylabel("count")
    plt.grid(color='black', linestyle='-', linewidth=0.2)
    plt.legend()
    plt.show()
    
    
    plt.plot(*np.array(graphs["AgentDetection"]).T, drawstyle="steps-post", label="AgentDetection")
    plt.plot(*np.array(graphs["EnemyDetection"]).T, drawstyle="steps-post", label="EnemyDetection")
    plt.xlabel("ticks")
    plt.ylabel("count")
    plt.grid(color='black', linestyle='-', linewidth=0.2)
    plt.legend()
    plt.show()
    