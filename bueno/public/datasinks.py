#
# Copyright (c)      2021 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Convenience data sinks.
'''

from abc import ABC, abstractmethod
from typing import (
    Dict,
    Optional
)

import os
import socket
import ssl
import subprocess  # nosec
import time

from bueno.public import utils

MaybePopen = Optional[subprocess.Popen[bytes]]


class TelegrafClientAgent:
    '''
    A thin wrapper for telegraf client agent management.
    '''
    def __init__(self, exe: str, config: str) -> None:
        fnf = '{} does not exist'
        if not os.path.exists(exe):
            raise RuntimeError(fnf.format(exe))
        if not os.path.exists(config):
            raise RuntimeError(fnf.format(config))

        self.exe = exe
        self.config = config
        self.tele_process: MaybePopen = None  # pylint: disable=E1136

    def __del__(self) -> None:
        self.stop()

    def start(self) -> None:
        '''
        Starts the Telegraf client agent. Raises a RuntimeError on failure.
        '''
        cmd = [self.exe, '--config', self.config]
        self.tele_process = subprocess.Popen(cmd)  # nosec
        # Hack to give the subprocess a little time to startup.
        time.sleep(10)

    def stop(self) -> None:
        '''
        Stops the Telegraf client agent.
        '''
        if self.tele_process is not None:
            self.tele_process.terminate()
            self.tele_process = None


class Measurement(ABC):
    '''
   Abstract measurement type.
    '''
    @abstractmethod
    def data(self) -> str:
        '''
        Returns measurement data as string following a given line protocol.
        '''


class InfluxDBMeasurement(Measurement):
    '''
    InfluxDB measurement type.
    '''
    def __init__(
        self,
        measurement: str,
        values: Dict[str, str],
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        self.time = str(int(time.time()) * 1000000000)
        self.measurement = utils.chomp(measurement)
        self.values = values
        self.tags = tags or {}

    @staticmethod
    def _format_str(istr: str) -> str:
        '''
        Formats a string for the line protocol.
        '''
        istr = istr.replace(',', '\,')  # noqa: W605 pylint: disable=W1401
        istr = istr.replace(' ', '\ ')  # noqa: W605 pylint: disable=W1401
        istr = istr.replace('=', '\=')  # noqa: W605 pylint: disable=W1401

        return istr

    def _values(self) -> str:
        '''
        Returns values in line protocol format.
        '''
        fmt = InfluxDBMeasurement._format_str
        return ','.join(F'{fmt(k)}={fmt(v)}' for k, v in self.values.items())

    def _tags(self) -> str:
        '''
        Returns tags in line protocol format.
        '''
        fmt = InfluxDBMeasurement._format_str
        return ','.join(F'{fmt(k)}={fmt(v)}' for k, v in self.tags.items())

    def data(self) -> str:
        '''
        Returns measurement data as string following InfluxDB line protocol.
        '''
        return '{}{}{}{}'.format(
            self.measurement,
            ',' + self._tags() if self.tags else '',
            self._values(),
            self.time
        )


class TelegrafClient:
    '''
    A straightforward client interface for interacting with a Telegraf daemon.
    '''
    def __init__(
        self,
        ssl_key: str,
        ssl_cert: str,
        host: str = 'localhost',
        port: int = 5555
    ) -> None:
        self.host = host
        self.port = port
        self.ssl_key = ssl_key
        self.ssl_cert = ssl_cert
        self.sock: Optional[socket.socket] = None
        self.ssock: Optional[ssl.SSLSocket] = None

        self._connect()

    def __del__(self) -> None:
        if self.sock is not None:
            self.sock.close()
        if self.ssock is not None:
            self.ssock.close()

    def _connect(self) -> None:
        '''
        Private connection.
        '''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10)

        sslctx = ssl.SSLContext()
        sslctx.load_cert_chain(certfile=self.ssl_cert, keyfile=self.ssl_key)

        self.ssock = sslctx.wrap_socket(self.sock)

        try:
            self.ssock.connect((self.host, self.port))
        except Exception as exception:
            ers = 'Cannot connect to Telegraf client agent'
            raise RuntimeError(ers) from exception

    def send(self, measurement: Measurement) -> None:
        '''
        Sends the contexts of measurement to the Telegraf client agent.
        '''
        try:
            # To silence mypy warnings
            assert self.ssock is not None  # nosec
            self.ssock.write(measurement.data().encode('utf-8'))
        except Exception as exception:
            ers = 'Sending data to Telegraf client agent failed'
            raise RuntimeError(ers) from exception

# vim: ft=python ts=4 sts=4 sw=4 expandtab
