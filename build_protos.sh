#!/bin/bash
protoc --python_out=./ protobuf/**/*.proto
#python3 -m grpc_tools.protoc -I=./ --python_out=./ ./coheat_grpc_services/**/**/*.proto

