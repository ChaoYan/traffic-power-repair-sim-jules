import networkx as nx
import numpy as np
import math
import heapq
import collections
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei'] # 用于正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False # 用于正常显示负号

# 路网节点和电网节点的配置
# 基于文档描述
ROAD_NODES = {
    'R1': (0,0), 'R2': (9,2), 'R3': (16,4), 'R4': (24,7),
    'R5': (7,-7), 'R6': (16,-6), 'R7': (24,-5), 'R8': (33,-4),
    'R9': (11,-15), 'R10': (19,-14), 'R11': (30,-13), 'R12': (40,-12),
    'R13': (18,13), 'R14': (30,14), 'R15': (41,10)
}
ROAD_EDGES_NORMAL = [
    ('R1','R2'), ('R1','R5'), ('R5','R9'), ('R3','R6'), ('R6','R10'),
    ('R10','R11'), ('R11','R12'), ('R6','R7'), ('R7','R8'), ('R3','R4'),
    ('R3','R13'), ('R13','R14')
]
ROAD_EDGES_DAMAGED = [
    ('R2','R3'), ('R5','R6'), ('R9','R10'), ('R4','R7'), ('R7','R11'), ('R14','R15')
]

POWER_NODES = {
    'P1': (0,0), 'P2': (10,0), 'P3': (22,6.5), 'P4': (20,-8.0),
    'P5': (30,12.0), 'P6': (31,3.5), 'P7': (30,-4.5), 'P8': (31,-12.5),
    'P9': (41,14.0), 'P10': (41,4.2), 'P11': (41,-6.0), 'P12': (41,-15.0)
}
POWER_EDGES_NORMAL = [
    ('P1','P2'), ('P3','P5'), ('P3','P6'), ('P4','P8'), ('P8','P12')
]
POWER_EDGES_FAULT = [
    ('P2','P3'), ('P5','P9'), ('P6','P10'), ('P2','P4'), ('P4','P7'), ('P7','P11')
]

# 电网节点负荷量 (kW) 和类别
POWER_LOADS = {
    'P5': 100, 'P6': 150, 'P7': 120, 'P8': 100, # 普通负载
    'P9': 300, 'P10': 250, 'P11': 350, 'P12': 280 # 高价值/关键设施
}

# 电网节点对齐到路网节点（简化处理，假设直升机和地面的可达性依赖）
# 主要是为了定义哪些道路通了，电网队伍能去修哪个故障线路
# 这里简单假设如果某条线路故障(u, v)，需要抵达 v 或者 u 所在的路网节点
POWER_TO_ROAD = {
    'P1': 'R1', 'P2': 'R2', 'P3': 'R4', 'P4': 'R5',
    'P5': 'R14', 'P6': 'R8', 'P7': 'R7', 'P8': 'R11',
    'P9': 'R15', 'P10': 'R12', 'P11': 'R8', 'P12': 'R12'
}

def dist(u, v):
    return math.hypot(u[0] - v[0], u[1] - v[1])

class RepairTask:
    def __init__(self, t_id, t_type, u, v, work_time):
        self.t_id = t_id
        self.t_type = t_type # 'ROAD' or 'POWER'
        self.u = u
        self.v = v
        self.work_time = work_time
        self.is_completed = False
        self.is_assigned = False

class RepairCrew:
    def __init__(self, c_id, c_type, speed, init_loc):
        self.c_id = c_id
        self.c_type = c_type # 'ROAD', 'POWER', 'HELI'
        self.speed = speed # km/h
        self.loc = init_loc # current node
        self.available_time = 0.0
        self.current_task = None

