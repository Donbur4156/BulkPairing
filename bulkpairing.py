import requests
import time
import json
import config
import sys

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Iterator, Any

BASE = "https://lichess.org"
CHALLENGE_URL = BASE + "/api/challenge/admin/{}/{}"
BULK_CREATE_API = BASE + "/api/bulk-pairing"
BULK_VIEW = BASE + "/api/bulk-pairing"
BULK_CANCEL = BASE + "/api/bulk-pairing/{}"

TOKEN = config.TOKEN # Lichess Token des Hosters (challenge:bulk)
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/x-ndjson"
}

GAME_SETTINGS: Dict[str, Any] = {
    "rated": "false",
    "clock.limit": 10 * 60,
    "clock.increment": 5,
    "message": "Your Game {game} is ready!"
}

http = requests.Session()


def get_tokens(pair, candidates):
    t1, t2 = None, None
    for c in candidates["candidates"]:
        if c["player_id"] == pair[0]:
            t1 = c["token"]
            break
    for c in candidates["candidates"]:
        if c["player_id"] == pair[1]:
            t2 = c["token"]
            break
    return t1, t2


def create_pairings(pairings):
    if len(pairings) == 0:
        return print("no pairings!")
    file = open("candidates.json", "r")
    candidates = json.loads(file.read())
    players = []
    for pair in pairings:
        token_pair = get_tokens(pair, candidates)
        players.append(":".join(token_pair))
    return players


def create_games_bulk(pairings, clock_limit, clock_incr, pair_in, message, rated):
    pairings = create_pairings(pairings=pairings)
    now = int(time.time()) * 1000
    data = GAME_SETTINGS.copy()
    data["players"] = ",".join(pairings)
    data["pairAt"] = now + 1000 * 60 * pair_in
    data["clock.limit"] = clock_limit
    data["clock.increment"] = clock_incr
    data["message"] = message
    data["rated"] = rated
    rep = http.post(BULK_CREATE_API, data=data, headers=HEADERS)
    print(rep.text)
    log = open("log.json", "a")
    now = datetime.now()
    log.write("\n\n")
    log.write(f"{now.strftime('%Y%m%d %H:%M:%S')} for {pairings}:\n")
    json_string = json.loads(rep.text)
    json.dump(json_string, log, indent=3)
    log.close()
    return rep


def create_bulk():
    count = 0
    pairings_amount = int(input("How many Pairings you want to create?"))
    pairings = []
    while count < pairings_amount:
        player1 = input(f"ID of the player with white for the {count+1}. pairing:")
        player2 = input(f"ID of the player with black for the {count+1}. pairing:")
        pairing = [player1, player2]
        pairings.append(pairing)
        count += 1
    clock_limit = str(input("Clock Limit (in seconds):"))
    clock_increment = str(input("Clock Increment (in seconds):"))
    pair_at_bool = str(input("Do you want the pairing instant (Y) or in the future (N)? Y/N"))
    if pair_at_bool == "Y" or pair_at_bool == "y":
        pair_in = 0
    elif pair_at_bool == "N" or pair_at_bool == "n":
        pair_in = int(input("In how many minutes do you want to pair the pairings?"))
    else:
        print("The Input was not clear. We took 10 minutes as default value!")
        pair_in = 10
    rated_bool = str(input("Do you want the pairing rated (Y) or unrated (N)? Y/N"))
    if rated_bool == "Y" or rated_bool == "y":
        rated = "true"
    elif rated_bool == "N" or rated_bool == "n":
        rated = "false"
    else:
        print("The Input was not clear. We took rated as default value!")
        rated = "true"
    while True:
        print("Which message do you want to send to the players? It must contains '{game}' for the individual Game ID! When you finish press STRG+Z and Enter!")
        message = sys.stdin.read()
        if "{game}" in message:
            break
        else:
            print("In your message is the term {game} missing. This is essential!")
    bulk = create_games_bulk(pairings, clock_limit, clock_increment, pair_in, message, rated)
    print(f"Your Bulk is created:\n\n{bulk.text}")
    end = input("You can close this Window with any key.")


def view_bulk_pairings():
    HEADERS["Accept"] = "application/json"
    rep = http.get(BULK_VIEW, headers=HEADERS)
    print(rep.text)


def cancel_bulk(bulk_id):
    HEADERS["Accept"] = "application/json"
    rep = http.delete(BULK_CANCEL.format(bulk_id), headers=HEADERS)
    print(rep.text)


if __name__ == '__main__':
    create_bulk()
