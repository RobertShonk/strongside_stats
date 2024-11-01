from time import sleep

import requests

import main.constants as constants

headers = {
    'User-Agent': 'Mozilla/5.0 (platform; rv:gecko-version) Gecko/gecko-trail Firefox/firefox-version'
}

ACCOUNT_URL = 'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id'
SUMMONER_URL = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid'
LEAGUE_URL = 'https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner'
MATCH_ID_URL = 'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid'
MATCH_URL = 'https://americas.api.riotgames.com/lol/match/v5/matches'

# define functions here that will replace logic in site.stats so it is 'cleaner.'


def get_account(summoner_name, tagline):
    url = f'{ACCOUNT_URL}/{summoner_name}/{tagline}?api_key={constants.RIOT_API_KEY}'

    req = requests.get(url, headers=headers)

    if req.status_code == 200:
        return req.json(), req.status_code
    
    return None, req.status_code


def get_summoner(puuid):
    url = f'{SUMMONER_URL}/{puuid}?api_key={constants.RIOT_API_KEY}'

    req = requests.get(url, headers)

    if req.status_code == 200:
        return req.json(), req.status_code
    
    return None, req.status_code

# use get_account and get_summoner here to get player id for league url
def get_league(summoner_name, tagline):
    account = get_account(summoner_name, tagline)
    status_code = account[1]

    if account[1] == 200:
        summoner = get_summoner(account[0]['puuid'])
        status_code = summoner[1]

        if summoner[1] == 200:
            url = f'{LEAGUE_URL}/{summoner[0]['id']}?api_key={constants.RIOT_API_KEY}'
            req = requests.get(url, headers=headers)

            if req.status_code == 200:
                return req.json(), req.status_code
    
    return None, status_code


def get_match_ids(summoner_name, tagline):
    account = get_account(summoner_name, tagline)

    if account[1] == 200:
        puuid = account[0]['puuid']
        url = f'{MATCH_ID_URL}/{puuid}/ids?start=0&count=20&api_key={constants.RIOT_API_KEY}'

        req = requests.get(url, headers=headers)

        if req.status_code == 200:
            return req.json(), req.status_code
    
    return None, req.status_code


def get_match(match_id):
    url = f'{MATCH_URL}/{match_id}?api_key={constants.RIOT_API_KEY}'

    req = requests.get(url, headers=headers)

    if req.status_code == 200:
        return req.json(), req.status_code
    
    return None, req.status_code


# mind the riot api rate limit
def get_matches(summoner_name, tagline):
    match_ids = get_match_ids(summoner_name, tagline)

    matches = []
    if match_ids[1] == 200:
        # get matches
        for id in match_ids[0]:
            matches.append(get_match(id))
        
        return matches

    return None