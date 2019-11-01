Message: Message.c Encoding.c
	gcc -shared -o Message.so -fPIC Message.c Encoding.c

test: test.c Message.c Encoding.c
	gcc -o test test.c Message.c Encoding.c