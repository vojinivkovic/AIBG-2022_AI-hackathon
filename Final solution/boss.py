import json
import pickle

class Boss:

    def __init__(self, data):

        self.data = data
        self.position = [{"q":0, "r":0}, {"q":0, "r":-1}, {"q":1, "r":-1}, {"q":-1, "r":0}, {"q":1, "r":0}, {"q":-1, "r":1}, {"q":0, "r":1}]

        self.state_pattern = [0, 0] # NAJBITNIJI DEO: state_pattern[0] oznacava tip paterna (0 - pauza, 1 - pattern1, 2 - pattern2)
                                    #state_pattern[1] oznacava fazu paterna
    def update_boss(self, data):
        self.data = data

        if (len(self.data["bossAttackedTiles"]) == 8):
            for dic in self.data["bossAttackedTiles"]:

                if((dic["q"] == 8) and (dic["r"] == -2)):
                    self.state_pattern = [1, 0]
                    break

                if ((dic["q"] == 8) and (dic["r"] == -4)):
                    self.state_pattern = [1, 1]
                    break

                if((dic["q"] == 8) and (dic["r"] == -6)):
                    self.state_pattern = [1, 2]
                    break
        elif (len(self.data["bossAttackedTiles"]) == 0):
            self.state_pattern[0] = 0
            self.state_pattern[1] += 1
        else:
            for dic in self.data["bossAttackedTiles"]:
                if ((dic["q"] == 6) and (dic["r"] == 0)):
                    self.state_pattern = [2, 0]
                    break

                if((dic["q"] == 8) and (dic["r"] == 0)):
                    self.state_pattern = [2, 1]
                    break

                if((dic["q"] == 10) and (dic["r"] == 0)):
                    self.state_pattern = [2, 2]
                    break

    def boss_next_attack(self):
        if (self.state_pattern == [1, 0]):
            return [(8, -4), (8, -5), (4, 4), (3, 5), (-3, -5), (-4, -4), (-8, 4), (-8, 5)], 0

        if (self.state_pattern == [1, 1]):
            return [(8, -6), (8, -7), (2, 6), (1, 7), (-1, -7), (-2, -6), (-8, 6), (-8, 7)], 0

        if (self.state_pattern == [1, 2]):
            self.state_pattern = [0, 0]

        index = []

        if(self.state_pattern == [2, 0]):
            for j in range(0, -9, -1):
                index.append((8, j))
            for j in range(7, -1, -1):
                index.append((j, -8))
            for j in range(0, 9):
                index.append((-8, j))
            for j in range(-7, 1):
                index.append((8, j))

            for i in range(-8, 8):
                for j in range(-8, 8):
                    if ((abs(i) + abs(j) == 8) and ((i < 0 and j < 0) or (i > 0 and j > 0) and (abs(i) != 8))):
                        index.append((i, j))
            
        elif(self.state_pattern == [2, 1]):
            for j in range(0, -11, -1):
                index.append((10, j))
            for j in range(9, -1, -1):
                index.append((j, -10))
            for j in range(0, 11):
                index.append((-10, j))
            for j in range(-9, 1):
                index.append((10, j))

            for i in range(-10, 10):
                for j in range(-10, 10):
                    if ((abs(i) + abs(j) == 10) and ((i < 0 and j < 0) or (i > 0 and j > 0) and (abs(i) != 10))):
                        index.append((i, j))

        elif(self.state_pattern == [2, 2]):
            for j in range(0, -7, -1):
                index.append((6, j))
            for j in range(5, -1, -1):
                index.append((j, -6))
            for j in range(0, 7):
                index.append((-6, j))
            for j in range(-5, 1):
                index.append((6, j))

            for i in range(-6, 6):
                for j in range(-6, 6):
                    if ((abs(i) + abs(j) == 6) and ((i < 0 and j < 0) or (i > 0 and j > 0) and (abs(i) != 6))):
                        index.append((i, j))

        return index, self.state_pattern[1] # dokle smo stigli sa pauzom


if __name__ == "__main__":

    with open('generated_game_state.pkl', 'rb') as f:
        game_state = pickle.load(f)
        game_state = json.loads(game_state['gameState'])
        game_state = {'gameState': game_state}


        boss = game_state["gameState"]["boss"]
        print(boss)
        boss1 = Boss(boss)
