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

- Install [myasync](https://github.com/KrySeyt/myasync)
```shell
git clone git@github.com:KrySeyt/myasync.git && pip install ./myasync
```

- Install `myredis`
```shell
pip install .
```

- Run `myredis`
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



