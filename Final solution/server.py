import requests
import json

import player
import map
import npc
import time
import boss

# Funkcija koja igra igru

SERVER_IP = "http://aibg2022.com:"
username = "Hiperparametri1"
password = "#@YyRQt3Fk"

login_data = {
    'username': username,
    'password': password
}

class Server:
    '''
    Atributi:
    * token
    * join_game
    * Player player
    * NPC npcs
    * Map map
    * Boss boss
    '''
    def __init__(self) -> None:
        '''
        * player_id: id pocetne pozicije 
        * time - trajanje igre u minutima
        '''
        self.__game_init__()
        try:
            start_action = json.loads(self.join_game.json()['gameState'])  # formatiranje
        except KeyError:
            print('Start action potez nije uspeo')
            print(self.join_game.json())


        # TODO: Inicijalizuj mapu, Playera itd.... smisleno za pravu igru
        #print(start_action)
        self.map = map.Map(start_action['map'])
        self.npc = {str(idx): npc.Npc({}) for idx in self.npc_ids}
        other_players = [p for p in self.npc.values()]
        self.boss = boss.Boss(start_action['boss'])
        self.player = player.Player(start_action[f'player{self.player_id}'], self.map, self.boss, other_players)
        print(self.player.get_position())
        for idx, p in self.npc.items():
            p.update(start_action[f'player{idx}'])


    def __game_init__(self):
        # Inicijalizacija igre
        token = requests.post(url =  SERVER_IP+"8081"+"/user/login",json = login_data).json()
        self.token_header = {
            'Authorization' : 'Bearer ' + token["token"]
        }
        self.join_game = requests.get(url =SERVER_IP +"8081" +"/game/joinGame", headers = self.token_header) # json = g_params
        print(self.join_game.json())
        self.player_id = self.join_game.json()['playerIdx']  # TODO: promeni za pravu igru
        self.npc_ids = [i for i in range(1, 5) if i != self.player_id]

    def get_state(self) -> None:
        turn = self.player.turn()
        print(self.player.get_position())
        print(turn)
    
        new_state_r = requests.post(url =SERVER_IP + "8081"+"/game/doAction", headers = self.token_header, json = turn)
        
        try:
            new_state = json.loads(new_state_r.json()['gameState'])  # formatiranje
        except KeyError:
            print('Potez nije uspeo')
            print(new_state_r.json())
        # Update mape, playera, NPCa i Boss-a
        self.map.update(new_state['map'])
        other_players = [p for p in self.npc.values()]
        self.player.update(new_state[f'player{self.player_id}'], self.map, self.boss, other_players)
        for idx, p in self.npc.items():
            p.update(new_state[f'player{idx}'])
        self.boss.update_boss(new_state['boss'])


    def play_game(self):
        while (True):
            self.get_state()
            print(self.boss.boss_next_attack())

if __name__ == "__main__":

    server = Server()
    server.play_game()