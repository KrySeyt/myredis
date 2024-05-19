import myasync

from myredis.old_main import main

if __name__ == "__main__":
    myasync.run(main())
