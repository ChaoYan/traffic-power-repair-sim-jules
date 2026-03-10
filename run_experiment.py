import os
import wandb
from simulator import Simulator

os.environ["WANDB_API_KEY"] = "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"

def run_experiment():
    sim = Simulator()
    strategies = ["S1", "S2", "S3", "S4"]

    for strategy in strategies:
        run = wandb.init(
            project="traffic-power-repair-sim",
            name=f"strategy_{strategy}",
            config={"strategy": strategy},
            reinit=True
        )

        res = sim.run_strategy(strategy)

        curve = res["curve"]
        for time_pt, load in curve:
            wandb.log({"time": time_pt, "load_restored": load})

        wandb.log({
            "AUC": res["auc"],
            "Makespan": res["makespan"],
            "Final_Load": res["final_load"]
        })

        run.finish()

if __name__ == "__main__":
    run_experiment()
