
protoc --plugin=protoc-gen-ts=..\..\node_modules\.bin\protoc-gen-ts.cmd --js_out=import_style=commonjs,binary:..\csr_frontend\protobuf_js --ts_out=..\csr_frontend\protobuf_js types.proto