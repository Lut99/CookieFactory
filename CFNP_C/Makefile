Message: src/C/Tools/Message.c src/C/Tools/Encoding.c
	gcc -shared -o bin/Message.so -fPIC src/C/Tools/Message.c src/C/Tools/Encoding.c

test: src/C/test.c src/C/Tools/Message.c src/C/Tools/Encoding.c
	gcc -o bin/test src/C/test.c src/C/Tools/Message.c src/C/Tools/Encoding.c