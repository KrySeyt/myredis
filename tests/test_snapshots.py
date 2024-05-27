import json
import time
import uuid
from pathlib import Path

from tests import commands, responses
from tests.client import create_client
from tests.server import ServerManager


def test_snapshot_created(server_manager: ServerManager):
    snapshot_dir = "."
    snapshot_file = str(uuid.uuid4())

    server = server_manager.start_server(
        dir=snapshot_dir,
        dbfilename=snapshot_file,
        snapshotsinterval=1,
    )

    test_value = str(uuid.uuid4())
    client = create_client(server.domain, server.port)
    client.send(commands.set_("test", test_value))

    assert client.recv(1024) == responses.ok()

    time.sleep(2)

    file_path = Path(snapshot_dir) / snapshot_file

    with open(file_path, "r") as file:
        result = file.read() == json.dumps({
            "test": {
                "_value": test_value,
                "expires": None
            }
        })

    file_path.unlink(missing_ok=False)
    assert result


def test_snapshot_loaded(server_manager):
    test_value = str(uuid.uuid4())
    snapshot_path = Path(str(uuid.uuid4()))

    with open(snapshot_path, "w") as file:
        json.dump(
            {
                "test": {
                    "_value": test_value,
                    "expires": None,
                }
            },
            file,
        )

    server = server_manager.start_server(
        dbfilename=str(snapshot_path),
    )

    client = create_client(server.domain, server.port)
    client.send(commands.get("test"))

    result = client.recv(1024) == responses.get(test_value)
    snapshot_path.unlink()
    assert result
