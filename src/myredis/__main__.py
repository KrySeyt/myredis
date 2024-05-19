import myasync

from myredis.main.tcp import main

if __name__ == "__main__":
    myasync.run(main())
