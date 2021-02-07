protoc --plugin=protoc-gen-ts=..\..\node_modules\.bin\protoc-gen-ts.cmd --js_out=import_style=commonjs,binary:..\sotcat_frontend\protobuf_js --ts_out=..\sotcat_frontend\protobuf_js types.proto

# protoc --python_out=..\sotcat_backend\protobuf_py types.proto

protoc --python_betterproto_out=..\sotcat_backend\pkg\protobuf_py types.proto