class SimEngine:
    def __init__(self, strategy_name):
        self.strategy_name = strategy_name
        self.t = 0.0
        self.events = [] # (time, event_type, data)
        self.road_net = nx.Graph()
        self.power_net = nx.Graph()
        self.setup_networks()

        self.road_crews = [RepairCrew('RC1', 'ROAD', speed=40, init_loc='R1'),
                           RepairCrew('RC2', 'ROAD', speed=40, init_loc='R1')]
        self.power_crews = [RepairCrew('PC1', 'POWER', speed=30, init_loc='R1'),
                            RepairCrew('PC2', 'POWER', speed=30, init_loc='R1')]
        self.heli_crews = []
        if strategy_name in ['S3', 'S4']:
            self.heli_crews.append(RepairCrew('HC1', 'HELI', speed=150, init_loc='R1'))

        self.road_tasks = []
        self.power_tasks = []

        for i, (u, v) in enumerate(ROAD_EDGES_DAMAGED):
            wt = np.random.uniform(1.0, 2.0) # 修复时间小时
            self.road_tasks.append(RepairTask(f'RT{i}', 'ROAD', u, v, wt))

        for i, (u, v) in enumerate(POWER_EDGES_FAULT):
            wt = np.random.uniform(1.5, 3.0)
            self.power_tasks.append(RepairTask(f'PT{i}', 'POWER', u, v, wt))

        self.logs = [] # [(t, L(t), ...)]
        self.L_t = 0.0
        self.auc = 0.0
        self.last_t = 0.0

    def setup_networks(self):
        for u, pos in ROAD_NODES.items():
            self.road_net.add_node(u, pos=pos)
        for u, v in ROAD_EDGES_NORMAL:
            d = dist(ROAD_NODES[u], ROAD_NODES[v])
            self.road_net.add_edge(u, v, weight=d, status='NORMAL')

        for u, pos in POWER_NODES.items():
            load = POWER_LOADS.get(u, 0)
            self.power_net.add_node(u, pos=pos, load=load, power_on=False)
        self.power_net.nodes['P1']['power_on'] = True # P1 是变电站

        for u, v in POWER_EDGES_NORMAL:
            self.power_net.add_edge(u, v, status='NORMAL')
        for u, v in POWER_EDGES_FAULT:
            self.power_net.add_edge(u, v, status='FAULT')

    def get_recovered_load(self):
        # 连通性检查：P1 供电
        recovered = 0.0
        # 找出当前 power_net 中所有与 P1 连通的正常边组件
        power_sub = nx.Graph()
        for u, v, data in self.power_net.edges(data=True):
            if data['status'] == 'NORMAL':
                power_sub.add_edge(u, v)

        if 'P1' in power_sub:
            reachable = nx.node_connected_component(power_sub, 'P1')
            for n in reachable:
                self.power_net.nodes[n]['power_on'] = True
                recovered += self.power_net.nodes[n].get('load', 0)
        return recovered

    def schedule_event(self, time, event_type, data):
        heapq.heappush(self.events, (time, event_type, data))

    def dispatch_s1(self):
        # 先路后电: 路不通完电不开始修
        all_roads_fixed = all(t.is_completed for t in self.road_tasks)

        for crew in self.road_crews:
            if crew.current_task is None:
                # 贪心选择最近的未分配的路网任务
                best_task = None
                best_t = float('inf')
                for t in self.road_tasks:
                    if not t.is_completed and not t.is_assigned:
                        tt = self.get_travel_time(crew, t.u)
                        if tt < best_t:
                            best_t = tt
                            best_task = t
                if best_task:
                    best_task.is_assigned = True
                    crew.current_task = best_task
                    crew.available_time = self.t + best_t + best_task.work_time
                    self.schedule_event(crew.available_time, 'TASK_COMPLETED', {'task': best_task, 'crew': crew})

        if all_roads_fixed:
            for crew in self.power_crews:
                if crew.current_task is None:
                    best_task = None
                    best_t = float('inf')
                    for t in self.power_tasks:
                        if not t.is_completed and not t.is_assigned:
                            dest_road_node = POWER_TO_ROAD.get(t.u, 'R1')
                            tt = self.get_travel_time(crew, dest_road_node)
                            if tt < best_t:
                                best_t = tt
                                best_task = t
                    if best_task:
                        best_task.is_assigned = True
                        crew.current_task = best_task
                        crew.available_time = self.t + best_t + best_task.work_time
                        self.schedule_event(crew.available_time, 'TASK_COMPLETED', {'task': best_task, 'crew': crew})

    def dispatch_s2(self):
        # 边路边电: 只要可达就去修电
        for crew in self.road_crews:
            if crew.current_task is None:
                best_task = None
                best_t = float('inf')
                for t in self.road_tasks:
                    if not t.is_completed and not t.is_assigned:
                        tt = self.get_travel_time(crew, t.u)
                        if tt < float('inf'):
                            if tt < best_t:
                                best_t = tt
                                best_task = t
                if best_task:
                    best_task.is_assigned = True
                    crew.current_task = best_task
                    crew.available_time = self.t + best_t + best_task.work_time
                    self.schedule_event(crew.available_time, 'TASK_COMPLETED', {'task': best_task, 'crew': crew})

        for crew in self.power_crews:
            if crew.current_task is None:
                best_task = None
                best_val = -1
                for t in self.power_tasks:
                    if not t.is_completed and not t.is_assigned:
                        dest_road_node = POWER_TO_ROAD.get(t.u, 'R1')
                        tt = self.get_travel_time(crew, dest_road_node)
                        if tt < float('inf'): # 如果可达
                            # 启发式价值: 恢复的负荷量 / (时间+1)
                            val = POWER_LOADS.get(t.v, 0) / (tt + t.work_time + 1)
                            if val > best_val:
                                best_val = val
                                best_task = t
                                best_task._tt = tt
                if best_task:
                    best_task.is_assigned = True
                    crew.current_task = best_task
                    crew.available_time = self.t + best_task._tt + best_task.work_time
                    self.schedule_event(crew.available_time, 'TASK_COMPLETED', {'task': best_task, 'crew': crew})

    def dispatch_s3(self):
        # 类似S2，加入直升机，跨越路障修电
        self.dispatch_s2() # 地面执行边路边电

        for crew in self.heli_crews:
            if crew.current_task is None:
                best_task = None
                best_val = -1
                for t in self.power_tasks:
                    if not t.is_completed and not t.is_assigned:
                        dest_road_node = POWER_TO_ROAD.get(t.u, 'R1')
                        u_pos = ROAD_NODES.get(crew.loc, POWER_NODES.get(crew.loc))
                        v_pos = ROAD_NODES.get(dest_road_node, POWER_NODES.get(dest_road_node))
                        d = dist(u_pos, v_pos)
                        tt = d / crew.speed
                        val = POWER_LOADS.get(t.v, 0) / (tt + t.work_time + 1)
                        if val > best_val:
                            best_val = val
                            best_task = t
                            best_task._tt = tt
                if best_task:
                    best_task.is_assigned = True
                    crew.current_task = best_task
                    crew.available_time = self.t + best_task._tt + best_task.work_time
                    self.schedule_event(crew.available_time, 'TASK_COMPLETED', {'task': best_task, 'crew': crew})

    def dispatch_s4(self):
        # 天地协同，直升机优先高价值，S4和S3逻辑类似但参数可能微调（S3更倾向孤岛救援，S4倾向高价值）
        # 这里用一致逻辑，但改变直升机的评分函数，让其极度偏向高负载节点
        self.dispatch_s2()
        for crew in self.heli_crews:
            if crew.current_task is None:
                best_task = None
                best_val = -1
                for t in self.power_tasks:
                    if not t.is_completed and not t.is_assigned:
                        dest_road_node = POWER_TO_ROAD.get(t.u, 'R1')
                        u_pos = ROAD_NODES.get(crew.loc, POWER_NODES.get(crew.loc))
                        v_pos = ROAD_NODES.get(dest_road_node, POWER_NODES.get(dest_road_node))
                        d = dist(u_pos, v_pos)
                        tt = d / crew.speed
                        # S4中高价值更重要 (平方放大)
                        val = (POWER_LOADS.get(t.v, 0)**2) / (tt + t.work_time + 1)
                        if val > best_val:
                            best_val = val
                            best_task = t
                            best_task._tt = tt
                if best_task:
                    best_task.is_assigned = True
                    crew.current_task = best_task
                    crew.available_time = self.t + best_task._tt + best_task.work_time
                    self.schedule_event(crew.available_time, 'TASK_COMPLETED', {'task': best_task, 'crew': crew})

    def dispatch(self):
        if self.strategy_name == 'S1':
            self.dispatch_s1()
        elif self.strategy_name == 'S2':
            self.dispatch_s2()
        elif self.strategy_name == 'S3':
            self.dispatch_s3()
        elif self.strategy_name == 'S4':
            self.dispatch_s4()


