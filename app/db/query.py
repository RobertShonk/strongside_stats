import time

from .db import get_db


def get_summoner(game_name, tag_line):
    db = get_db()

    summoner = db.execute(
        "SELECT * FROM summoner WHERE game_name LIKE ? AND tag_line LIKE ?",
        (game_name, tag_line,)
    ).fetchone()

    if summoner is None:
        return "404"
    
    return dict(summoner)


def insert_summoner(account, summoner, league):
    db = get_db()

    solo_tier, solo_rank, solo_league_points, solo_wins, solo_losses = None, None, None, None, None
    flex_tier, flex_rank, flex_league_points, flex_wins, flex_losses = None, None, None, None, None

    for leg in league:
        if leg['queueType'] == 'RANKED_SOLO_5x5':
            solo_tier = leg['tier']
            solo_rank = leg['rank']
            solo_league_points = leg['leaguePoints']
            solo_wins = leg['wins']
            solo_losses = leg['losses']
        elif leg['queueType'] == 'RANKED_FLEX_SR':
            flex_tier = leg['tier']
            flex_rank = leg['rank']
            flex_league_points = leg['leaguePoints']
            flex_wins = leg['wins']
            flex_losses = leg['losses']

    # check db for existing summoner
    check_summoner = db.execute(
        "SELECT id FROM summoner WHERE game_name LIKE ? AND tag_line LIKE ?",
        (account['gameName'], account['tagLine'])
    ).fetchone()

    # if no summoner (None) then insert, else update.
    if check_summoner is None:
        db.execute(
            "INSERT INTO summoner"
            " (game_name, tag_line, profile_icon_id, summoner_level, solo_tier, solo_rank, solo_league_points, solo_wins, solo_losses,"
            " flex_tier, flex_rank, flex_league_points, flex_wins, flex_losses, last_update) VALUES"
            " (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (account['gameName'], account['tagLine'], summoner['profileIconId'], summoner['summonerLevel'],
            solo_tier, solo_rank,  solo_league_points, solo_wins, solo_losses,
            flex_tier, flex_rank, flex_league_points, flex_wins, flex_losses,
            current_milli_time())
        )
        db.commit()
        return "201"
    else:
        db.execute(
            "UPDATE summoner SET"
            " profile_icon_id = ?, summoner_level = ?, solo_tier = ?, solo_rank = ?, solo_league_points = ?, solo_wins = ?, solo_losses = ?,"
            " flex_tier = ?, flex_rank = ?, flex_league_points = ?, flex_wins = ?, flex_losses = ?, last_update = ?"
            " WHERE game_name LIKE ? AND tag_line LIKE ?",
            (summoner['profileIconId'], summoner['summonerLevel'],
            solo_tier, solo_rank,  solo_league_points, solo_wins, solo_losses,
            flex_tier, flex_rank, flex_league_points, flex_wins, flex_losses,
            current_milli_time(), account['gameName'], account['tagLine'])
        )
        db.commit()
        return "200"


def get_matches_by_game_name(game_name, tag_line):
    db = get_db()

    match_ids = db.execute(
        "SELECT match_id FROM participant WHERE riot_id_game_name LIKE ? AND riot_id_tag_line LIKE ? LIMIT 20",
        (game_name, tag_line,)
    ).fetchall()

    matches = []

    for id in match_ids:
        match = db.execute(
            "SELECT match_table.*, participant.* FROM match_table"
            " INNER JOIN participant ON match_table.id = participant.match_id"
            " WHERE match_table.id = ?",
            (id[0],)
        ).fetchall()

        matches.append(match)
 
    return matches


def insert_match(match):
    db = get_db()

    db.execute(
        "INSERT OR IGNORE INTO match_table"
        " (match_id, end_of_game_result, game_creation, game_duration, game_end_timestamp, game_id, game_mode, game_name,"
        " game_start_timestamp, game_type, game_version, map_id, platform_id, queue_id)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (match['metadata']['matchId'], match['info']['endOfGameResult'], match['info']['gameCreation'], match['info']['gameDuration'],
        match['info']['gameEndTimestamp'], match['info']['gameId'], match['info']['gameMode'], match['info']['gameName'],
        match['info']['gameStartTimestamp'], match['info']['gameType'], match['info']['gameVersion'], match['info']['mapId'],
        match['info']['platformId'], match['info']['queueId'])
    )
    db.commit()

    return "201"


# takes in a list of matches and inserts them all into the db via db.executemany().
def insert_matches(matches):
    db = get_db()

    # need to loop through matches and create lists of relevant data for each row.
    match_data = []

    for match in matches:
        match_data.append(
            (match['metadata']['matchId'], match['info']['endOfGameResult'], match['info']['gameCreation'], match['info']['gameDuration'],
             match['info']['gameEndTimestamp'], match['info']['gameId'], match['info']['gameMode'], match['info']['gameName'],
             match['info']['gameStartTimestamp'], match['info']['gameType'], match['info']['gameVersion'], match['info']['mapId'],
             match['info']['platformId'], match['info']['queueId'])
        )

    db.executemany(
        "INSERT OR IGNORE INTO match_table"
        " (match_id, end_of_game_result, game_creation, game_duration, game_end_timestamp, game_id, game_mode, game_name,"
        " game_start_timestamp, game_type, game_version, map_id, platform_id, queue_id)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        match_data
    )
    db.commit()

    return "201"


