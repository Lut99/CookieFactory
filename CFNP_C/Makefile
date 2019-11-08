Message: src/C/Message.c src/C/Encoding.c
	gcc -shared -o bin/Message.so -fPIC src/C/Message.c src/C/Encoding.c

test: src/C/test.c src/C/Message.c src/C/Encoding.c
	gcc -o bin/test src/C/test.c src/C/Message.c src/C/Encoding.c