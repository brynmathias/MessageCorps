#!/usr/bin/env python3
from MessageCorps.broker import kafka_producer
from protobuf.data.ImageData_pb2 import Image
from time import sleep
import logging

logging.basicConfig(level=logging.DEBUG)

def main():

    producer = kafka_producer(bootstrap_servers=['localhost:9092'], topic="VideoStream")

    test_image = Image(
        image_data = b"this is just a test string",
        height = 10,
        width = 10
    )
    for frame in range(100):
        test_image.frame = frame
        producer.send(test_image)
        sleep(1)




if __name__ == "__main__":
    main()