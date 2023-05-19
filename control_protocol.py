# control_protocol.py

from typing import Union, Optional, Self
import struct
import json

class ControlPacket():
    """Control Protocol Packet.
    """

    # Global Variables
    _packet: bytes = b''
    _flags: int = 0

    def __init__(self: Self, manifest_file: str = '') -> None:
        """Initialize the packet.

        Args:
            self (Self): self
        """

        # Read in the parameter oracle
        with open('param_oracle.json', 'r') as fp:
            self._param_oracle = json.load(fp)

        if manifest_file != '':
            self.create_from_manifest(manifest_file)

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
        decompiled: tuple[Optional[bytes], Optional[list[bytes]], Optional[bytes]] = self._decompile()
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
                # Print each byte as binary
                for byte in param[2:]:
                    print(f"{byte:08b}", end="")
                print("")
            print("")

        # Print devices in binary notation
        if devices:
            devices_int: int = int.from_bytes(devices, 'big')
            print("Devices:")
            print(f"{devices_int:08b}")
            print("")

    def create_from_manifest(self: Self, manifest_file: str) -> None:
        with open(manifest_file, 'r') as fp:
            manifest: dict = json.load(fp)

        self.add_clksync(manifest["time"])

        for param in manifest["parameters"]:
            self.add_parameter(param["name"], param["value"])

        self.add_devices(
                manifest["device_signals"]["state"],
                manifest["device_signals"]["devices"]
                )

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
        self._recompile(newflags, clk = clk.to_bytes(4, 'big'))

        # Save the new flags
        self._flags: int = newflags

    def add_parameter(
            self: Self,
            param_id: Union[int, str],
            param_data: Union[bool, int, float]
            ) -> None:
        """Adds a new parameter.

        Args:
            self (Self): self
            param_id (int): ID of the parameter
            param_data (Union[float, int, bool]): The data of the parameter

        Returns:
            None:

        Raises:
            ValueError: Invalid id
        """

        # Extract flags to a temp variable
        newflags: int = self._flags

        # Set the flag bit
        newflags |= 2

        # Create a new parameter
        param: bytes = b''

        # Variable to hold the name of the param
        pname: str = ''

        # Make variable to hold the param type
        ptype: str = ''

        # Make variable to check if the id is valid
        valid: bool = False

        # Check if id is valid
        match param_id:
            # If we use a integer as the id
            case int():
                for item in self._param_oracle.items():
                    if item[1]['id'] == param_id:
                        valid: bool = True
                        pname: str = item[0]
                        ptype: str = item[1]['type']
                        break

            # If we used the name
            case str():
                # Set the pname to the param_id
                pname: str = param_id

                # Find the correct id for the name
                item = self._param_oracle.get(pname, None)

                # If we found the item set valid, param_id and type
                if item:
                    valid: bool = True
                    param_id: int = item['id']
                    ptype: str = item['type']

            case _:
                # TODO: better error
                raise ValueError("Hell is burning")

        # if it is not a valid id raise an error
        if not valid:
            raise ValueError("Invalid param id or param name")

        # Add id to the parameter
        param += param_id.to_bytes(1, 'big')

        # Create temporary variables to hold the size and byte data
        psize: int = 0
        pdata: bytes = b''

        # Inner method to check if the ptype is of allowed type
        def check_allowed_type(types: list[str]) -> None:
            if not ptype in types:
                raise ValueError(f'{pname} ({param_id}) cannot be in {types}')

        # Check what type of data we need to add
        match param_data:
            # If integer or boolean (booleans are 0 and 1)
            case int():
                # Check if param_data is allowed to be a bool or int
                check_allowed_type(['bool', 'int'])

                # Calculate size of parameter data
                psize: int = (param_data.bit_length() + 7) // 8

                # Make sure that we have at least one byte (0 and False give 0)
                psize = psize if psize > 0 else 1

                # Convert integer to bytes
                pdata: bytes = param_data.to_bytes(psize, 'big')

            # If floating point
            case float():
                # Check if param_data is allowed to be a float
                check_allowed_type(['float'])

                # Set the size of parameter data
                psize: int = 8

                # Pack the float with struct
                pdata: bytes = struct.pack('>d', param_data)

            # Default case/fallback
            case _:
                raise ValueError("Parameter data not of accepted type")

        # Set the calculated size and data
        param += psize.to_bytes(1, 'big')
        param += pdata

        self._recompile(newflags, param = param)

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
        self._recompile(newflags, devices = devices.to_bytes(1, 'big'))

        # Save the new flags
        self._flags: int = newflags

    def _decompile(self: Self) -> tuple[Optional[bytes], Optional[list[bytes]], Optional[bytes]]:
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

            # Make variable to collect parameters in
            paramlist: list[bytes] = []

            # Loop over all parameters
            for _ in range(paramnum):

                # Collect their id and size
                paramid: int = self._packet[cursor]
                paramsize: int = self._packet[cursor+1]
                cursor += 2

                # Collect the data bytes
                paramdata: bytes = self._packet[cursor:cursor+paramsize]
                cursor += paramsize

                # Recreate the parameter bytes
                parambytes: bytes = paramid.to_bytes(1, 'big') + paramsize.to_bytes(1, 'big') + paramdata

                # Add the bytes to the list
                paramlist.append(parambytes)

        # Decompile devices
        if self._flags & 8 > 0:
            devices: bytes = self._packet[cursor].to_bytes(1, 'big')
            cursor += 1

        # Return the decompiled packet
        return (clk, paramlist, devices)

    def _recompile(self: Self, newflags: int, **kwargs: bytes) -> None:
        """Recompiles the packet with new parameters

        Args:
            self (Self): self
            kwargs (Union[bytes, list[bytes]]): Data to add

        Returns:
            None:

        Raises:
            ValueError: Packet part is not set
        """

        # Decompile the parameters
        decompiled: tuple[Optional[bytes], Optional[list[bytes]], Optional[bytes]] = self._decompile()
        clk: Optional[bytes] = decompiled[0]
        paramlist: Optional[list[bytes]] = decompiled[1]
        devices: Optional[bytes] = decompiled[2]

        # Reset packet
        self._packet: bytes = b''

        # Add new clock or add the old one back
        if newflags & 1 > 0:

            # Extract new clock from the arguments
            clk: bytes = kwargs.get('clk', clk)

            # Check that the clock is set,
            # either from arguments or decompiled packet
            if not clk:
                raise ValueError('clk not set')

            # Add the clock bytes
            self._packet += clk

        # Add new parameter to the list,
        # or compile the old one back
        if newflags & 2 > 0:

            # Extract parameter from the arguments
            param: bytes = kwargs.get('param', None)

            # Check if we have a parameter list from the packet
            if not paramlist:

                # Make sure that we have a new parameter set
                if not param:
                    raise ValueError('paramlist or param not set')

                # Make an empty parameter list
                paramlist = []

            # Check that we have a new parameter set
            if param:
                # Make index variable to track where
                # the new parameter needs to be inserted
                index = -1

                # Loop through all parameter and check
                # if we already have one with the same id
                for i, p in enumerate(paramlist):
                    if p[0] == param[0]:
                        # If we do save the index
                        index = i
                        break

                if index > 0:
                    # If we saved an index replaced the parameter
                    # at that index with our new parameter
                    paramlist: list[bytes] = paramlist[:i] + \
                            [param] + \
                            paramlist[i+1:]
                else:
                    # Else just append it
                    paramlist.append(param)

            # Write the parameter length
            self._packet += len(paramlist).to_bytes(1, 'big')

            # Sort and reorder the parameters by id
            # Make a list to hold the ordering
            # contents: (id, index)
            order_list: list[tuple[int, int]] = []

            # Loop over all parameters,
            # add their id and index to the list
            for i, p in enumerate(paramlist):
                order_list.append((p[0], i))

            # Sort the list by the id
            order_list.sort(key=lambda x: x[0])

            # Add the parameters in order from the list
            for _, index in order_list:
                self._packet += paramlist[index]

        # Add new device signal or add the old one back
        if newflags & 8 > 0:

            # Extract device signal from arguments
            devices: bytes = kwargs.get('devices', devices)

            # Check that a device signal is set,
            # either from arguments or decompiled packet
            if not devices:
                raise ValueError('devices not set')

            # Add device signal bytes
            self._packet += devices
