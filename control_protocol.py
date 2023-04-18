from typing import Union, Optional, Self

class ControlPacket():
    """Control Protocol Packet.
    """

    def __init__(self: Self):
        """Constructor for the class

        Args:
            self:
        """

        # Set Global Variables
        self.packet: bytes = b''
        self.flags: int = 0

    def __repr__(self: Self) -> str:
        """Returns parameters as a hex string

        Args:
            self:

        Returns:
            str: packet as hex
        """
        return self.get_packet().hex()

    def get_packet(self: Self) -> bytes:
        """Method to get the full packet.

        Args:
            self:

        Returns:
            bytes: Packet with flags appended
        """
        return self.flags.to_bytes(1, 'big') + self.packet

    def print_packet(self: Self) -> None:
        """Method for printing packet in a readable manner.

        Args:
            self:

        Returns:
            None:
        """

        # Decompile Parameters
        decompiled: tuple[Optional[bytes], Optional[list[bytes]], Optional[bytes]] = self.decompile()
        clk: Optional[bytes] = decompiled[0]
        paramlist: Optional[list[bytes]] = decompiled[1]
        devices: Optional[bytes] = decompiled[2]

        # Print the flags in binary notation
        print("--- Packet Breakdown ---")
        print("Flags:")
        print(f"{self.flags:08b}")
        print()

        # Print clk sync in binary notation
        if clk:
            clk_int: int = int.from_bytes(clk, 'big')
            print("CLK Sync:")
            print(f"{clk_int:032b} ({clk_int})")
            print("")

        # Print sim parameters in binary
        if paramlist:

            # Print the number of parameters
            paramnum: int = len(paramlist)
            print("Number of parameters:")
            print(f"{paramnum:08b} ({paramnum})")
            print("")

            # Print each parameter
            print("Param ID\tParam Size\tParam Data")
            for param in paramlist:
                paramid: int = param[0]
                print(f"{paramid:08b} ({paramid})\t", end="")
                paramsize: int = param[1]
                print(f"{paramsize:08b} ({paramsize})\t", end="")
                for byte in param[2:]:
                    print(f"{byte:08b}", end="")
            print("")

        # Print devices in binary notation
        if devices:
            devices_int: int = int.from_bytes(devices, 'big')
            print("Devices:")
            print(f"{devices_int:08b}")
            print("")

    def add_clksync(self: Self, clk: int) -> None:
        """Adds clock syncronization parameter

        Args:
            self:
            clk (int): clock time

        Returns:
            None:
        """

        # Extract flags to a temp variable
        newflags: int = self.flags

        # Set the flag bit
        newflags |= 1

        # Recompile packet with new clock sync
        self.recompile(newflags, clk = clk.to_bytes(4, 'big'))

        # Save the new flags
        self.flags: int = newflags

    def add_paramlist(self: Self, paramlist: list[bytes]):
        """Adds parameters.

        Args:
            self:
            paramlist (list[bytes]): list of parameters
        """

        # Extract flags to a temp variable
        newflags: int = self.flags

        # Set the flag bit
        newflags |= 2

        # Recompile packet with new paramlist
        self.recompile(newflags, paramlist = paramlist)

        # Save the new flags
        self.flags: int = newflags

    def add_devices(self: Self, onoff: bool, devices: int) -> None:
        """Adds device parameter

        Args:
            self:
            onoff (bool): Should the devices be turned on or off?
            devices (int): Devices to affect

        Returns:
            None:
        """

        # Extract flags to a temp variable
        newflags: int = self.flags

        # Set the flag bits
        newflags |= 8
        if onoff: newflags |= 4
        else: newflags &= ~4

        # Recompile packet with new devices
        self.recompile(newflags, devices = devices.to_bytes(1, 'big'))

        # Save the new flags
        self.flags: int = newflags

    def decompile(self: Self) -> tuple[Optional[bytes], Optional[list[bytes]], Optional[bytes]]:
        """Decompiles the packet and extracts parameters

        Args:
            self:

        Returns:
            tuple[Optional[bytes], Optional[list[bytes]], Optional[bytes]]: Decompiled parameters
        """

        # Set variables
        cursor: int = 0
        clk: Optional[bytes] = None
        devices: Optional[bytes] = None
        paramlist: Optional[bytes] = None

        # Decompile clock sync
        if self.flags & 1 > 0:
            clk: bytes = self.packet[cursor:cursor+4]
            cursor += 4

        # Decompile params
        if self.flags & 2 > 0:
            paramnum: int = self.packet[cursor]
            cursor += 1

            paramlist: list[bytes] = []
            for _ in range(paramnum):
                paramid: int = self.packet[cursor]
                paramsize: int = self.packet[cursor+1]
                cursor += 2

                paramdata: bytes = self.packet[cursor:cursor+paramsize]
                cursor += paramsize

                parambytes: bytes = paramid.to_bytes(1, 'big') + paramsize.to_bytes(1, 'big') + paramdata

                paramlist.append(parambytes)

            cursor += 1

        # Decompile devices
        if self.flags & 8 > 0:
            devices: bytes = self.packet[cursor].to_bytes(1, 'big')
            cursor += 1

        return (clk, paramlist, devices)

    def recompile(self: Self, newflags: int, **kwargs: Union[bytes, list[bytes]]) -> None:
        """Recompiles the packet with new parameters

        Args:
            self:
            kwargs (Union[bytes, list[bytes]]): Parameters

        Returns:
            None:
        """

        # Decompile the parameters
        decompiled: tuple[Optional[bytes], Optional[list[bytes]], Optional[bytes]] = self.decompile()
        clk: Optional[bytes] = decompiled[0]
        paramlist: Optional[list[bytes]] = decompiled[1]
        devices: Optional[bytes] = decompiled[2]

        # Reset packet
        self.packet: bytes = b''

        # Add new clock or add the old one back
        if newflags & 1 > 0:
            clk: bytes = kwargs.get('clk', clk)
            if not clk:
                raise ValueError('clk not set')
            self.packet += clk

        if newflags & 2 > 0:
            paramlist: list[bytes] = kwargs.get('paramlist', paramlist)
            if not paramlist:
                raise ValueError('paramlist not set')
            self.packet += len(paramlist).to_bytes(1, 'big')
            for param in paramlist: self.packet += param

        # Add new devices or add the old one back
        if newflags & 8 > 0:
            devices: bytes = kwargs.get('devices', devices)
            if not devices:
                raise ValueError('devices not set')
            self.packet += devices
