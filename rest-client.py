#!/usr/bin/env python3

import argparse
import base64
import json
import random
import time
from pathlib import Path

import requests
from PIL import Image


IMAGE_FILE = Path(__file__).resolve().parent / 'Flatirons_Winter_Sunrise_edit_2.jpg'

with Image.open(IMAGE_FILE) as image:
    EXPECTED_WIDTH, EXPECTED_HEIGHT = image.size


def doRawImage(addr, debug=False):
    headers = {'content-type': 'image/jpeg'}

    with open(IMAGE_FILE, 'rb') as f:
        img = f.read()

    image_url = addr + '/api/rawimage'
    response = requests.post(image_url, data=img, headers=headers)
    response.raise_for_status()

    result = response.json()

    assert result['width'] == EXPECTED_WIDTH
    assert result['height'] == EXPECTED_HEIGHT

    if debug:
        print("Response is", response)
        print(result)


def doAdd(addr, debug=False):
    headers = {'content-type': 'application/json'}

    add_url = addr + '/api/add/5/10'
    response = requests.post(add_url, headers=headers)
    response.raise_for_status()

    result = response.json()

    assert int(result['sum']) == 15, "Incorrect add result"

    if debug:
        print("Response is", response)
        print(result)


def doDotProduct(addr, debug=False):
    a = [random.random() for _ in range(100)]
    b = [random.random() for _ in range(100)]

    payload = {
        'a': a,
        'b': b
    }

    dot_url = addr + '/api/dotproduct'
    response = requests.post(dot_url, json=payload)
    response.raise_for_status()

    result = response.json()
    expected = sum(x * y for x, y in zip(a, b))

    assert abs(result['dotproduct'] - expected) < 1e-6, \
        "Incorrect dot product result"

    if debug:
        print("Response is", response)
        print(result)


def doJsonImage(addr, debug=False):
    with open(IMAGE_FILE, 'rb') as f:
        img = f.read()

    image_base64 = base64.b64encode(img).decode('utf-8')

    payload = {
        'image': image_base64
    }

    image_url = addr + '/api/jsonimage'
    response = requests.post(image_url, json=payload)
    response.raise_for_status()

    result = response.json()

    assert result['width'] == EXPECTED_WIDTH
    assert result['height'] == EXPECTED_HEIGHT

    if debug:
        print("Response is", response)
        print(result)


def main():
    parser = argparse.ArgumentParser(
        description='REST client for measuring server operations'
    )

    parser.add_argument(
        'host',
        help='IP address or hostname of the REST server'
    )

    parser.add_argument(
        'cmd',
        choices=['add', 'rawImage', 'dotProduct', 'jsonImage'],
        help='Operation to perform'
    )

    parser.add_argument(
        'reps',
        type=int,
        help='Number of repetitions for measurement'
    )

    parser.add_argument(
        '-p', '--port',
        type=int,
        default=5000,
        help='Server port (default: 5000)'
    )

    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Print the response from the server'
    )

    args = parser.parse_args()

    if args.reps <= 0:
        parser.error('reps must be greater than zero')

    addr = f"http://{args.host}:{args.port}"

    print(f"Running {args.reps} reps against {addr}")

    operations = {
        'add': doAdd,
        'rawImage': doRawImage,
        'dotProduct': doDotProduct,
        'jsonImage': doJsonImage
    }

    operation = operations[args.cmd]

    start = time.perf_counter()

    for _ in range(args.reps):
        operation(addr, debug=args.debug)

    delta = (
        (time.perf_counter() - start) / args.reps
    ) * 1000

    print(f"Took {delta:.6f} ms per operation")


if __name__ == '__main__':
    main()