
#!/usr/bin/env python3

import grpc
import argparse
import time
import random
import base64
import math

import lab6_pb2
import lab6_pb2_grpc


IMAGE_FILE = 'Flatirons_Winter_Sunrise_edit_2.jpg'


def doAdd(stub, debug=False):
    response = stub.add(
        lab6_pb2.addMsg(a=5, b=10)
    )

    assert response.sum == 15, "Incorrect add result"

    if debug:
        print("Sum:", response.sum)


def doRawImage(stub, debug=False):
    with open(IMAGE_FILE, 'rb') as f:
        img = f.read()

    response = stub.rawimage(
        lab6_pb2.rawImageMsg(img=img)
    )

    assert response.width == 3004
    assert response.height == 1002

    if debug:
        print("Image dimensions:", response.width, response.height)


def doDotProduct(stub, debug=False):
    a = [random.random() for _ in range(100)]
    b = [random.random() for _ in range(100)]

    response = stub.dotproduct(
        lab6_pb2.dotProductMsg(a=a, b=b)
    )

    expected = sum(x * y for x, y in zip(a, b))

    # Protobuf uses float32, so allow small rounding differences
    assert math.isclose(
        response.dotproduct,
        expected,
        rel_tol=1e-5,
        abs_tol=1e-5
    ), "Incorrect dot product result"

    if debug:
        print("Dot product:", response.dotproduct)


def doJsonImage(stub, debug=False):
    with open(IMAGE_FILE, 'rb') as f:
        img = f.read()

    encoded = base64.b64encode(img).decode('utf-8')

    response = stub.jsonimage(
        lab6_pb2.jsonImageMsg(img=encoded)
    )

    assert response.width == 3004
    assert response.height == 1002

    if debug:
        print("Image dimensions:", response.width, response.height)


def main():
    parser = argparse.ArgumentParser(
        description='Lab 6 gRPC Client'
    )

    parser.add_argument('host')
    parser.add_argument(
        'cmd',
        choices=['add', 'rawImage', 'dotProduct', 'jsonImage']
    )
    parser.add_argument('reps', type=int)
    parser.add_argument('-p', '--port', type=int, default=50051)
    parser.add_argument('-d', '--debug', action='store_true')

    args = parser.parse_args()

    if args.reps <= 0:
        parser.error('reps must be greater than zero')

    address = f'{args.host}:{args.port}'

    print(f'Running {args.reps} reps against {address}')

    operations = {
        'add': doAdd,
        'rawImage': doRawImage,
        'dotProduct': doDotProduct,
        'jsonImage': doJsonImage
    }

    # gRPC uses one channel for all requests
    with grpc.insecure_channel(
        address,
        options=[
            ('grpc.max_send_message_length', 16 * 1024 * 1024),
            ('grpc.max_receive_message_length', 16 * 1024 * 1024)
        ]
    ) as channel:
        stub = lab6_pb2_grpc.Lab6ServiceStub(channel)

        operation = operations[args.cmd]

        start = time.perf_counter()

        for _ in range(args.reps):
            operation(stub, debug=args.debug)

        delta = (
            (time.perf_counter() - start) / args.reps
        ) * 1000

        print(f'Took {delta:.6f} ms per operation')


if __name__ == '__main__':
    main()