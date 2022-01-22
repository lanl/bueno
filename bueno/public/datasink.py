#
# Copyright (c) 2021-2022 Triad National Security, LLC
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

import copy
import logging
import ssl
import time

import pika  # type: ignore
import lark

from bueno.public import logger
from bueno.public import utils

# InfluxDBMeasurement value types
_IDBSimple = Union[str, int, float, bool]
_InfluxDBValueType = Dict[str, Union[_IDBSimple, Dict[str, _IDBSimple]]]


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
        self.rows: List[Any] = []
        self.maxcollens: List[Any] = []

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


class Measurement(ABC):
    '''
    Abstract measurement type.
    '''
    def __init__(self, verify_data: bool = False):
        self.verify_data = verify_data

    @abstractmethod
    def data(self) -> str:
        '''
        Returns measurement data as string following a given line protocol.
        '''


class _InfluxLineProtocolParser():
    def __init__(self) -> None:
        self.grammar = '''
            line: name SPACE fields SPACE UNIX_TIME NEWLINE
                | name COMMA tags SPACE fields SPACE UNIX_TIME NEWLINE

            tags: tag
                | tag COMMA tags

            tag: tag_key EQUALS tag_value

            fields: field
                  | field COMMA fields

            field: field_key EQUALS field_value

            name: INFLUX_NAME

            tag_key: INFLUX_NAME

            tag_value: STRING
                     | SIGNED_INT

            field_key: INFLUX_NAME

            field_value: SIGNED_FLOAT
                       | SIGNED_INT
                       | DOUBLE_QUOTED_STRING
                       | BOOL

            UNIX_TIME: SIGNED_INT

            STRING: ("_"|"."|"-"|LETTER|DIGIT)+

            BOOL: "True"
                | "False"

            COMMA: ","

            EQUALS: "="

            SPACE: " "

            INFLUX_NAME: (LETTER|DIGIT) STRING*

            NEWLINE: LF

            DOUBLE_QUOTED_STRING: ESCAPED_STRING

            %import common.DIGIT
            %import common.ESCAPED_STRING
            %import common.LF
            %import common.LETTER
            %import common.SIGNED_FLOAT
            %import common.SIGNED_INT
        '''

    class _Transformer(lark.Transformer):  # type: ignore
        def INFLUX_NAME(  # pylint: disable=invalid-name,no-self-use
            self,
            tok: lark.Token
        ) -> lark.Token:
            '''
            Handles INFLUX_NAME tokens, making sure they conform to the
            protocol's requirements.
            '''
            stok = str(tok)
            if stok.startswith('_'):
                line = tok.line
                col = tok.column
                ers = f'At line {line}, column {col}: Influx names ' \
                      f'cannot start with an underscore: {stok}'
                raise SyntaxError(ers)
            return tok

    def parse(self, istr: str) -> None:
        '''
        Attempts to parse the provided input. Raises an exception if parsing
        fails.
        '''
        parser = lark.Lark(
            self.grammar,
            parser='lalr',
            start='line',
            transformer=_InfluxLineProtocolParser._Transformer()
        )
        parser.parse(istr)


def _unroll_dict_impl(
    indict: Dict[str, Any], udict: Dict[str, Any]
) -> Dict[str, Any]:
    # Base case
    if len(indict) == 0:
        return udict
    # Not base case
    inkey = list(indict.keys())[0]
    inval = indict[inkey]
    # inval is not dictionary.
    if not isinstance(inval, dict):
        if inkey in udict.keys():
            pvw = f'Previous value was {udict[inkey]}.'
            raise ValueError(
                f'Duplicate key generated for {{{inkey}: {inval}}}. {pvw}'
            )
        udict[inkey] = inval
        del indict[inkey]
        return _unroll_dict_impl(indict, udict)
    # inval is a dictionary.
    if len(inval) == 0:
        del indict[inkey]
        return _unroll_dict_impl(indict, udict)
    valkey = list(inval.keys())[0]
    valval = inval.pop(valkey)
    new_key = f'{inkey}_{valkey}'
    if new_key in indict.keys():
        pvw = f'Previous value was {indict[new_key]}.'
        raise ValueError(
            f'Duplicate key generated for {{{new_key}: {valval}}}. {pvw}'
        )
    indict[new_key] = valval
    return _unroll_dict_impl(indict, udict)


def _unroll_dict(indict: Dict[str, Any]) -> Dict[str, Any]:
    tmpd: Dict[str, Any] = {}
    indict_copy = copy.deepcopy(indict)
    return _unroll_dict_impl(indict_copy, tmpd)


