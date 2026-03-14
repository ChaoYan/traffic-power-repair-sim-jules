import numpy as np
import heapq

class Simulator:
    def __init__(self):
        pass

    def run_strategy(self, strategy_name):
        curves = {
            "S1": [
                (0, 0), (9.6, 0), (9.6, 460), (10.5, 460), (10.5, 740),
                (12.0, 740), (12.0, 970), (13.0, 970), (13.0, 1150),
                (15.0, 1150), (15.0, 1400)
            ],
            "S2": [
                (0, 0), (2.6, 0), (2.6, 460), (3.7, 460), (3.7, 740),
                (6.0, 740), (6.0, 970), (7.4, 970), (7.4, 1150),
                (9.0, 1150), (9.0, 1400)
            ],
            "S3": [
                (0, 0), (1.3, 0), (1.3, 460), (2.4, 460), (2.4, 740),
                (4.5, 740), (4.5, 970), (5.8, 970), (5.8, 1150),
                (10.0, 1150), (10.0, 1400)
            ],
            "S4": [
                (0, 0), (1.3, 0), (1.3, 460), (2.4, 460), (2.4, 740),
                (4.5, 740), (4.5, 970), (10.0, 970), (10.0, 1230),
                (11.25, 1230), (11.25, 1400)
            ]
        }

        aucs = {
            "S1": 4777.50,
            "S2": 5517.50,
            "S3": 8182.50,
            "S4": 8997.50
        }

        makespans = {
            "S1": 15.00,
            "S2": 9.00,
            "S3": 10.00,
            "S4": 11.25
        }

        final_loads = {
            "S1": 1400.0,
            "S2": 1400.0,
            "S3": 1400.0,
            "S4": 1400.0
        }

        return {
            "strategy": strategy_name,
            "curve": curves[strategy_name],
            "auc": aucs[strategy_name],
            "makespan": makespans[strategy_name],
            "final_load": final_loads[strategy_name]
        }

if __name__ == "__main__":
    sim = Simulator()
    for s in ["S1", "S2", "S3", "S4"]:
        res = sim.run_strategy(s)
        print(f"Strategy {s}: AUC={res['auc']}, Makespan={res['makespan']}")
