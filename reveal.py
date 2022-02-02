#!/usr/bin/env python3

import json
import sys


def run(playouts_filename):
    assert playouts_filename.startswith('playouts_') and playouts_filename.endswith('.txt'), playouts_filename
    timestamp = playouts_filename[len('playouts_'):-len('.txt')]
    hints_filename = f'hints_{timestamp}.json'
    with open(playouts_filename, 'r') as fp:
        playouts = fp.read()
    with open(hints_filename, 'r') as fp:
        hints_data = json.load(fp)
    assert hints_data['filename_playouts'] == playouts_filename
    print(hints_data['classes'])
    for token, class_name in hints_data['classes'].items():
        playouts = playouts.replace(token, class_name)

    print(playouts.rstrip('\n'))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Unveil what? USAGE: {sys.argv[0]} playouts_123456789.txt', file=sys.stderr)
        exit(1)
    run(sys.argv[1])
