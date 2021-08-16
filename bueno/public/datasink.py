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
    Any,
    Dict,
    List,
    Optional,
    Union
)

import os
import socket
import sys
import ssl
import subprocess  # nosec
import time

from bueno.public import logger
from bueno.public import utils

if sys.version_info < (3, 8):
    MaybePopen = Optional[subprocess.Popen]
else:
    MaybePopen = Optional[subprocess.Popen[bytes]]  # pylint: disable=E1136


class Table:
    '''
    A straightforward class to display formatted tabular data.
    '''
    class Row():
        '''
        Creates a row for use in a table.
        '''
        def __init__(self, data: List[Any], withrule: bool = False) -> None:
            self.data = data
            self.withrule = withrule

    class _RowFormatter():
        '''
        Private class used for row formatting.
        '''
        def __init__(self, mcls: List[int]) -> None:
            self.colpad = 2
            self.mcls = list(map(lambda x: x + self.colpad, mcls))
            self.fmts = str()
            # Generate format string based on max column lengths.
            for mcl in self.mcls:
                self.fmts += F'{{:<{mcl}s}}'

        def format(self, row: 'Table.Row') -> str:
            '''
            Formats the contents of a given row into a nice output string.
            '''
            res = str()
            res += self.fmts.format(*row.data)
            if row.withrule:
                res += '\n' + ('-' * (sum(self.mcls) - self.colpad))
            return res

    def __init__(self) -> None:
        self.rows: List[Any] = list()
        self.maxcollens: List[Any] = list()

    def addrow(self, row: List[Any], withrule: bool = False) -> None:
        '''
        Adds the contents of row to a table, optionally with a rule.
        '''
        if len(self.rows) == 0:
            ncols = len(row)
            self.maxcollens = [0] * ncols

        srow = list(map(str, row))
        maxlens = map(len, srow)

        self.maxcollens = list(map(max, zip(self.maxcollens, maxlens)))
        self.rows.append(Table.Row(srow, withrule))

    def emit(self) -> None:
        '''
        Emits the contents of the table using logger.log().
        '''
        rowf = Table._RowFormatter(self.maxcollens)
        for row in self.rows:
            logger.log(rowf.format(row))


class TelegrafClientAgent:
    '''
    A thin wrapper for telegraf client agent management.
    '''
    def __init__(self, exe: str, config: str, verbose: bool = False) -> None:
        self.verbose = verbose
        self.exe = exe
        self.config = config
        self.tele_process: MaybePopen = None

        fnf = '{} does not exist'
        if not os.path.exists(exe):
            raise RuntimeError(fnf.format(exe))
        if not os.path.exists(config):
            raise RuntimeError(fnf.format(config))

    def __del__(self) -> None:
        self.stop()

    def start(self) -> None:
        '''
        Starts the Telegraf client agent. Raises a RuntimeError on failure.
        '''
        cmd = [self.exe, '--config', self.config]
        self.tele_process = subprocess.Popen(  # nosec
            cmd,
            shell=False,
            stdout=None if self.verbose else subprocess.DEVNULL,
            stderr=None if self.verbose else subprocess.DEVNULL
        )
        # Hack to give the subprocess a little time to startup.
        time.sleep(5)

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
        values: Dict[str, Union[str, int, float, bool]],
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        self.time = str(int(time.time()) * 1000000000)
        self.measurement = utils.chomp(measurement)
        self.values = values
        self.tags = tags or {}

    @staticmethod
    def _format_item(item: Any) -> str:
        '''
        Formats an item for the line protocol.
        '''
        if isinstance(item, str):
            item = item.replace(',', '\,')  # noqa: W605 pylint: disable=W1401
            item = item.replace(' ', '\ ')  # noqa: W605 pylint: disable=W1401
            item = item.replace('=', '\=')  # noqa: W605 pylint: disable=W1401

        return str(item)

    def _values(self) -> str:
        '''
        Returns values in line protocol format.
        '''
        fmt = InfluxDBMeasurement._format_item
        return ','.join(F'{fmt(k)}={fmt(v)}' for k, v in self.values.items())

    def _tags(self) -> str:
        '''
        Returns tags in line protocol format.
        '''
        fmt = InfluxDBMeasurement._format_item
        return ','.join(F'{fmt(k)}={fmt(v)}' for k, v in self.tags.items())

    def data(self) -> str:
        '''
        Returns measurement data as string following InfluxDB line protocol.
        '''
        return '{}{} {} {}'.format(
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

    def send(self, measurement: Measurement, verbose: bool = False) -> None:
        '''
        Sends the contexts of measurement to the Telegraf client agent.
        '''
        try:
            # To silence mypy warnings
            assert self.ssock is not None  # nosec
            mdata = measurement.data()
            if verbose:
                logger.log(F'{type(self).__name__}:send({mdata})')
            self.ssock.write(mdata.encode('utf-8'))
        except Exception as exception:
            ers = 'Sending data to Telegraf client agent failed'
            raise RuntimeError(ers) from exception

# vim: ft=python ts=4 sts=4 sw=4 expandtab
