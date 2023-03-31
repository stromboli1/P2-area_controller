class ControlPacket():

    def __init__(self):
        """Contructor for the class

        Args:
            self:
        """
        # Set Global Variables
        self.packet = b''
        self.flags = 0

    def __repr__(self) -> str:
        """Returns parameters as a hex string

        Args:
            self:

        Returns:
            str: packet as hex
        """
        return self.get_packet().hex()

    def get_packet(self) -> bytes:
        """Method to get the full packet.

        Args:
            self:

        Returns:
            bytes: Packet with flags appended
        """
        return self.flags.to_bytes(1, 'big') + self.packet

    def add_clksync(self, clk: int) -> None:
        """Adds clock syncronization parameter

        Args:
            self:
            clk (int): clock time

        Returns:
            None:
        """

        # Extract flags to a temp variable
        newflags = self.flags

        # Set the flag bit
        newflags |= 1

        # Recompile packet with new clock sync
        self.recompile(newflags, clk = clk.to_bytes(4, 'big'))

        # Save the new flags
        self.flags = newflags

    def add_devices(self, onoff: bool, devices: int) -> None:
        """Adds device parameter

        Args:
            self:
            onoff (bool): Should the devices be turned on or off?
            devices (int): Devices to affect

        Returns:
            None:
        """

        # Extract flags to a temp variable
        newflags = self.flags

        # Set the flag bits
        newflags |= 8
        if onoff: newflags |= 4
        else: newflags &= ~4

        # Recompile packet with new devices
        self.recompile(newflags, devices = devices.to_bytes(1, 'big'))

        # Save the new flags
        self.flags = newflags

    def decompile(self) -> tuple[bytes, list[bytes], bytes]:
        """Decompiles the packet and extracts parameters

        Args:
            self:

        Returns:
            tuple[bytes, list[bytes], bytes]: Decompiled parameters
        """

        # Set variables
        cursor = 0
        clk = None
        devices = None
        paramlist = None

        # Decompile clock sync
        if self.flags & 1 > 0:
            clk = self.packet[cursor:cursor+4]
            cursor += 4

        # Decompile devices
        if self.flags & 8 > 0:
            devices = self.packet[cursor].to_bytes(1, 'big')
            cursor += 1

        return (clk, paramlist, devices)

    def recompile(self, newflags: int, **kwargs: bytes | list[bytes]) -> None:
        """Recompiles the packet with new parameters

        Args:
            self:
            kwargs (bytes | list[bytes]): Parameters

        Returns:
            None:
        """

        # Decompile the parameters
        clk, paramlist, devices = self.decompile()

        # Reset packet
        self.packet = b''

        # Add new clock or add the old one back
        if newflags & 1 > 0:
            clk = kwargs.get('clk', clk)
            if not clk:
                raise Exception('clk not set')
            self.packet += clk

        # Add new devices or add the old one back
        if newflags & 8 > 0:
            devices = kwargs.get('devices', devices)
            if not devices:
                raise Exception('devices not set')
            self.packet += devices
