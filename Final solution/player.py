import json
from map import Map
import pickle
from boss import Boss
from npc import Npc

class Player:
    def __init__(self, _data, _map: Map, _boss: Boss, _other_players: list) -> None:
            self.data = _data
            self.map = _map
            self.boss = _boss
            self.other_players =_other_players

    def update(self, new_data, new_map, boss, other_players):
        ''' Updates player atributes'''
        self.data = new_data
        self.map = new_map
        self.boss = boss
        self.other_players = other_players

    def get_position(self):
        return(self.data["q"], self.data["r"])

    def get_health(self):
        return(self.data["health"])

    def get_power(self):
        return(self.data["power"])

    def get_level(self):
        return(self.data["level"])

    def get_score(self):
        return(self.data["score"])

    def get_trapped(self):
        return(self.data["trapped"])

    def get_trap_duration(self):
        return(self.data["trapDuration"])

    def get_max_health(self):
        return (self.get_level() - 1)*300 + 1000

    def create_empty_map(self):
        tiles = self.map.tiles
        empty_map = []
        for i, row in enumerate(tiles):
            new_row = []
            for j, tile in enumerate(row):
                new_row.append(0)
            empty_map.append(new_row)

        return empty_map

    def bfs_path(self, i_start, j_start, i_end, j_end, asteroids=False):
        '''Vrsi BFS pretragu i vraca sledeci potez'''
        visited = self.create_empty_map()
        queue = [[(i_start, j_start)]]

        delta_i = [1, 0, -1, -1, 0, 1]
        delta_j = [1, 1, -1, 0, -1, 0]

        while queue:
            path = queue.pop(0)
            i_cur = path[-1][0]
            j_cur = path[-1][1]

            if visited[i_cur][j_cur] == 0:
                for k in range(len(delta_i)):
                    i_next, j_next = i_cur + delta_i[k], j_cur + delta_j[k]
                    if self.is_valid(i_next, j_next, asteroids) and visited[i_next][j_next] == 0:
                        new_path = list(path)
                        new_path.append((i_next, j_next))
                        queue.append(new_path)
                    if i_next == i_end and j_next == j_end:
                        path.append((i_end, j_end))
                        return path # next move
                visited[i_cur][j_cur] = 1

    def is_valid(self, i, j, asteroids=False):
        # Provera da li su i,j van mape
        if i < 0 or i > 28 or j < 0:
            return False
        if i <= 14 and j > 14 + i:
            return False
        if i > 14 and j > 42 - i:
            return False
        # Provera dal su opasna
        if asteroids:
            if self.map.get_tile_type(i, j) in ["BOSS", "BLACKHOLE"]:
                return False
        else:
            if self.map.get_tile_type(i, j) in ["BOSS", "ASTEROID", "BLACKHOLE"]:
                return False
        return True

    def convert_to_qr(self, i, j):
        '''return q, r'''
        return (j-i, i - 14) if i <= 14 else (j-14, i-14)
    
    def convert_to_ij(self, r, q):
            ''' return i, j '''
            return (r+14, q+r+14) if r<=0 else (r+14 ,q+14)

    def get_asteroids_on_path(self, path):
        asteroids = []
        if path == []:
            return [0]
        for node in path:
            i, j = node
            if self.map.get_tile_type(i, j) == "ASTEROID":
                asteroids.append(self.map.tiles[i][j]['entity']['health'])

        return asteroids

    def bfs(self, i_start, j_start, i_end, j_end):

        path = self.bfs_path(i_start, j_start, i_end, j_end, False)
        path_a = self.bfs_path(i_start, j_start, i_end, j_end, True)

        asteroids = self.get_asteroids_on_path(path_a)

        next_i, next_j = 0, 0
        if len(path) < len(path_a) + sum(asteroids)/self.get_power():
            next_i, next_j = path[1]
        else:
            next_i, next_j = path_a[1]
            if self.map.get_tile_type(next_i, next_j) == "ASTEROID":
                next_q, next_r = self.convert_to_qr(next_i, next_j)
                return {"action":"attack,"+str(next_q)+","+str(next_r)}

        # dodzovanje boss-a ##################################
        next_i, next_j = self.will_boss_attack(next_i, next_j)
        ######################################################

        next_q, next_r = self.convert_to_qr(next_i, next_j)
        turn = {"action":"move," + str(next_q) + "," + str(next_r)}

        return turn

    def will_boss_attack(self, i, j):
        attack_positions, phase = self.boss.boss_next_attack()
        for pos in attack_positions:
            if pos[0] == i and pos[1] == j:
                return i, j - 1
        return i, j

    def dist_from_boss(self, pos):

        boss_pos = self.boss.position
        min_dst = 100
        closest_node = {}
        for node in boss_pos:
            if self.tiles_distance(node, pos) < min_dst:
                min_dst = self.tiles_distance(node, pos)
                closest_node = node

        return min_dst, closest_node

    def get_max_health_dist(self):
        max_health = self.get_max_health()
        if self.get_health() < 0.8 * max_health and self.get_health() > 0.5*max_health:
            return 3
        elif self.get_health() < 0.5*max_health:
            return 5
        else:
            return 0

    def get_max_xp_dist(self):
        return 6 - self.get_level()

    def get_closest_wormhole(self, pos, wormholes):
        min_dst = 100
        for wormhole in wormholes:
            if self.tiles_distance(pos, wormhole) < min_dst:
                min_dst = self.tiles_distance(pos, wormhole)
                closest_wormhole = wormhole
        return closest_wormhole

    def wormhole_logic(self, wormholes, wormhole_tile):
        player_pos = self.get_position()
        player_dist = self.tiles_distance({"q":player_pos[0], "r":player_pos[1]}, wormhole_tile)

        for w in wormholes:
            if w != wormhole_tile and w['id'] == wormhole_tile['id']:
                next_wormhole = w

        min_npc_dist = 100
        for npc in self.other_players:
            if not npc: continue
            npc_dist = self.tiles_distance({"q":npc.get_position()[0], "r":npc.get_position()[1]}, next_wormhole)
            if npc_dist < min_npc_dist:
                min_npc_dist = npc_dist

        if min_npc_dist >= 6 and player_dist < 2:
            return True

        if player_dist < 2 and self.get_health() < 100:
            return True

        return False

    def turn(self):
        '''Vraca serveru sledecu akciju --- SVA LOGIKA JE OVDE'''
        q, r = self.get_position()
        i, j = self.convert_to_ij(r=r, q=q)
        
        dist_boss, node_boss = self.dist_from_boss({"q":self.get_position()[0], "r":self.get_position()[1]})
        if dist_boss <= 3:
            if self.get_health() >= 251:
                return {"action":"attack,"+str(node_boss["q"])+","+str(node_boss["r"])}

        i_end, j_end = 0, 0
        max_xp_dist = self.get_max_xp_dist()
        max_health_dist = self.get_max_health_dist()

        xp_tile = self.map.get_all_tiles_type("EXPERIENCE")[0]
        health_tile = self.map.get_all_tiles_type("HEALTH")[0]
        wormholes = self.map.get_all_tiles_type("WORMHOLE")
        wormhole_tile = self.get_closest_wormhole({"q":self.get_position()[0], "r":self.get_position()[1]}, wormholes)

        skip_to_wormhole = self.wormhole_logic(wormholes, wormhole_tile)
        
        if skip_to_wormhole:
            i_end, j_end = self.convert_to_ij(r=wormhole_tile["r"], q=wormhole_tile["q"])
            turn = self.bfs(i, j, i_end=i_end, j_end=j_end)

            return turn
        else:
            for npc in self.other_players:
                if not npc: continue
                npc_dist = self.tiles_distance({"q":npc.get_position()[0], "r":npc.get_position()[1]}, {"q":self.get_position()[0], "r":self.get_position()[1]})
                if npc_dist <= 4 and npc.get_trap_duration() == 2:
                    i_end, j_end = self.convert_to_ij(q=npc.get_position()[0], r=npc.get_position()[1])
                    turn = self.bfs(i, j, i_end=i_end, j_end=j_end)
                    return turn
                if npc_dist <= 3:
                    return {"action":"attack,"+str(npc.get_position()[0])+","+str(npc.get_position()[1])}
            # ako imamo malo health-a idemo ka njemu
            if self.get_health() < 251:
                i_end, j_end = self.convert_to_ij(health_tile["r"], health_tile["q"])
            # ako smo blizu xp idemo ka njemu
            elif self.tiles_distance({"q":self.get_position()[0], "r":self.get_position()[1]}, health_tile) < max_health_dist:
                i_end, j_end = self.convert_to_ij(health_tile["r"], health_tile["q"])
            # ako smo blizu health idemo ka njemu
            elif self.tiles_distance({"q":self.get_position()[0], "r":self.get_position()[1]}, xp_tile) < max_xp_dist:
                i_end, j_end = self.convert_to_ij(xp_tile["r"], xp_tile["q"])
            else:
                i_end, j_end = self.convert_to_ij(node_boss["r"], node_boss["q"]) # inace idemo ka boss-u

        q, r = self.get_position()
        i, j = self.convert_to_ij(r=r, q=q)
        
        turn = self.bfs(i, j, i_end=i_end, j_end=j_end)
        
        return turn
    
    def tiles_distance(self, a: dict, b: dict) -> float:
        return (abs(a['q'] - b['q']) 
            + abs(a['q'] + a['r'] - b['q'] - b['r'])
            + abs(a['r'] - b['r'])) / 2
            
    def get_zone(self) -> int:
        '''
        Prva: 2-4, Druga 5-10, Treca 11-14
        '''  
        # {'r': 0, 'q': 0}
        q, r = self.get_position()
        dist = self.tiles_distance({'r': 0, 'q': 0}, {'r': r, 'q': q})
        if dist >= 2 and dist <= 4:
            return 1
        if dist >= 5 and dist <= 10:
            return 2
        if dist >= 11 and dist <= 14:
            return 3
        else:
            return None

    def next_move(self):
        zone_5 = [{"q": 5, "r": 0}, {"q": 5, "r": -1}, {"q": 5, "r": -2}, {"q": 5, "r": -3}, {"q": 5, "r": -4},
                  {"q": 5, "r": -5}, {"q": 4, "r": -5}, {"q": 3, "r": -5}, {"q": 2, "r": -5},
                  {"q": 1, "r": -5}, {"q": 0, "r": -5}, {"q": -1, "r": -4}, {"q": -2, "r": -3}, {"q": -3, "r": -2},
                  {"q": -4, "r": -1}, {"q": -5, "r": 0}, {"q": -5, "r": 1}, {"q": -5, "r": 2}, {"q": -5, "r": 3},
                  {"q": -5, "r": 4}
            , {"q": -5, "r": 5}, {"q": -4, "r": 5}, {"q": -3, "r": 5}, {"q": -2, "r": 5}, {"q": -1, "r": 5},
                  {"q": 0, "r": 5}, {"q": 1, "r": 4}, {"q": 2, "r": 3}, {"q": 3, "r": 2}, {"q": 4, "r": 1}]

        wormholes = self.map.get_all_tiles_type("WORMHOLE")
        xp = self.map.get_all_tiles_type("EXPERIENCE")
        health = self.map.get_all_tiles_type("HEALTH")
        black_holes = self.map.get_all_tiles_type("BLACKHOLE")

        attack_of_boss = self.boss.boss_next_attack()


        for dic in self.boss.position:
            if (self.tiles_distance(self.data, dic) <= 3):
                return {"action": "attack," + str(dic["q"]) + "," + str(dic["r"])}

        zero_position = {"q": 0, "r": 0}



        if (self.tiles_distance(self.data, zero_position) == 5 and self.get_health() > 500):
            path = self.bfs(*self.convert_to_ij(self.data["r"], self.data["q"]), *self.convert_to_ij(0, 0))
            return path

        if (self.tiles_distance(self.data, zero_position) == 5 and self.get_health() < 100):
            distances = []

            for player in self.other_players:
                if ((self.tiles_distance(self.data, player.data) <= 3) and (self.get_health() >= player.get_health())):
                    return {"action": "attack," + str(player.data["q"]) + "," + str(player.data["r"])}

            for i in range(len(health)):
                if ((health[i]["q"], health[i]["r"]) not in attack_of_boss):
                    distances.append(self.tiles_distance(self.data, health[i]))
                    min = distances[0]
                    j = 0
                    for i in range(1, len(distances)):
                        if (min > distances[i]):
                            j = i
                            min = distances[i]

                    path = self.bfs(*self.convert_to_ij(self.data["r"], self.data["q"]),
                                         *self.convert_to_ij(health[j]["r"], health[j]["q"]))
                    return path

        for player in self.other_players:
            if ((self.tiles_distance(self.data, player.data) <= 4) and (player.get_trap_duration() == 2)):
                path = self.bfs(self.convert_to_ij(self.data["r"], self.data["q"]),
                                     self.convert_to_ij(player.data["r"], player.data["q"]))
                return path

            if (self.tiles_distance(self.data, player.data) <= 3):
                return {"action": "attack," + str(player.data["q"]) +","+ str(player.data["r"])}

            if ((self.tiles_distance(self.data, player.data)) <= 5 and player.get_health() <= self.get_health()):
                if ((player.data["q"], player.data["r"]) not in attack_of_boss):
                    path = self.bfs(*self.convert_to_ij(self.data["r"], self.data["q"]),
                                         *self.convert_to_ij(player.data["r"], player.data["q"]))
                    return path

        # proveravanje za wormhole
        flag = 0
        for i in range(len(wormholes)):
            dic = {"q": wormholes[i]["q"], "r": wormholes[i]["r"]}
            if (self.tiles_distance(self.data, dic) <= 2):
                for j in range(i + 1, len(wormholes)):
                    if (wormholes[i]["id"] == wormholes[j]["id"]):
                        for k in zone_5:
                            dic1 = {"q": wormholes[j]["q"], "r": wormholes[j]["r"]}
                            if ((self.tiles_distance(dic1, zone_5) <= 3) and (
                                    (dic1["q"], dic1["r"]) not in attack_of_boss)):
                                flag = 1
                                break
                    if (flag):
                        path = self.bfs(*self.convert_to_ij(self.data["r"], self.data["q"]),
                                             *self.convert_to_ij(wormholes[i]["r"], wormholes[i]["q"]))
                        return path

        distances = []
        for i in range(len(zone_5)):
            distances.append(self.tiles_distance(self.data, zone_5[i]))
        min_distance = distances[0]
        min_idx = 0
        for i in range(1, len(distances)):
            if (min_distance > distances[i]):
                min_idx = i
                min_distance = distances[i]

        print('START', self.convert_to_ij(self.data["r"], self.data["q"]))
        print('END', self.convert_to_ij(zone_5[min_idx]["r"], zone_5[min_idx]["q"]))
        path = self.bfs(*self.convert_to_ij(self.data["r"], self.data["q"]),
                             *self.convert_to_ij(zone_5[min_idx]["r"], zone_5[min_idx]["q"]))
        return path



if __name__ == "__main__":
    with open('game_state.json', 'r') as f:
        game_state = json.load(f)
    with open('map.json', 'r') as f:
        map_data = json.load(f)
    map = Map(map_data)
    player = Player(game_state['gameState']['player1'], map)
    print(player.bfs_path(0, 0, 0, 5))
