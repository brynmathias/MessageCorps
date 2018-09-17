"""Kafka wrapper for easy interface with protobufs and sending on channels bound
to that schema"""

import logging
import os
import sys
import threading
from time import sleep, time

from kafka import KafkaConsumer, KafkaProducer, TopicPartition
from tenacity import retry, stop_after_attempt, wait_exponential

from .pb_handler import MessageHandler, MessageLoader

LOGGER = logging.getLogger(__name__)


class MessagingException(Exception):
    """Exception type for messaging"""
    pass


class MessagingExceptionCritical(MessagingException):
    def __init__(self, e):
        super().__init__()
        sys.exit(0)


class kafka_producer(object):
    """docstring for KafkaProducer"""

    def __init__(self, topic=None, bootstrap_servers=None, async=True, **kwargs):
        super(kafka_producer, self).__init__()
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers if isinstance(
            bootstrap_servers, list) else [bootstrap_servers, ]
        self.async = async
        self.producer = None
        self.producer_args = kwargs
        self.setup()

    def setup(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers)
            LOGGER.debug(f"Setting producer topic to {self.topic}")
        except Exception as e:
            LOGGER.fatal("Could not create kafka producer",
                         exc_info=True)
            raise e

    def send(self, pb, topic=None, callback=None):
        """docstring for send"""
        this_topic = None
        message = None
        LOGGER.debug(f"called to send {pb}, self.topic {self.topic}, topic {topic}")
        if self.topic:
            this_topic = self.topic
            message = MessageHandler(pb)
        elif topic:
            this_topic = topic
            message = MessageHandler(pb)
        else:
            raise MessagingException("Called send without a topic and producer " +
                                     f"instantiated with topic = None {self.topic}")
        self.producer.send(this_topic, message.compress())
        if callable(callback):
            callback()

class kafka_consumer(object):
    """docstring for kafka_consumer"""

    def __init__(self, topic,
                 bootstrap_servers=None, enable_auto_commit=True,
                 start_point='latest', group=None,  **kwargs):

        super(kafka_consumer, self).__init__()
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.consumer = None
        if group:
            self.group = group
        else:
            self._get_group()
        self.enable_auto_commit = enable_auto_commit
        self.start_point = start_point
        self.kwargs = kwargs
        self.initial_setup()
        self._commit_lock = threading.Lock()

    def _get_group(self):
        try:
            self.group = os.getenv('LOG_TAG_GROUP', "NOTSET")
            self.service = os.getenv('LOG_TAG_SERVICE', "NOTSET")
        except Exception:
            LOGGER.warning("Could not set group and service tags",
                           exc_info=True)

    def initial_setup(self):
        """set up consumer"""
        try:
            self.create_kafka_consumer()
        except Exception as e:
            LOGGER.critical(
                "Could not create consumer with {0}".format(e), exc_info=e)
            LOGGER.critical("Exiting due to inability to create consumer")
            sys.exit(0)

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(1))
    def create_kafka_consumer(self):
        """docstring for create_kafka_consumer"""
        try:
            if isinstance(self.topic, list):
                self.consumer = KafkaConsumer(
                    group_id=self.group,
                    bootstrap_servers=self.bootstrap_servers,
                    enable_auto_commit=self.enable_auto_commit,
                    auto_offset_reset=self.start_point
                    )
                self.consumer.subscribe(self.topic)
            else:
                self.consumer = KafkaConsumer(
                    self.topic,
                    group_id=self.group,
                    bootstrap_servers=self.bootstrap_servers,
                    enable_auto_commit=self.enable_auto_commit,
                    auto_offset_reset=self.start_point)
        except Exception as e:
            LOGGER.critical(
                "Can't create a consumer with {0}".format(e), exc_info=e)
            raise e

    def get_position(self, topic=None):
        """docstring for get_position"""
        if topic is None:
            topic = self.topic
        if isinstance(topic, list):
            for item in topic:
                self.get_position(topic=item)
        else:
            pos = self.consumer.position(TopicPartition(topic, 0))
            LOGGER.info("Topic: {t}, position: {p}".format(t=topic, p=pos))

    def consume(self):
        while True:
            try:
                for message in self.consumer:
                    try:
                        LOGGER.debug(f"We have recieved {message}")
                        ml = MessageLoader(self.topic)
                        ml.load_kafka_message(message)
                        ret_val = ml.return_message()
                        LOGGER.info(f"Channel: {self.topic}, "
                                    f"Received: {ret_val._message_data.uuid} "
                                    f"at {ret_val._message_data.timestamp} "
                                    f"offset {ret_val._message_data.offset}, "
                                    f"partition {ret_val._message_data.partition}"
                                    )
                        yield ret_val
                    except Exception as e:
                        LOGGER.critical(f"{self} failed to consume message {message} on channel {message.topic} failed with: {e}",
                                    exc_info=True)
                        raise e

            except Exception as e:
                if self.consumer is not None:
                    try:
                        self.commit()
                        self.close()
                    except Exception as e:
                        LOGGER.critical(
                            "Couldn't close/commit consumer in exception due to {} trying to re-create".format(e))
                    self.create_kafka_consumer()
                    LOGGER.critical(
                        "consuming message failed with: ", exc_info=True)
                else:
                    raise MessagingExceptionCritical(
                        "Kafka has gone away, exiting running code, tried creating new consumer and failed")
            finally:
                sleep(0.0001)

    def commit(self):
        try:
            with self._commit_lock:
                LOGGER.debug('Commit called for %s', self)
                self.consumer.commit()
        except Exception as e:
            LOGGER.warning("Couldn't commit with {}".format(e))
            raise e

    def close(self):
        """docstring for close"""
        try:
            self.consumer.close()
        except Exception as e:
            LOGGER.warning("Couldn't close consumer with {}".format(e))
            raise e
