import myasync

from myredis.application.wait_replicas import WaitReplicas
from myredis.external.tcp_replicas import TCPReplicasManager


def wait(replicas_count: int, timeout: int) -> myasync.Coroutine[bytes]:
    wait_interactor = WaitReplicas(TCPReplicasManager())
    responded_replicas_count = yield from wait_interactor(replicas_count, timeout / 1000)
    return f":{responded_replicas_count}\r\n".encode()
