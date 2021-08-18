import requests
import time
import json
import config

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
        if c["order"] == pair[0]:
            t1 = c["token"]
            break
    for c in candidates["candidates"]:
        if c["order"] == pair[1]:
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


def create_games_bulk(pairings, clock_limit, clock_incr, waiting):
    pairings = create_pairings(pairings=pairings)
    now = int(time.time()) * 1000
    data = GAME_SETTINGS.copy()
    data["players"] = ",".join(pairings)
    data["pairAt"] = now + 1000 * 60 * 1
    rep = http.post(BULK_CREATE_API, data=data, headers=HEADERS)
    print(rep.text)
    log = open("log.json", "a")
    now = datetime.now()
    log.write("\n\n")
    log.write(f"{now.strftime('%Y%m%d %H:%M:%S')} for {pairings}:\n")
    json_string = json.loads(rep.text)
    json.dump(json_string, log, indent=3)
    log.close()


def create_games_initial(clock_limit, clock_incr):



    create_games_bulk(pairings=, clock_limit=clock_limit, )


def view_bulk_pairings():
    HEADERS["Accept"] = "application/json"
    rep = http.get(BULK_VIEW, headers=HEADERS)
    print(rep.text)


def cancel_bulk(bulk_id):
    HEADERS["Accept"] = "application/json"
    rep = http.delete(BULK_CANCEL.format(bulk_id), headers=HEADERS)
    print(rep.text)


if __name__ == '__main__':
    print("hi")
