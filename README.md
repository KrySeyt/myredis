# MyRedis
My simple Redis data structure store powered by [myasync](https://github.com/KrySeyt/myasync). RESP2 compatible. Supports `redis-cli`. 

Implemented:
- Replicas
- Append-only snapshots
- Ping
- Echo
- Get
- Set (with expire)
- Get config values

# Setup
- Create venv
```shell
python -m venv .venv 
```

- Activate venv
```shell
. .venv/bin/activate 
```

- Install `myredis`
```shell
pip install myredis@git+https://github.com/KrySeyt/myredis.git
```

- Run `myredis` server
```shell
python -m myredis
```

# Configuration
- `--port <port:int>` - Optional. Server port. Default - `6379`
- `--dir <dirname:str>` - Optional. DB files dir.
- `--dbfilename <filename:str>` - Optional. DB filename.
- `--snapshotsinterval <seconds:int>` - Optional. Interval between snapshot updates. Default - 300 secs (5 mins)
- `--replicaof <master-domain:str> <master-port:int>` - Optional. Start server as replica of master

```shell
python -m myredis --port 6379 --dir mydir --dbfilename dbfile
```

# Supported commands

```shell
redis-cli get foo
```

```shell
redis-cli set foo bar
```

```shell
redis-cli set foo bar px 1000
```

```shell
redis-cli wait 3 1000
```

```shell
redis-cli ping
```

```shell
redis-cli echo "Hello, World\!"
```

```shell
redis-cli wait 3 1000
```

```shell
redis-cli config get port
```

# Supported data types
- String
- Integer (server responses only)
- Null (server responses only)

# Tests
- Complete [Setup](#Setup)

- Run tests
```shell
pytest
```
