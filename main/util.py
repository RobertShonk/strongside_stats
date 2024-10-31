import time

from main.db import get_db

# data will be a list, one for each queueType (solo/duo, flex, etc)
# could potentially be empty list which would mean the player has no current season ranked data at all
def insert_leagues(leagues, summoner_name, tagline):

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
                        SET tier = ?, rank = ?, leaguePoints = ?, wins = ?, losses = ?, veteran = ?, inactive = ?, freshBlood = ?, hotStreak = ?
                        WHERE id = ?
                    """,
                    (league['tier'], league['rank'], league['leaguePoints'], league['wins'], league['losses'], league['veteran'], league['inactive'], league['freshBlood'], league['hotStreak'], db_league['id'])
                )
                db.commit()
            
            if db_league is None:
                db.execute(
                    """
                    INSERT INTO league (leagueId, queueType, tier, rank, summonerId, leaguePoints, wins, losses, veteran, inactive, freshBlood, hotStreak, summoner_name, tagline) 
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (league['leagueId'], league['queueType'], league['tier'], league['rank'], league['summonerId'], league['leaguePoints'], league['wins'], league['losses'],
                     league['veteran'], league['inactive'], league['freshBlood'], league['hotStreak'], summoner_name, tagline)
                )
                db.commit()
        
        return 202
    
    return 500