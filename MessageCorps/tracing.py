"""Tools for tracing messages though a cloud system,
best used in hand with the ELK stack (elastic search)
adds a unique Id to a message that originates either from a batch (kafka)
process, or from a REST (via GRPC) call."""

from uuid import uuid1

def trace_id():
    return uuid1().hex
