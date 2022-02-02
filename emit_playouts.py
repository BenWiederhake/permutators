#!/usr/bin/env python3

import json
import secrets
import time

NUM_PLAYERS = 3
TURNS = 20
SAMPLES_EACH = 5
PERMUTATORS = []


class UniformPermutator:
    name = 'uniform'

    def __init__(self, players):
        self.players = set(players)
        assert len(self.players) > 1
        self.last = None

    def poll(self):
        available = set(self.players)
        if self.last is not None:
            available.remove(self.last)
        chosen = secrets.choice(list(available))
        self.last = chosen
        return chosen


PERMUTATORS.append(UniformPermutator)


def do_playout(permutator_class, players, turns):
    permutator = permutator_class(players)
    return [permutator.poll() for _ in range(turns)]


def run(classes, num_players, turns, samples_each):
    rng = secrets.SystemRandom()
    players = [chr(65 + i) for i in range(NUM_PLAYERS)]
    hints = dict()
    playout_list = []
    for permutator_class in classes:
        for _ in range(samples_each):
            playout = ''.join(do_playout(permutator_class, players, turns))
            token = secrets.token_urlsafe(8)
            playout_list.append(f'{playout}  # {token}')
            hints[token] = permutator_class.name
    rng.shuffle(playout_list)

    timestamp = time.time_ns()
    filename_hints = f'hints_{timestamp}.json'
    filename_playouts = f'playouts_{timestamp}.txt'

    with open(filename_hints, 'w') as fp:
        json.dump(dict(classes=hints, filename_playouts=filename_playouts), fp, indent=4)
    with open(filename_playouts, 'w') as fp:
        fp.write(f'# Permutators: {[c.name for c in classes]}\n')
        fp.write(f'# Players: {players}\n')
        fp.write(f'# Turns: {turns}\n')
        fp.write(f'# Samples for each permutator: {samples_each}\n')
        fp.write(f'# Filename hints: {filename_hints}\n')
        fp.write('\n')
        for playout in playout_list:
            fp.write(f'{playout}\n')

    print(f'Written to {filename_hints} and {filename_playouts}.')


if __name__ == '__main__':
    run(PERMUTATORS, NUM_PLAYERS, TURNS, SAMPLES_EACH)
