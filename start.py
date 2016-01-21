#!flask/bin/python
import sys
from server import uchan

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Error: start.py [port]")
    else:
        uchan.development_start(int(sys.argv[1]))
