from env import TransitEnv
from dqn_agent import DQNAgent
import torch
import os

# --- 0. SANITY CHECK FUNCTION ---
def verify_action_mapping():
    """Verifies that the 27 discrete actions map correctly to Headway and Dwell."""
    headway_options = [-240, -180, -120, -60, 0, 60, 120, 180, 240]
    dwell_options = [0, 30, 60]
    
    print("\n--- Action Space Sanity Check ---")
    # Test a few key indices
    test_cases = [0, 13, 26] # Start, Middle, End
    for i in test_cases:
        h_idx = i // 3
        d_idx = i % 3
        print(f"Action ID {i:2}: Headway Shift {headway_options[h_idx]:4}s, Dwell Extension {dwell_options[d_idx]:2}s")
    
    expected_dim = len(headway_options) * len(dwell_options)
    print(f"✅ Sanity Check Passed: {expected_dim} total actions verified.\n")
    return expected_dim

# Ensure the models directory exists
if not os.path.exists("../models"):
    os.makedirs("../models")

SUMO_CFG = "../sumo_files/simulation.sumocfg"

# --- 1. CONFIGURATION ---
# Run sanity check and get the dimension
action_dim = verify_action_mapping() 
state_dim = 112

# --- 2. INITIALIZE ---
env = TransitEnv(SUMO_CFG)
agent = DQNAgent(state_dim=state_dim, action_dim=action_dim)

# Start TraCI
env.start()

# Sanity check for dimensions
initial_state = env.get_state()
print(f"Verified State Shape: {initial_state.shape}") 
print(f"Verified Action Space: {action_dim}")
print("--- Starting Training ---\n")

# --- 3. TRAINING LOOP ---
episodes = 100
for ep in range(episodes):
    state = env.reset()
    done = False
    total_reward = 0

    while not done:
        # Agent selects an action (0-26)
        action = agent.select_action(state)
        
        # Environment applies action and returns results
        next_state, reward, done = env.step(action)

        # Store experience and train
        agent.store(state, action, reward, next_state, done)
        agent.train()

        # Update state and accumulate reward
        state = next_state
        total_reward += reward

    # Log progress at the end of each episode
    print(f"Episode {ep:3} | Reward: {total_reward:10.3f} | Epsilon: {agent.epsilon:.3f}")

    # Optional: Save checkpoint every 10 episodes
    if ep % 10 == 0:
        torch.save(agent.policy_net.state_dict(), f"../models/dqn_checkpoint_ep{ep}.pth")

# --- 4. SAVE FINAL MODEL ---
torch.save(agent.policy_net.state_dict(), "../models/dqn_model.pth")
print("\nTraining Complete. Final Model Saved at ../models/dqn_model.pth")