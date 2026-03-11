from sim_engine import EnhancedSimEngine
import matplotlib.pyplot as plt
import wandb
import os

# Font fix for chinese
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

def run_experiment():
    wandb.login(key=os.environ.get("WANDB_API_KEY", "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"))
    wandb.init(project="traffic-power-repair-sim", name="heuristic-strategies-eval")

    strategies = ['S1', 'S2', 'S3', 'S4']
    results = {}

    for s in strategies:
        engine = EnhancedSimEngine(s)
        logs, auc, makespan = engine.run()
        results[s] = {'logs': logs, 'auc': auc, 'makespan': makespan}

        # log to wandb
        wandb.log({
            f"{s}_auc": auc,
            f"{s}_makespan": makespan
        })

    # 可视化
    plt.figure(figsize=(10, 6))
    for s in strategies:
        logs = results[s]['logs']
        t_vals = [l[0] for l in logs]
        L_vals = [l[1] for l in logs]
        plt.step(t_vals, L_vals, where='post', label=f'{s} (AUC: {results[s]["auc"]:.1f})', linewidth=2)

    plt.xlabel('Time (h)')
    plt.ylabel('Recovered Load L(t) (kW)')
    plt.title('LSD Curve Comparison')
    plt.legend()
    plt.grid(True)
    plt.savefig('lsd_curve.png', dpi=300)
    plt.close()

    plt.figure(figsize=(8, 5))
    s_names = list(results.keys())
    aucs = [results[s]['auc'] for s in s_names]
    bars = plt.bar(s_names, aucs, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 50, f'{yval:.0f}', ha='center', va='bottom')
    plt.xlabel('Strategy')
    plt.ylabel('Accumulated Recovery AUC')
    plt.title('AUC Comparison')
    plt.savefig('auc_bar.png', dpi=300)
    plt.close()

    plt.figure(figsize=(8, 5))
    makespans = [results[s]['makespan'] for s in s_names]
    bars = plt.bar(s_names, makespans, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.2, f'{yval:.1f}h', ha='center', va='bottom')
    plt.xlabel('Strategy')
    plt.ylabel('Makespan (h)')
    plt.title('Makespan Comparison')
    plt.savefig('makespan_bar.png', dpi=300)
    plt.close()

    wandb.log({
        "lsd_curve": wandb.Image('lsd_curve.png'),
        "auc_bar": wandb.Image('auc_bar.png'),
        "makespan_bar": wandb.Image('makespan_bar.png')
    })

    wandb.finish()
    return results

if __name__ == '__main__':
    run_experiment()
