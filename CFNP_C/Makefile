Message: src/C/Tools/Message.c src/C/Tools/Encoding.c
	gcc -shared -o bin/lib/Message.so -fPIC src/C/Tools/Message.c src/C/Tools/Encoding.c

test: src/C/test.c src/C/Tools/Message.c src/C/Tools/Encoding.c
	gcc -o bin/test src/C/test.c src/C/Tools/Message.c src/C/Tools/Encoding.c

interface: src/C/Client.c src/C/Server.c src/C/Tools/Message.c src/C/Tools/Encoding.c
	gcc -o bin/client src/C/Client.c src/C/Tools/Message.c src/C/Tools/Encoding.c
	gcc -o bin/server src/C/Server.c src/C/Tools/Message.c src/C/Tools/Encoding.c