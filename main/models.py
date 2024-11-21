class Match:
    def __init__(self, metadata, participants, summoner_name):
        self.game_mode = metadata['gameMode']
        self.date_played = metadata['gameCreation']
        self.game_duration = metadata['gameDuration']

        for p in participants:
            if p['riotIdGameName'].lower() == summoner_name.lower():
                self.player = p

        self.participants = participants

        self.match_type = 'Other'
        if metadata['queueId'] == 420:
            self.match_type = 'Solo/Duo'
        elif metadata['queueId'] == 430 or metadata['queueId'] == 400:
            self.match_type = 'Normal'
        elif metadata['queueId'] == 440:
            self.match_type = 'Flex'
        elif metadata['queueId'] == 450:
            self.match_type = 'ARAM'
        

    def get_kda_ratio(self):
        if self.player['deaths'] == 0:
            return 'Perfect'

        return round(((self.player['kills'] + self.player['assists']) / self.player['deaths']), 1)
    
    def get_cs_per_min(self):
        minutes = self.game_duration // 60
        seconds = (self.game_duration % 60) / 60
        min = minutes + seconds # duration of game in terms of only minutes.

        total_cs = self.player['totalMinionsKilled'] + self.player['totalAllyJungleMinionsKilled'] + self.player['totalEnemyJungleMinionsKilled']
        cs_pm = round(total_cs/min, 1)

        return cs_pm
    
    def get_most_damage(self):
        top_damage = 0
        for part in self.participants:
            if part['totalDamageDealtToChampions'] > top_damage:
                top_damage = part['totalDamageDealtToChampions']
        return top_damage
    
    def get_most_damage_taken(self):
        top_taken = 0
        for part in self.participants:
            if part['totalDamageTaken'] > top_taken:
                top_taken = part['totaldamageTaken']
        return top_taken
    
    def get_highest_csm(self):
        highest_csm = 0
        for part in self.participants:
            minutes = self.game_duration // 60
            seconds = (self.game_duration % 60) / 60
            min = minutes + seconds
            total_cs = part['totalMinionsKilled'] + part['totalAllyJungleMinionsKilled'] + part['totalEnemyJungleMinionsKilled']
            csm = round(total_cs/min, 1)
            if csm > highest_csm:
                highest_csm = csm
        return highest_csm
    
    def create_chart_data(self):
        # total damage done, total damage taken, cs/m for player
        # also want to use most damage done/taken and highest cs/m to plot the ratios
        #   (total damage)/(most damage), (total taken)/(most taken), and (cs/m)/(highest cs/m)
        # then plot with range [0,1].
        tot_dmg = self.player['totalDamageDealtToChampions']
        tot_taken = self.player['totalDamageTaken']
        csm = self.get_cs_per_min()

        dmg_ratio = tot_dmg / self.get_most_damage()
        taken_ratio = tot_taken / self.get_most_damage_taken()
        csm_ratio = csm / self.get_highest_csm()

        return [dmg_ratio, taken_ratio, csm_ratio]