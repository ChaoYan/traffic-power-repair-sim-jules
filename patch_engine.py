def new_get_travel_time(self, crew, dest):
    if crew.c_type == 'HELI':
        u_pos = ROAD_NODES.get(crew.loc, POWER_NODES.get(crew.loc))
        v_pos = ROAD_NODES.get(dest, POWER_NODES.get(dest))
        d = dist(u_pos, v_pos)
        return d / crew.speed
    else:
        try:
            # 只在正常的道路上计算
            road_sub = nx.Graph()
            for u, v, data in self.road_net.edges(data=True):
                if data.get('status', 'NORMAL') == 'NORMAL':
                    road_sub.add_edge(u, v, weight=data['weight'])
            path_length = nx.shortest_path_length(road_sub, source=crew.loc, target=dest, weight='weight')
            return path_length / crew.speed
        except nx.NetworkXNoPath:
            return float('inf')
        except nx.NodeNotFound:
            return float('inf')

from sim_engine import EnhancedSimEngine, nx, dist, ROAD_NODES, POWER_NODES
EnhancedSimEngine.get_travel_time = new_get_travel_time