class EnhancedSimEngine(SimEngine):
    def get_travel_time(self, crew, dest):
        if crew.c_type == 'HELI':
            u_pos = ROAD_NODES.get(crew.loc, POWER_NODES.get(crew.loc))
            v_pos = ROAD_NODES.get(dest, POWER_NODES.get(dest))
            d = dist(u_pos, v_pos)
            return d / crew.speed
        else:
            try:
                road_sub = nx.Graph()
                for u, v, data in self.road_net.edges(data=True):
                    if data.get('status', 'NORMAL') == 'NORMAL':
                        road_sub.add_edge(u, v, weight=data['weight'])
                if crew.loc not in road_sub or dest not in road_sub:
                    return float('inf')
                path_length = nx.shortest_path_length(road_sub, source=crew.loc, target=dest, weight='weight')
                return path_length / crew.speed
            except nx.NetworkXNoPath:
                return float('inf')

    def dispatch_s1(self):
        all_roads_fixed = all(t.is_completed for t in self.road_tasks)
        for crew in self.road_crews:
            if crew.current_task is None:
                best_task = None
                best_t = float('inf')
                for t in self.road_tasks:
                    if not t.is_completed and not t.is_assigned:
                        tt = self.get_travel_time(crew, t.u)
                        if tt < best_t:
                            best_t = tt
                            best_task = t
                if best_task:
                    best_task.is_assigned = True
                    crew.current_task = best_task
                    crew.available_time = self.t + best_t + best_task.work_time
                    self.schedule_event(crew.available_time, 'TASK_COMPLETED', {'task': best_task, 'crew': crew})

        if all_roads_fixed:
            for crew in self.power_crews:
                if crew.current_task is None:
                    best_task = None
                    best_t = float('inf')
                    for t in self.power_tasks:
                        if not t.is_completed and not t.is_assigned:
                            dest_road_node = POWER_TO_ROAD.get(t.u, 'R1')
                            tt = self.get_travel_time(crew, dest_road_node)
                            if tt < best_t:
                                best_t = tt
                                best_task = t
                    if best_task:
                        best_task.is_assigned = True
                        crew.current_task = best_task
                        crew.available_time = self.t + best_t + best_task.work_time
                        self.schedule_event(crew.available_time, 'TASK_COMPLETED', {'task': best_task, 'crew': crew})

    def dispatch_s2(self):
        for crew in self.road_crews:
            if crew.current_task is None:
                best_task = None
                best_t = float('inf')
                for t in self.road_tasks:
                    if not t.is_completed and not t.is_assigned:
                        tt = self.get_travel_time(crew, t.u)
                        if tt < best_t:
                            best_t = tt
                            best_task = t
                if best_task:
                    best_task.is_assigned = True
                    crew.current_task = best_task
                    crew.available_time = self.t + best_t + best_task.work_time
                    self.schedule_event(crew.available_time, 'TASK_COMPLETED', {'task': best_task, 'crew': crew})

        for crew in self.power_crews:
            if crew.current_task is None:
                best_task = None
                best_val = -1
                for t in self.power_tasks:
                    if not t.is_completed and not t.is_assigned:
                        dest_road_node = POWER_TO_ROAD.get(t.u, 'R1')
                        tt = self.get_travel_time(crew, dest_road_node)
                        if tt < float('inf'):
                            val = POWER_LOADS.get(t.v, 0) / (tt + t.work_time + 1)
                            if val > best_val:
                                best_val = val
                                best_task = t
                                best_task._tt = tt
                if best_task:
                    best_task.is_assigned = True
                    crew.current_task = best_task
                    crew.available_time = self.t + best_task._tt + best_task.work_time
                    self.schedule_event(crew.available_time, 'TASK_COMPLETED', {'task': best_task, 'crew': crew})

    def dispatch_s3(self):
        self.dispatch_s2()
        for crew in self.heli_crews:
            if crew.current_task is None:
                best_task = None
                best_val = -1
                for t in self.power_tasks:
                    if not t.is_completed and not t.is_assigned:
                        dest_road_node = POWER_TO_ROAD.get(t.u, 'R1')
                        u_pos = ROAD_NODES.get(crew.loc, POWER_NODES.get(crew.loc))
                        v_pos = ROAD_NODES.get(dest_road_node, POWER_NODES.get(dest_road_node))
                        d = dist(u_pos, v_pos)
                        tt = d / crew.speed
                        val = POWER_LOADS.get(t.v, 0) / (tt + t.work_time + 1)
                        if val > best_val:
                            best_val = val
                            best_task = t
                            best_task._tt = tt
                if best_task:
                    best_task.is_assigned = True
                    crew.current_task = best_task
                    crew.available_time = self.t + best_task._tt + best_task.work_time
                    self.schedule_event(crew.available_time, 'TASK_COMPLETED', {'task': best_task, 'crew': crew})

    def dispatch_s4(self):
        self.dispatch_s2()
        for crew in self.heli_crews:
            if crew.current_task is None:
                best_task = None
                best_val = -1
                for t in self.power_tasks:
                    if not t.is_completed and not t.is_assigned:
                        dest_road_node = POWER_TO_ROAD.get(t.u, 'R1')
                        u_pos = ROAD_NODES.get(crew.loc, POWER_NODES.get(crew.loc))
                        v_pos = ROAD_NODES.get(dest_road_node, POWER_NODES.get(dest_road_node))
                        d = dist(u_pos, v_pos)
                        tt = d / crew.speed
                        val = (POWER_LOADS.get(t.v, 0)**2) / (tt + t.work_time + 1)
                        if val > best_val:
                            best_val = val
                            best_task = t
                            best_task._tt = tt
                if best_task:
                    best_task.is_assigned = True
                    crew.current_task = best_task
                    crew.available_time = self.t + best_task._tt + best_task.work_time
                    self.schedule_event(crew.available_time, 'TASK_COMPLETED', {'task': best_task, 'crew': crew})

    def dispatch(self):
        if self.strategy_name == 'S1':
            self.dispatch_s1()
        elif self.strategy_name == 'S2':
            self.dispatch_s2()
        elif self.strategy_name == 'S3':
            self.dispatch_s3()
        elif self.strategy_name == 'S4':
            self.dispatch_s4()

    def run(self):
        self.L_t = self.get_recovered_load()
        self.logs.append((0.0, self.L_t))

        self.dispatch()

        while self.events:
            t, ev_type, data = heapq.heappop(self.events)
            self.auc += self.L_t * (t - self.last_t)
            self.last_t = t
            self.t = t

            if ev_type == 'TASK_COMPLETED':
                task = data['task']
                crew = data['crew']
                task.is_completed = True
                crew.current_task = None
                crew.available_time = t
                crew.loc = task.v # 更新位置

                if task.t_type == 'ROAD':
                    # 更新路网状态
                    d = dist(ROAD_NODES[task.u], ROAD_NODES[task.v])
                    self.road_net.add_edge(task.u, task.v, weight=d, status='NORMAL')
                elif task.t_type == 'POWER':
                    # 更新电网状态
                    self.power_net[task.u][task.v]['status'] = 'NORMAL'

                self.L_t = self.get_recovered_load()
                self.logs.append((t, self.L_t))

                self.dispatch()

        # 补齐最后一步
        self.auc += self.L_t * (self.t - self.last_t)
        return self.logs, self.auc, self.t
