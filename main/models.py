class Match:
    def __init__(self, metadata, participants, summoner_name):
        self.game_mode = metadata['gameMode']
        self.date_played = metadata['gameCreation']
        self.game_duration = metadata['gameDuration']
        #self.player = [p for p in participants if p['riotIdGameName'] == summoner_name]
        for p in participants:
            if p['riotIdGameName'].lower() == summoner_name.lower():
                self.player = p

        self.participants = participants

    def get_kda_ratio(self):
        return round(((self.player['kills'] + self.player['assists']) / self.player['deaths']), 1)