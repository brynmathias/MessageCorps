"""Tools for handling the protobufs we've made,
this could be done in a nicer way involving auto grabbing the names of the protobufs,
but for the moment this makes using the code in prodcution easier if you're small"""

from datetime import datetime
import logging
import pytz
import uuid

from tracing import trace_id 
import os

# Import the protobuf objects


LOGGER = logging.getLogger("messaging.protobuff_loader")

def utcnow():
    return pytz.utc.localize(datetime.utcnow())


class MessageHandlerException(Exception):
    pass


def topic_to_object(topic):
    """You pass us a topic name we return you a class"""
    try:
        return {
        }[topic]
    except Exception as e:
        LOGGER.critical("could not convert topic string to protobuff message type with {0}".format(e), exc_info=e)
        raise e


def hex_str_to_bytes(hs):
    return bytes(bytearray.fromhex(hs))


def bytes_to_hex_str(b):
    return "".join(['%02x' % i for i in b])


def check_json(pb):
    """docstring for check_json"""
    if "JSON" in str(type(pb)):
        LOGGER.warning("Using a json message rather than defined protobuf")


class MessageHandler():
    def __init__(self, pb, **kwargs):
        self.pb = pb
        self.kwargs = kwargs
        self._add_meta_data()
        self._setattrs()
        self._add_meta_data()
        check_json(self.pb)

    def list_attrs(self):
        for item in self.pb._fields.items():
            print(item)

    def _setattrs(self):
        [ setattr(self.pb, key, self.kwargs[key]) for key in self.kwargs if hasattr(self.pb, key) ]
        # for key in self.kwargs:
        #     if hasattr(self.pb, key):
        #         setattr(self.pb, key, self.kwargs[key])

    def _add_meta_data(self):
        if not hasattr(self.pb, "_message_data"):
            LOGGER.critical("Protobuff does not have _message_data field this is necessary")
            raise MessageHandlerException("Protobuf does not contain _message_data field")
        self.md = self.pb._message_data
        self.md.iso_date = utcnow().isoformat()
        self.md.environment = messageData.Environment.Value(ENVIRONMENT)
        self.md.sending_service = SENDING_SERVICE
        self.md.uuid = str(uuid.uuid1())
        if not self.md.trace_id:
            self.md.trace_id = Tracing.trace_id()

    def string_repr(self):
        return self.pb.SerializeToString()

    def to_dict(self):
        """docstring for to_json"""
        return {"protobuf": bytes_to_hex_str(self.string_repr())}


class MessageLoader():
    def __init__(self, message_type):
        if isinstance(message_type, str):
            self.pb = topic_to_object(message_type)()
        else:
            self.pb = message_type()
        check_json(self.pb)

    def load_from_request(self, obj):
        if not isinstance(obj, dict):
            raise MessageHandlerException("Didn't receive a dict")
        encoded = obj.get("protobuf")
        if not isinstance(encoded, str):
            LOGGER.error("Passed malformed dictionary containing protobuf")
            raise ("Passed malformed dictionary containing protobuf")
        LOGGER.debug("Loading: {0}, into {1}".format(encoded, type(self.pb)))
        self.load_message(hex_str_to_bytes(encoded))

    def load_message(self, message):
        self.pb.ParseFromString(message)

    def load_kafka_message(self, message):
        self.load_message(message.value)
        self.pb._message_data.offset = message.offset
        self.pb._message_data.partition = message.partition

    def return_message(self):
        return self.pb
