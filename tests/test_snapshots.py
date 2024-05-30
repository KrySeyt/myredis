import json
import time
import uuid
from pathlib import Path

from tests import commands, responses
from tests.client import create_client


def test_snapshot_loaded(server_manager):
    snapshot_path = Path(".") / (str(uuid.uuid4()) + ".csv")

    server = server_manager.start_server(
        dbfilename=snapshot_path,
        snapshotsinterval=1,
    )

    test_value = str(uuid.uuid4())
    client = create_client(server.domain, server.port)
    client.send(commands.set_("test", test_value))

    assert client.recv(1024) == responses.ok()

    time.sleep(2)

    server_manager.kill_server(server.process.pid)

    server = server_manager.start_server(
        dbfilename=snapshot_path,
        snapshotsinterval=1,
    )

    client = create_client(server.domain, server.port)
    client.send(commands.get("test"))

    result = client.recv(1024) == responses.get(test_value)
    snapshot_path.unlink()
    assert result
