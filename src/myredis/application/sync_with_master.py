from myredis.application.gateways.master import MasterGateway
from myredis.application.gateways.values import ValuesStorage


class SyncWithMaster:
    def __init__(self, values_storage: ValuesStorage, master_gateway: MasterGateway) -> None:
        self._values_storage = values_storage
        self._master_gateway = master_gateway

    def __call__(self) -> None:
        records = self._master_gateway.get_records()
        self._values_storage.set_records(records)
