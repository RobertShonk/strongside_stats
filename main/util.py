import time

from main.db import get_db

# leagues will be a list, one for each queueType (solo/duo, flex, etc)
# could potentially be empty list which would mean the player has no current season ranked data at all
def insert_leagues(leagues, summoner_name, tagline, profileIconId, summonerLevel):

    if len(leagues) > 0:
        db = get_db()

        for league in leagues:
            db_league = db.execute(
                'SELECT * FROM league WHERE summonerId = ? AND queueType = ?',
                (league['summonerId'], league['queueType'])
            ).fetchone()

            if db_league:
                db.execute(
                    """
                    UPDATE league
                        SET tier = ?, rank = ?, leaguePoints = ?, wins = ?, losses = ?, veteran = ?, inactive = ?, freshBlood = ?, hotStreak = ?, profileIconId = ?, summonerLevel = ?
                        WHERE id = ?
                    """,
                    (league['tier'], league['rank'], league['leaguePoints'], league['wins'], league['losses'], league['veteran'], league['inactive'], league['freshBlood'], league['hotStreak'], profileIconId, summonerLevel, db_league['id'])
                )
                db.commit()
            
            if db_league is None:
                db.execute(
                    """
                    INSERT INTO league (leagueId, queueType, tier, rank, summonerId, leaguePoints, wins, losses, veteran, inactive, freshBlood, hotStreak, summoner_name, tagline, profileIconId, summonerLevel) 
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (league['leagueId'], league['queueType'], league['tier'], league['rank'], league['summonerId'], league['leaguePoints'], league['wins'], league['losses'],
                     league['veteran'], league['inactive'], league['freshBlood'], league['hotStreak'], summoner_name, tagline, profileIconId, summonerLevel)
                )
                db.commit()
        
        return 202
    
    return 500

# matches will be a list of match dictionaries. 
# check if match metadata exists first.
#   if match metadata by matchId does exists, then DO NOT insert participants
#   if metadata does not exist, add the 10 participants data
# need to insert match metadata and each participant for each match.
def insert_matches(matches):
    db = get_db()

    for match in matches:
        match = match[0]
        db_metadata = db.execute('SELECT matchId FROM metadata WHERE matchId = ?', (match['metadata']['matchId'],)).fetchone()

        if db_metadata is None:

            db.execute(
                """
                INSERT INTO metadata (dataVersion, matchId, endOfGameResult, gameCreation, gameDuration, gameEndTimestamp, gameId, gameMode, gameName, gameStartTimestamp, gameType, gameVersion, mapId, platformId, queueId)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (match['metadata']['dataVersion'], match['metadata']['matchId'], match['info']['endOfGameResult'], match['info']['gameCreation'], match['info']['gameDuration'],
                 match['info']['gameEndTimestamp'], match['info']['gameId'], match['info']['gameMode'], match['info']['gameName'], match['info']['gameStartTimestamp'],
                 match['info']['gameType'], match['info']['gameVersion'], match['info']['mapId'], match['info']['platformId'], match['info']['queueId'])
            )
            db.commit()
            print(match['metadata']['matchId'])
            # insert each participant
            # get metadata_id that we just inserted
            many_participants = []
            metadata_id = db.execute('SELECT id FROM metadata WHERE matchId = ?', (match['metadata']['matchId'],)).fetchone()
            participants = match['info']['participants']
            for part in participants:
                if len(part.keys()) == 133: # makes sure that data will be same size as table.
                    many_participants.append(partic_ins_data(part, metadata_id['id']))

            db.executemany(create_partic_insert(), many_participants)
            db.commit()
               
        


# functions to generate sql insert statements (mostly for participant table as it has a lot of columns).
def create_partic_insert():
    db = get_db()
    res = db.execute('SELECT * FROM participant').description

    col_names = []
    for i in range(1, len(res)):
        col_names.append(res[i][0])

    str_names = ','.join(col_names)
    str_names = f'({str_names})'
    ins1 = 'INSERT INTO participant'
    ins_stmt = f'{ins1} {str_names} VALUES'

    q_marks = ''

    for i in range(1, len(res)):
        if i == len(res)-1:
            q_marks = q_marks + '?'
        else:
            q_marks = q_marks + '?,'

    q_marks = f'({q_marks})'

    return f'{ins_stmt} {q_marks}'


def partic_ins_data(participant, metadata_id):
    data = [metadata_id]

    for key in participant:
        if not isinstance(participant[key], dict):
            data.append(participant[key])

    # minor_rune_defense, minor_rune_flex, minor_rune_offense, primary_main_rune, primary_rune1, primary_rune2, primary_rune3, secondary_main_rune, secondary_rune1, secondary_rune2
    data.append(participant['perks']['statPerks']['defense'])
    data.append(participant['perks']['statPerks']['flex'])
    data.append(participant['perks']['statPerks']['offense'])
    data.append(participant['perks']['styles'][0]['style'])
    data.append(participant['perks']['styles'][0]['selections'][0]['perk'])
    data.append(participant['perks']['styles'][0]['selections'][1]['perk'])
    data.append(participant['perks']['styles'][0]['selections'][2]['perk'])
    data.append(participant['perks']['styles'][1]['style'])
    data.append(participant['perks']['styles'][1]['selections'][0]['perk'])
    data.append(participant['perks']['styles'][1]['selections'][1]['perk']) 

    return data