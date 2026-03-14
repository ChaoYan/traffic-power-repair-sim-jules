import matplotlib.pyplot as plt
from simulator import Simulator

def generate_plots():
    sim = Simulator()
    strategies = ["S1", "S2", "S3", "S4"]
    results = {s: sim.run_strategy(s) for s in strategies}

    plt.figure(figsize=(10, 6))
    for s in strategies:
        curve = results[s]["curve"]
        times = [pt[0] for pt in curve]
        loads = [pt[1] for pt in curve]
        plt.step(times, loads, where='post', label=f'{s}  AUC={results[s]["auc"]}', linewidth=2)

    plt.xlabel('Time (h)')
    plt.ylabel('Load Restored (kW)')
    plt.title('Strategy Comparison: Load Restored over Time')
    plt.legend()
    plt.grid(True)
    plt.savefig('lsd_curves.png')
    plt.close()

    plt.figure(figsize=(8, 6))
    aucs = [results[s]["auc"] for s in strategies]
    bars = plt.bar(strategies, aucs, color=['blue', 'orange', 'green', 'red'])
    plt.xlabel('Strategy')
    plt.ylabel('AUC')
    plt.title('AUC Comparison')
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 100, f'{yval}', ha='center', va='bottom')
    plt.grid(axis='y')
    plt.savefig('auc_comparison.png')
    plt.close()

    plt.figure(figsize=(8, 6))
    makespans = [results[s]["makespan"] for s in strategies]
    bars = plt.bar(strategies, makespans, color=['blue', 'orange', 'green', 'red'])
    plt.xlabel('Strategy')
    plt.ylabel('Makespan (h)')
    plt.title('Makespan Comparison')
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.2, f'{yval}', ha='center', va='bottom')
    plt.grid(axis='y')
    plt.savefig('makespan_comparison.png')
    plt.close()

if __name__ == "__main__":
    generate_plots()
