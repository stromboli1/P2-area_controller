from typing import Union, Optional, Self
import struct

class ControlPacket():
    """Control Protocol Packet.
    """

    # Global Variables
    _packet: bytes = b''
    _flags: int = 0

    def __init__(self: Self):
        """Initialize the packet.

        Args:
            self (Self): self
        """

    def __repr__(self: Self) -> str:
        """Represent packet as a hex string

        Args:
            self (Self): self

        Returns:
            str: packet as hex
        """

        return self.get_packet().hex()

    def get_packet(self: Self) -> bytes:
        """Method to get the full packet.

        Args:
            self (Self): self

        Returns:
            bytes: Packet with flags appended
        """

        return self._flags.to_bytes(1, 'big') + self._packet

    def print_packet(self: Self) -> None:
        """Method for printing packet in a readable manner.

        Args:
            self (Self): self

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
        print(f"{self._flags:08b}")
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
            self (Self): self
            clk (int): clock time

        Returns:
            None:
        """

        # Extract flags to a temp variable
        newflags: int = self._flags

        # Set the flag bit
        newflags |= 1

        # Recompile packet with new clock sync
        self.recompile(newflags, clk = clk.to_bytes(4, 'big'))

        # Save the new flags
        self._flags: int = newflags

    def add_parameter(self: Self, param_id: int, param_data: Union[float, int, bool]) -> None:
        """Adds a new parameter.

        Args:
            self (Self): self
            param_id (int): ID of the parameter
            param_data (Union[float, int, bool]): The data of the parameter

        Returns:
            None:
        """

        # Extract flags to a temp variable
        newflags: int = self._flags

        # Set the flag bit
        newflags |= 2

        # Create a new parameter
        param: bytes = b''

        # Add id to the parameter
        param += param_id.to_bytes(1, 'big')

        # Create temporary variables to hold the size and byte data
        psize: int = 0
        pdata: bytes = b''

        # Check what type of data we need to add
        match param_data:
            case float():
                # Set the size of parameter data
                psize: int = 8

                # Pack the float with struct
                pdata: bytes = struct.pack('>d', param_data)
            case bool():
                # Set the size of parameter data
                psize: int = 1

                # Make the bool a byte
                pdata: bytes = b'\x01' if param_data else b'\x00'
            case int():
                # Calculate size of parameter data
                psize: int = (param_data.bit_length() + 7) // 8

                # Convert integer to bytes
                pdata: bytes = param_data.to_bytes(psize, 'big')
            case _:
                raise ValueError("Parameter data not of accepted type")

        # Set the calculated size and data
        param += psize.to_bytes(1, 'big')
        param += pdata

        self.recompile(newflags, param = param)

        # Save the new flags
        self._flags: int = newflags

    def add_devices(self: Self, onoff: bool, devices: int) -> None:
        """Adds device parameter

        Args:
            self (Self): self
            onoff (bool): Should the devices be turned on or off?
            devices (int): Devices to affect

        Returns:
            None:
        """

        # Extract flags to a temp variable
        newflags: int = self._flags

        # Set the flag bits
        newflags |= 8
        if onoff: newflags |= 4
        else: newflags &= ~4

        # Recompile packet with new devices
        self.recompile(newflags, devices = devices.to_bytes(1, 'big'))

        # Save the new flags
        self._flags: int = newflags

    def decompile(self: Self) -> tuple[Optional[bytes], Optional[list[bytes]], Optional[bytes]]:
        """Decompiles the packet and extracts parameters

        Args:
            self (Self): self

        Returns:
            tuple[Optional[bytes], Optional[list[bytes]], Optional[bytes]]: Decompiled parameters
        """

        # Set variables
        cursor: int = 0
        clk: Optional[bytes] = None
        devices: Optional[bytes] = None
        paramlist: Optional[bytes] = None

        # Decompile clock sync
        if self._flags & 1 > 0:
            clk: bytes = self._packet[cursor:cursor+4]
            cursor += 4

        # Decompile params
        if self._flags & 2 > 0:
            paramnum: int = self._packet[cursor]
            cursor += 1

            paramlist: list[bytes] = []
            for _ in range(paramnum):
                paramid: int = self._packet[cursor]
                paramsize: int = self._packet[cursor+1]
                cursor += 2

                paramdata: bytes = self._packet[cursor:cursor+paramsize]
                cursor += paramsize

                parambytes: bytes = paramid.to_bytes(1, 'big') + paramsize.to_bytes(1, 'big') + paramdata

                paramlist.append(parambytes)

        # Decompile devices
        if self._flags & 8 > 0:
            devices: bytes = self._packet[cursor].to_bytes(1, 'big')
            cursor += 1

        return (clk, paramlist, devices)

    def recompile(self: Self, newflags: int, **kwargs: bytes) -> None:
        """Recompiles the packet with new parameters

        Args:
            self (Self): self
            kwargs (Union[bytes, list[bytes]]): Data to add

        Returns:
            None:
        """

        # Decompile the parameters
        decompiled: tuple[Optional[bytes], Optional[list[bytes]], Optional[bytes]] = self.decompile()
        clk: Optional[bytes] = decompiled[0]
        paramlist: Optional[list[bytes]] = decompiled[1]
        devices: Optional[bytes] = decompiled[2]

        # Reset packet
        self._packet: bytes = b''

        # Add new clock or add the old one back
        if newflags & 1 > 0:
            clk: bytes = kwargs.get('clk', clk)
            if not clk:
                raise ValueError('clk not set')
            self._packet += clk

        if newflags & 2 > 0:
            param: bytes = kwargs.get('param', None)
            if not paramlist and not param:
                raise ValueError('paramlist not set')
            elif param:
                # TODO: make us able to change an already set parameter
                paramlist = paramlist if paramlist else []
                paramlist.append(param)
            self._packet += len(paramlist).to_bytes(1, 'big')
            for param in paramlist: self._packet += param

        # Add new devices or add the old one back
        if newflags & 8 > 0:
            devices: bytes = kwargs.get('devices', devices)
            if not devices:
                raise ValueError('devices not set')
            self._packet += devices
