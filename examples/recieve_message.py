#!/usr/bin/env python3

from MessageCorps.broker import kafka_consumer
import logging

logging.basicConfig(level=logging.DEBUG)


def main():
    consumer = kafka_consumer(bootstrap_servers="localhost:9092", topic="VideoStream")

    for message in consumer.consume():
        print(message)


if __name__ == '__main__':
    main()
