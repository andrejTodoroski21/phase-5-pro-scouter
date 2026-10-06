"""The fixed list of games a clip can belong to.

Kept as a constant rather than a table: the list changes rarely, and a table
would mean a join on every feed query for data that fits in memory. If games
ever become user-editable this is the thing to promote to a table.
"""

GAMES = [
    {'slug': 'valorant', 'name': 'Valorant'},
    {'slug': 'cs2', 'name': 'Counter-Strike 2'},
    {'slug': 'rocket-league', 'name': 'Rocket League'},
    {'slug': 'apex-legends', 'name': 'Apex Legends'},
    {'slug': 'league-of-legends', 'name': 'League of Legends'},
    {'slug': 'overwatch-2', 'name': 'Overwatch 2'},
    {'slug': 'fortnite', 'name': 'Fortnite'},
    {'slug': 'rainbow-six-siege', 'name': 'Rainbow Six Siege'},
]

GAME_SLUGS = {g['slug'] for g in GAMES}
GAME_NAMES = {g['slug']: g['name'] for g in GAMES}


def is_valid(slug):
    return slug in GAME_SLUGS
