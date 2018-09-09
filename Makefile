all:
	gcc turn1.c -o turn -lwiringPi
	gcc control.c -o control -lwiringPi
