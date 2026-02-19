import matplotlib.pyplot as plt
import re

def plot_rewards(log_file):
    episodes = []
    rewards = []
    
    # Simple regex to pull numbers from your console output format
    # "Episode  76 | Reward:   -168.784"
    with open(log_file, 'r') as f:
        for line in f:
            if "Episode" in line and "Reward" in line:
                parts = line.split('|')
                ep_num = int(re.search(r'\d+', parts[0]).group())
                rew_val = float(re.search(r'[-+]?\d*\.\d+|\d+', parts[1]).group())
                episodes.append(ep_num)
                rewards.append(rew_val)

    plt.figure(figsize=(10, 5))
    plt.plot(episodes, rewards, label='Raw Reward', color='lightblue', alpha=0.5)
    
    # Calculate moving average to see the trend clearly
    if len(rewards) > 10:
        moving_avg = [sum(rewards[max(0, i-10):i+1]) / len(rewards[max(0, i-10):i+1]) for i in range(len(rewards))]
        plt.plot(episodes, moving_avg, label='10-Episode Average', color='blue', linewidth=2)

    plt.title('Training Progress: Reward vs Episode')
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.show()

if __name__ == "__main__":
    # If you didn't save a log file, you can copy-paste your terminal 
    # output into a file named 'train_log.txt'
    try:
        plot_rewards('train_log.txt')
    except FileNotFoundError:
        print("Please save your terminal output to 'train_log.txt' first!")