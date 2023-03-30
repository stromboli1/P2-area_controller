

class ControlProtocol():

    def __init__(self):
        """__init__.

        Args:
            self:
        """
        self.packet = b''
        self.flags = 0

    def get_packet(self) -> bytes:
        """get_packet.

        Args:
            self:

        Returns:
            bytes: packet
        """
        return self.flags.to_bytes(1, 'big') + self.packet

    def add_clksync(self, clk: int) -> None:
        """add_clksync.

        Args:
            self:
            clk (int): clk

        Returns:
            None:
        """
        self.flags += 1
        recompile(clk = clk.to_bytes(4, 'big'))

    def add_onoff(self, onoff: bool, devices: int) -> None:
        """add_onoff.

        Args:
            self:
            onoff (bool): onoff
            devices (int): devices

        Returns:
            None:
        """
        self.flags += 8
        if onoff: self.flags += 4
        recompile(devices = devices.to_bytes(1, 'big'))

    def decompile(self) -> tuple[bytes, list[bytes], bytes]:
        """decompile.

        Args:
            self:

        Returns:
            tuple[bytes, list[bytes], bytes]:
        """
        cursor = 0
        clk = None
        devices = None
        paramlist = None

        if self.flags & 1 > 0:
            clk = self.packet[cursor:cursor+4]
            cursor += 4

        if self.flags & 8 > 0:
            devices = self.packet[cursor]
            cursor += 1

        return (clk, paramlist, devices)

    def recompile(self, **kwargs) -> None:
        """recompile.

        Args:
            self:
            kwargs:

        Returns:
            None:
        """
        clk, paramlist, devices = decompile()
        self.packet = b''

        if self.flags & 1 > 0:
            clk = kwargs.get('clk', clk)
            if not clk:
                raise Exception('clk not set')
            self.packet += clk

        if self.flags & 8 > 0:
            devices = kwargs.get('devices', devices)
            if not devices:
                raise Exception('devices not set')
            self.packet += devices
