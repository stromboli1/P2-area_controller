

class ControlProtocol():

    def __init__(self):
        self.packet = b''
        self.flags = 0

    def get_packet(self) -> bytes:
        return self.flags.to_bytes(1, 'big') + self.packet

    def add_clksync(self, clk: int) -> None:
        self.flags += 1
        self.packet += clk.to_bytes(4, 'big')

    def add_onoff(self, onoff: bool, devices: int) -> None:
        self.flags += 8
        if onoff: self.flags += 4
        self.packet += devices.to_bytes(1, 'big')
