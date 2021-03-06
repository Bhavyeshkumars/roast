#
# Copyright (c) 2020 Xilinx, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#

import time
from abc import ABCMeta, abstractmethod
from stevedore import driver
from roast.utils import register_plugin


class RelayBase(metaclass=ABCMeta):
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnects relay."""

    @abstractmethod
    def connect(self) -> None:
        """Connects relay."""

    @abstractmethod
    def reconnect(self, seconds: int) -> None:
        """Disconnects for specified time and reconnects.

        Args:
            seconds (int): Amount of time to sleep between disconnect and connect.
        """


class Relay:
    def __init__(self, relay_type: str, **kwargs) -> None:
        if relay_type is None:
            relay_type = "dummy_relay"
            kwargs = {}
            register_plugin(
                __file__,
                "dummy_relay",
                "relay",
                "roast.component.board.relay:DummyRelay",
            )
        self._relay_mgr = driver.DriverManager(
            namespace="roast.relay",
            name=relay_type,
            invoke_on_load=True,
            invoke_kwds=kwargs,
        )

    @property
    def driver(self):
        return self._relay_mgr.driver

    def disconnect(self) -> None:
        self.driver.disconnect()

    def connect(self) -> None:
        self.driver.connect()

    def reconnect(self, seconds: int = 5) -> None:
        self.driver.reconnect(seconds)


class DummyRelay(RelayBase):
    def __init__(self):
        super().__init__()

    def disconnect(self):
        self.disconnected = True

    def connect(self):
        self.connected = True

    def reconnect(self, seconds: int = 5):
        self.reconnected = True
        self.seconds = seconds


class UsbRelay(RelayBase):
    def __init__(self, session):
        self._session = session
        self.expected_failures = "J283"
        self.expected = session.host

    def disconnect(self):
        cmd = "sudo usb_relay off"
        self._session.host_console.runcmd(
            cmd, self.expected_failures, self.expected, wait_for_prompt=False
        )

    def connect(self):
        cmd = "sudo usb_relay on"
        self._session.host_console.runcmd(
            cmd, self.expected_failures, self.expected, wait_for_prompt=False
        )

    def reconnect(self, seconds=5):
        self.disconnect()
        time.sleep(seconds)
        self.connect()
