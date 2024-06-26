import requests

from . import Constants

ACCOUNT = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"
SUMMONER = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/"
LEAGUE = "https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/"
MATCH_LIST = "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/"
MATCH = "https://americas.api.riotgames.com/lol/match/v5/matches/" #use for specific match by match id


def get_account(summonerName, tagLine):
    account_url = ACCOUNT + summonerName + "/" + tagLine + "?api_key=" + Constants.RIOT_API_KEY
    req = requests.get(account_url)
    
    if req.status_code == 200:
        return req.json()
    
    return None
    

def get_summoner(puuid):
    summoner_url = SUMMONER + puuid + "?api_key=" + Constants.RIOT_API_KEY
    req = requests.get(summoner_url)

    if req.status_code == 200:
        return req.json()
    
    return None


def get_league(summoner_id):
    league_url = LEAGUE + summoner_id + "?api_key=" + Constants.RIOT_API_KEY
    req = requests.get(league_url)

    if req.status_code == 200:
        return req.json()
    
    return None

# returns count=20 most recent matches by default.
# stick to 20 for now just to keep an eye on the rate limit.
def get_match_list(puuid):
    match_list_url = MATCH_LIST + puuid + "/ids?start=0&count=20&api_key=" + Constants.RIOT_API_KEY
    req = requests.get(match_list_url)

    if req.status_code == 200:
        return req.json()
    
    return None


def get_match(match_id):
    match_url = MATCH + match_id + "?api_key=" + Constants.RIOT_API_KEY
    req = requests.get(match_url)

    if req.status_code == 200:
        return req.json()
    
    return None