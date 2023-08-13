import json

class Npc:
    def __init__(self, npc) -> None:
        self.data = npc

    def update(self, npc):
        self.data = npc

    def get_position(self):
        if not self.data:
            return None
        return(self.data["q"], self.data["r"])

    def get_health(self):
        if not self.data:
            return None
        return(self.data["health"])

    def get_power(self):
        if not self.data:
            return None
        return(self.data["power"])

    def get_level(self):
        if not self.data:
            return None
        return(self.data["level"])

    def get_score(self):
        if not self.data:
            return None
        return(self.data["score"])

    def get_trapped(self):
        if not self.data:
            return None
        return(self.data["trapped"])

    def get_trap_duration(self):
        if not self.data:
            return None
        return(self.data["trapDuration"])