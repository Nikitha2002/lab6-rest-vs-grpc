#!/usr/bin/env python3

import grpc
from concurrent import futures
import argparse
from PIL import Image
import io
import base64

import lab6_pb2
import lab6_pb2_grpc


class Lab6Service(lab6_pb2_grpc.Lab6ServiceServicer):

    def add(self, request, context):
        result = request.a + request.b
        return lab6_pb2.addReply(sum=result)
    def dotproduct(self, request, context):
        a = request.a
        b = request.b

        if len(a) != len(b):
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                'Vectors must have the same length'
            )

        result = sum(x * y for x, y in zip(a, b))

        return lab6_pb2.dotProductReply(
            dotproduct=result
        )
    def rawimage(self, request, context):
        try:
            image_bytes = request.img

            img = Image.open(io.BytesIO(image_bytes))

            return lab6_pb2.imageReply(
                width=img.size[0],
                height=img.size[1]
            )

        except Exception as e:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                f'Invalid image: {e}'
            )
    def jsonimage(self, request, context):
        try:
            image_base64 = request.img

            image_bytes = base64.b64decode(image_base64)

            img = Image.open(io.BytesIO(image_bytes))

            return lab6_pb2.imageReply(
                width=img.size[0],
                height=img.size[1]
            )

        except Exception as e:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                f'Invalid image: {e}'
            )


def serve():
    parser = argparse.ArgumentParser(
        description='Lab 6 gRPC Server'
    )

    parser.add_argument(
        '-p', '--port',
        type=int,
        default=50051,
        help='gRPC server port (default: 50051)'
    )

    args = parser.parse_args()

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    lab6_pb2_grpc.add_Lab6ServiceServicer_to_server(
        Lab6Service(), server
    )

    server.add_insecure_port(f'[::]:{args.port}')
    server.start()

    print(f'gRPC server running on port {args.port}')

    server.wait_for_termination()


if __name__ == '__main__':
    serve()