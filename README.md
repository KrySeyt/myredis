# MyRedis
My simple Redis powered by [myasync](https://github.com/KrySeyt/myasync)

# Setup
- Copy repo
```shell
git clone git@github.com:KrySeyt/myredis.git
```

- Create venv
```shell
python -m venv .venv 
```

- Activate venv
```shell
. ./.venv/bin/activate 
```

- Install `myredis`
```shell
pip install .
```

- Run `myredis` server
```shell
python -m src.myredis
```

# Configuration
- `--port <port:int>` - Optional. Server port. Default - `6379`
- `--dir <dirname:str>` - Optional. DB files dir. DB files not implemented yet
- `--dbfilename <filename:str>` - Optional. DB filename. DB files not implemented yet
- `--replicaof <master-domain:str> <master-port:int>` - Optional. Start server as replica of master

```shell
python -m src.myredis --port 6379 --dir mydir --dbfilename dbfile
```

# Supported commands

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


