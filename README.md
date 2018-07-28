MessageCorps is a wrapper around kafka-python, forcing the use of google protobuffers https://developers.google.com/protocol-buffers/docs/proto3

Later integration with GRPC for non batch operations is planned (also using the GRPC <-> Rest compatability for creating RESTful apis)

You require protoc to be installed to build the protobuffers, otherwise everything else is in requirements.txt


A very short send and recieve example is in the examples folder, you'll require docker-compose / docker for setting up your kafka instance.



# Adding new protobufs

You can add new folders or sub folders depending on the hierachy you require.

1) Add new .proto file and fill in (see the link above for documentation)

2) Build the protos in to python files (top level run build_protos.sh)

3) Add the import path and channel: object mapping in MessageCorps/pb_handler.py so you have the correct associations

4) Install via your favourite method (either setup.py install or bump the version number, commit to git and install your projects dependancies again using pip)