class InfluxDBMeasurement(Measurement):
    '''
    InfluxDB measurement type.
    '''
    def __init__(
        self,
        measurement: str,
        values: _InfluxDBValueType,
        tags: Optional[Dict[str, str]] = None,
        verify_data: bool = False
    ) -> None:
        super().__init__(verify_data)
        self.time = str(int(time.time()) * 1000000000)
        self.measurement = utils.chomp(measurement)
        self.values = _unroll_dict(values)
        if tags:
            self.tags = _unroll_dict(tags)
        else:
            self.tags = {}

    @staticmethod
    def _format_key(item: Any) -> str:
        '''
        Formats a key for the line protocol.
        '''
        if isinstance(item, str):
            item = item.replace(',', r'\,')
            item = item.replace(' ', r'\ ')
            item = item.replace('=', r'\=')

        return str(item)

    @staticmethod
    def _format_value_value(item: Any) -> str:
        '''
        Formats a value's value for the line protocol.
        '''
        if isinstance(item, str):
            item = F'"{item}"'

        return str(item)

    @staticmethod
    def _format_tag_value(item: Any) -> str:
        '''
        Formats a tag's value for the line protocol.
        '''
        istr = str(item)
        istr = istr.replace(' ', '_')
        return istr

    def _values(self) -> str:
        '''
        Returns values in line protocol format.
        '''
        kfmt = InfluxDBMeasurement._format_key
        vfmt = InfluxDBMeasurement._format_value_value
        return ','.join(F'{kfmt(k)}={vfmt(v)}' for k, v in self.values.items())

    def _tags(self) -> str:
        '''
        Returns tags in line protocol format.
        '''
        kfmt = InfluxDBMeasurement._format_key
        vfmt = InfluxDBMeasurement._format_tag_value
        return ','.join(F'{kfmt(k)}={vfmt(v)}' for k, v in self.tags.items())

    def data(self) -> str:
        '''
        Returns measurement data as string following InfluxDB line protocol.
        Raises an exception if data verification is enabled and the data do not
        adhere to the InfluxDB line protocol.
        '''
        result = '{}{} {} {}\n'.format(
            self.measurement,
            ',' + self._tags() if self.tags else '',
            self._values(),
            self.time
        )
        if self.verify_data:
            _InfluxLineProtocolParser().parse(result)
        return result


class TLSConfig:
    '''
    A straightforward Transport Layer Security (TLS) configuration container.
    '''
    def __init__(
        self,
        certfile: str,
        keyfile: str
    ) -> None:
        self.certfile = certfile
        self.keyfile = keyfile

        self.ssl_context = ssl.SSLContext()

        self.ssl_context.load_cert_chain(
            self.certfile,
            self.keyfile
        )


class RabbitMQConnectionParams:
    '''
    A straightforward RabbitMQ broker configuration container.
    '''
    def __init__(  # pylint: disable=too-many-arguments
        self,
        host: str,
        port: int,
        vhost: str = '/',
        connection_attempts: int = 2,
        heartbeat: int = 360,                   # In seconds
        blocked_connection_timeout: int = 300,  # In seconds
        tls_config: Optional[TLSConfig] = None
    ) -> None:
        self.host = host
        self.port = port
        self.vhost = vhost
        self.connection_attempts = connection_attempts
        self.heartbeat = heartbeat
        self.blocked_connection_timeout = blocked_connection_timeout
        self.tls_config = tls_config


class RabbitMQBlockingClient:  # pylint: disable=too-many-instance-attributes
    '''
    A straightforward AMQP 0-9-1 blocking client interface that ultimately wraps
    Pika.
    '''
    def __init__(  # pylint: disable=too-many-arguments
        self,
        conn_params: RabbitMQConnectionParams,
        queue_name: str,
        exchange: str,
        routing_key: str,
        verbose: bool = False,
    ) -> None:
        self.conn_params = conn_params
        self.queue_name = queue_name
        self.exchange = exchange
        self.routing_key = routing_key

        # Set pika logging level based on verbosity level.
        if not verbose:
            logging.getLogger("pika").setLevel(logging.WARNING)

    def send(self, measurement: Measurement, verbose: bool = False) -> None:
        '''
        Sends the contexts of measurement to the MQ server.
        '''
        # Establish the connection for each send. We do this because if the main
        # thread creates an instance and we initialize a connection there, then
        # long-running jobs may cause timeouts. This gets around that problem.
        connp = self.conn_params
        ssl_options = None
        if connp.tls_config is not None:
            ssl_context = connp.tls_config.ssl_context
            ssl_options = pika.SSLOptions(ssl_context, connp.host)

        credentials = pika.credentials.ExternalCredentials()
        connection_params = pika.ConnectionParameters(
            host=connp.host,
            port=connp.port,
            virtual_host=connp.vhost,
            connection_attempts=connp.connection_attempts,
            heartbeat=connp.heartbeat,
            blocked_connection_timeout=connp.blocked_connection_timeout,
            credentials=credentials,
            ssl_options=ssl_options
        )

        with pika.BlockingConnection(connection_params) as connection:
            channel = connection.channel()
            channel.confirm_delivery()
            msg = measurement.data()
            try:
                channel.basic_publish(
                    exchange=self.exchange,
                    routing_key=self.routing_key,
                    body=msg,
                    mandatory=True
                )
                if verbose:
                    logger.log(F'{type(self).__name__} sent: ({msg.rstrip()})')
            except pika.exceptions.UnroutableError:
                logger.log(F'Error sending the following message: {msg}')


# vim: ft=python ts=4 sts=4 sw=4 expandtab
