import torch
import os
from env import TransitEnv
from dqn_agent import DQNAgent

# 1. Setup paths
SUMO_CFG = "../sumo_files/simulation.sumocfg"
MODEL_PATH = "../models/dqn_model.pth"

# 2. Initialize Environment
# Set GUI=True in your env.py start() if you want to watch it!
env = TransitEnv(SUMO_CFG)

# 3. Initialize Agent
state_dim = 112
action_dim = 27
agent = DQNAgent(state_dim=state_dim, action_dim=action_dim)

# 4. Load the Trained Weights
if os.path.exists(MODEL_PATH):
    agent.policy_net.load_state_dict(torch.load(MODEL_PATH))
    agent.epsilon = 0.0  # Force agent to use learned policy only
    print(f"Successfully loaded model from {MODEL_PATH}")
else:
    print("Model file not found!")
    exit()

# 5. Run Evaluation Loop
env.start() # Change to env.start(gui=True) in env.py to watch
state = env.reset()
done = False
total_reward = 0

print("Running Evaluation Simulation...")
while not done:
    action = agent.select_action(state)
    state, reward, done = env.step(action)
    total_reward += reward

print(f"Evaluation Complete. Total Reward: {total_reward:.3f}")
env.close()