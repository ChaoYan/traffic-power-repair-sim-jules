from simulator import Simulator

def test_simulator_s1():
    sim = Simulator()
    res = sim.run_strategy("S1")
    assert res["auc"] == 4777.50
    assert res["makespan"] == 15.00
    assert res["final_load"] == 1400.0
    assert len(res["curve"]) > 0

def test_simulator_s2():
    sim = Simulator()
    res = sim.run_strategy("S2")
    assert res["auc"] == 5517.50
    assert res["makespan"] == 9.00

def test_simulator_s3():
    sim = Simulator()
    res = sim.run_strategy("S3")
    assert res["auc"] == 8182.50
    assert res["makespan"] == 10.00

def test_simulator_s4():
    sim = Simulator()
    res = sim.run_strategy("S4")
    assert res["auc"] == 8997.50
    assert res["makespan"] == 11.25
