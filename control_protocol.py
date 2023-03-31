class ControlProtocol():

    def __init__(self):
        """__init__.

        Args:
            self:
        """
        self.packet = b''
        self.flags = 0

    def __repr__(self) -> str:
        """Returns parameters

        Args:
            self:

        Returns:
            str: packet as hex
        """
        return (self.flags.to_bytes(1, 'big') + self.packet).hex()

    def add_clksync(self, clk: int) -> None:
        """Adds clock syncronization parameter

        Args:
            self:
            clk (int): clk

        Returns:
            None:
        """
        newflags = self.flags
        newflags |= 1
        self.recompile(newflags, clk = clk.to_bytes(4, 'big'))
        self.flags = newflags

    def add_devices(self, onoff: bool, devices: int) -> None:
        """Adds device parameter

        Args:
            self:
            onoff (bool): onoff
            devices (int): devices

        Returns:
            None:
        """
        newflags = self.flags
        newflags |= 8
        if onoff: newflags |= 4
        else: newflags &= ~4
        self.recompile(newflags, devices = devices.to_bytes(1, 'big'))
        self.flags = newflags

    def decompile(self) -> tuple[bytes, list[bytes], bytes]:
        """Decompiles the packet and extracts parameters

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
            devices = self.packet[cursor].to_bytes(1, 'big')
            cursor += 1

        return (clk, paramlist, devices)

    def recompile(self, newflags: int, **kwargs: bytes | list[bytes]) -> None:
        """Recompiles the packet with new parameters

        Args:
            self:
            kwargs (bytes | list[bytes]): kwargs

        Returns:
            None:
        """
        clk, paramlist, devices = self.decompile()
        self.packet = b''

        #Verifies if there is a clock parameter
        if newflags & 1 > 0:
            clk = kwargs.get('clk', clk)
            if not clk:
                raise Exception('clk not set')
            self.packet += clk

        #Verifies if there is a device parameter
        if newflags & 8 > 0:
            devices = kwargs.get('devices', devices)
            if not devices:
                raise Exception('devices not set')
            self.packet += devices