# participants = list of participants from one match
# match_id: used to check the list of 10 participants for match exists or not
def insert_participants(participants, match_id):
    db = get_db()

    # match_id in match_table looks like "NA12345".
    match_PK = db.execute(
        "SELECT id FROM match_table WHERE match_id = ?",
        (match_id,)
    ).fetchone()

    # match_id in participant is FK to match_table from participants.
    check_participants = db.execute(
        "SELECT id FROM participant WHERE match_id = ?",
        (match_PK[0],)
    ).fetchall()

    print(match_PK['id'])
    if len(check_participants) < 10:
        parts = []
        for p in participants:
            parts.append(
                (p['assists'], p['baronKills'], p['bountyLevel'], p['champExperience'], p['champLevel'], p['championId'], p['championName'],
                p['consumablesPurchased'], p['damageDealtToBuildings'], p['damageDealtToObjectives'], p['damageDealtToTurrets'],
                p['damageSelfMitigated'], p['deaths'], p['detectorWardsPlaced'], p['doubleKills'], p['dragonKills'], p['firstBloodAssist'],
                p['firstBloodKill'], p['firstTowerAssist'], p['firstTowerKill'], p['gameEndedInSurrender'], p['goldEarned'], p['goldSpent'],
                p['individualPosition'], p['inhibitorKills'], p['inhibitorTakedowns'], p['inhibitorsLost'], p['item0'], p['item1'],
                p['item2'], p['item3'], p['item4'], p['item5'], p['item6'], p['itemsPurchased'], p['kills'], p['lane'], p['largestCriticalStrike'],
                p['largestKillingSpree'], p['largestMultiKill'], p['longestTimeSpentLiving'], p['magicDamageDealt'], p['magicDamageDealtToChampions'],
                p['magicDamageTaken'], p['neutralMinionsKilled'], p['objectivesStolen'], p['objectivesStolenAssists'], p['pentaKills'],
                p['physicalDamageDealt'], p['physicalDamageDealtToChampions'], p['physicalDamageTaken'], p['profileIcon'], p['puuid'], p['quadraKills'],
                p['riotIdGameName'], p['riotIdTagline'], p['role'], p['sightWardsBoughtInGame'], p['spell1Casts'], p['spell2Casts'], p['spell3Casts'],
                p['spell4Casts'], p['summoner1Casts'], p['summoner1Id'], p['summoner2Casts'], p['summoner2Id'], p['summonerId'], p['summonerLevel'],
                p['teamId'], p['timeCCingOthers'], p['timePlayed'], p['totalAllyJungleMinionsKilled'], p['totalDamageDealt'], p['totalDamageDealtToChampions'],
                p['totalDamageShieldedOnTeammates'], p['totalDamageTaken'], p['totalEnemyJungleMinionsKilled'], p['totalHeal'], p['totalHealsOnTeammates'],
                p['totalMinionsKilled'], p['totalTimeCCDealt'], p['totalTimeSpentDead'], p['totalUnitsHealed'], p['tripleKills'], p['trueDamageDealt'],
                p['trueDamageDealtToChampions'], p['trueDamageTaken'], p['turretKills'], p['turretTakedowns'], p['turretsLost'], p['unrealKills'],
                p['visionScore'], p['visionWardsBoughtInGame'], p['wardsKilled'], p['wardsPlaced'], p['win'], p['perks']['statPerks']['defense'],
                p['perks']['statPerks']['flex'], p['perks']['statPerks']['offense'], p['perks']['styles'][0]['style'], p['perks']['styles'][1]['style'],
                match_PK[0])
            )

        db.executemany(
            "INSERT INTO participant"
            " (assists, baron_kills, bounty_level, champ_experience, champ_level, champion_id, champion_name, consumables_purchased,"
            " damage_dealt_to_buildings, damage_dealt_to_objectives, damage_dealt_to_turrets, damage_self_mitigated, deaths,"
            " detector_wards_placed, double_kills, dragon_kills, first_blood_assist, first_blood_kill, first_tower_assist, first_tower_kill,"
            " game_ended_in_surrender, gold_earned, gold_spent, individual_position, inhibitor_kills, inhibitor_takedowns, inhibitors_lost,"
            " item0, item1, item2, item3, item4, item5, item6, items_purchased, kills, lane, largest_critical_strike, largest_killing_spree,"
            " largest_multi_kill, longest_time_spent_living, magic_damage_dealt, magic_damage_dealt_to_champions, magic_damage_taken,"
            " neutral_minions_killed, objectives_stolen, objectives_stolen_assists, penta_kills, physical_damage_dealt,"
            " physical_damage_dealt_to_champions, physical_damage_taken, profile_icon, puuid, quadra_kills, riot_id_game_name, riot_id_tag_line,"
            " player_role, sight_wards_bought_in_game, spell1_casts, spell2_casts, spell3_casts, spell4_casts, summoner1_casts, summoner1_id,"
            " summoner2_casts, summoner2_id, summoner_id, summoner_level, team_id, time_CCing_others, time_played, total_ally_jungle_minions_killed,"
            " total_damage_dealt, total_damage_dealt_to_champions, total_damage_shielded_on_teammates, total_damage_taken,"
            " total_enemy_jungle_minions_killed, total_heal, total_heals_on_teammates, total_minions_killed, total_time_CC_dealt, total_time_spent_dead,"
            " total_units_healed, triple_kills, true_damage_dealt, true_damage_dealt_to_champions, true_damage_taken, turret_kills, turret_takedowns,"
            " turrets_lost, unreal_kills, vision_score, vision_wards_bought_in_game, wards_killed, wards_placed, win, defense_perk, flex_perk, offense_perk,"
            " primary_style_perk, sub_style_perk, match_id)"
            " VALUES"
            " (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,"
            " ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            parts
        )
        db.commit()
        
        return "200"
    
    return "did not insert participants"

def current_milli_time():
    return round(time.time() * 1000)