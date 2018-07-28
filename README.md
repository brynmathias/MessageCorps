MessageCorps is a wrapper around kafka-python, forcing the use of google protobuffers https://developers.google.com/protocol-buffers/docs/proto3

Later integration with GRPC for non batch operations is planned (also using the GRPC <-> Rest compatability for creating RESTful apis)

You require protoc to be installed to build the protobuffers, otherwise everything else is in requirements.txt


A very short send and recieve example is in the examples folder, you'll require docker-compose / docker for setting up your kafka instance.