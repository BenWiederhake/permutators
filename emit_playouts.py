#!/usr/bin/env python3

import json
import secrets
import time

NUM_PLAYERS = 5
TURNS = 30
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


class AvoidTurnbackPermutator:
    name = 'avoid_turnback'

    def __init__(self, players):
        self.players = set(players)
        assert len(self.players) > 1
        self.last = None
        self.second_last = None

    def basic_poll(self):
        available = set(self.players)
        if self.last is not None:
            available.remove(self.last)
        chosen = secrets.choice(list(available))
        return chosen

    def poll(self):
        chosen = self.basic_poll()
        if self.second_last == chosen:
            chosen = self.basic_poll()
        self.second_last = self.last
        self.last = chosen
        return chosen


PERMUTATORS.append(AvoidTurnbackPermutator)


class GenerationalPermutator:
    name = 'generational'

    def __init__(self, players):
        assert len(players) > 1
        self.generation = 1
        self.last_chosen = {p: 0 for p in players}
        self.rng = secrets.SystemRandom()
        self.most_recent = None

    def poll(self):
        weight_tuples = [(p, self.generation - last_chosen) for p, last_chosen in self.last_chosen.items()]
        chosen = self.rng.choices(*zip(*weight_tuples))[0]
        self.generation += 1
        self.last_chosen[chosen] = self.generation
        self.most_recent = chosen
        return chosen


PERMUTATORS.append(GenerationalPermutator)


def do_playout(permutator_class, players, turns):
    permutator = permutator_class(players)
    return [permutator.poll() for _ in range(turns)]


def playout_analysis(playout, players):
    # String manip is actually easier here
    playout = ''.join(playout)
    parts = []
    waits = []
    turns = []

    for player in players:
        segments = playout.split(player)

        for s in segments:
            waits.append((player, len(s)))
        turns.append(str(len(segments)))

        segments[0] = '?' + segments[0]
        segments[-1] = segments[-1] + '?'
        successors = ''.join(s[0] for s in segments[1:])
        predecessors = ''.join(s[-1] for s in segments[:-1])

        parts.append(f'{player}:{predecessors}→{successors}')

    waits.sort(key=lambda p: (-p[1], p[0]))
    waits = waits[:5]
    waits = ','.join(f'{p}{time}' for p, time in waits)

    return f'{waits} {",".join(turns)} {" ".join(parts)}'


def run(classes, num_players, turns, samples_each):
    rng = secrets.SystemRandom()
    players = [chr(65 + i) for i in range(NUM_PLAYERS)]
    hints = dict()
    playout_list = []
    for permutator_class in classes:
        for _ in range(samples_each):
            playout = ''.join(do_playout(permutator_class, players, turns))
            token = secrets.token_urlsafe(16)
            playout_list.append((playout, token))
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
        fp.write('# GOOD\n')
        fp.write('\n')
        fp.write('# BAD\n')
        fp.write('\n')
        fp.write('# UNSORTED\n')
        fp.write('\n')
        for playout, token in playout_list:
            fp.write(f'{playout} -> {playout_analysis(playout, players)}  # {token}\n')

    print(f'Written to {filename_hints} and {filename_playouts}')


if __name__ == '__main__':
    run(PERMUTATORS, NUM_PLAYERS, TURNS, SAMPLES_EACH)
