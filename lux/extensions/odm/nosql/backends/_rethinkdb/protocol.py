import struct

from rethinkdb import ql2_pb2 as p
from rethinkdb.net import Query, Response, Cursor
from rethinkdb.ast import RqlQuery, DB, recursively_convert_pseudotypes
from rethinkdb.errors import *

from pulsar import ProtocolConsumer, Connection

pResponse = p.Response.ResponseType
pQuery = p.Query.QueryType
SequenceResponse = frozenset((pResponse.SUCCESS_PARTIAL,
                              pResponse.SUCCESS_SEQUENCE))


def start_query(term, token, options):
    return Query(pQuery.START, token, term, options)


class Consumer(ProtocolConsumer):
    _response_buf = None

    def start_request(self):
        query = self.request
        if self.connection.requests_processed == 1:
            msg = (struct.pack("<2L", p.VersionDummy.Version.V0_3,
                               len(query)) + query +
                   struct.pack("<L", p.VersionDummy.Protocol.JSON))
            self.write(msg)
        else:
            query_str = query.serialize().encode('utf-8')
            query_header = struct.pack("<QL", query.token, len(query_str))
            self.write(query_header + query_str)

    def data_received(self, data):
        if self._response_buf:
            data = self._response_buf + data

        try:
            value = None
            if self.connection.requests_processed == 1:
                if b'\0' in data:
                    idx = data.index(b'\0')
                    msg, data = data[:idx], data[idx+1:]
                    if msg != b'SUCCESS':
                        raise RqlDriverError(
                            'Server dropped connection: "%s"' %
                            msg.decode('utf-8').strip())
            elif len(data) >= 12:
                buf, data = data[:12], data[12:]
                token, size = struct.unpack("<qL", buf)
                if len(data) >= size:
                    buf, data = data[:size], data[size:]
                    response = Response(token, buf)
                    if data:
                        raise RqlDriverError('protocol error')
                    elif response.token != self.request.token:
                        raise RqlDriverError('Unexpected response token')
                    value = self._check_response(response)
                else:
                    data = buf + data
        except Exception as exc:
            self.finished(exc=exc)
        else:
            self._response_buf = data
            if not data:
                self.finished(value)

    def is_open(self):
        if self._connection:
            return not self._connection.closed
        return False

    def _check_error_response(self, response, term):
        if response.type == pResponse.RUNTIME_ERROR:
            message = response.data[0]
            frames = response.backtrace
            raise RqlRuntimeError(message, term, frames)
        elif response.type == pResponse.COMPILE_ERROR:
            message = response.data[0]
            frames = response.backtrace
            raise RqlCompileError(message, term, frames)
        elif response.type == pResponse.CLIENT_ERROR:
            message = response.data[0]
            frames = response.backtrace
            raise RqlClientError(message, term, frames)

    def _check_response(self, response):
        query = self.request
        term = query.term
        opts = query.global_optargs
        self._check_error_response(response, term)
        if response.type in SequenceResponse:
            # Sequence responses
            value = Cursor(self, query, opts)
            value._extend(response)
        elif response.type == pResponse.SUCCESS_ATOM:
            # Atom response
            if len(response.data) < 1:
                value = None
            value = recursively_convert_pseudotypes(response.data[0], opts)
        elif response.type == pResponse.WAIT_COMPLETE:
            # Noreply_wait response
            return None
        else:
            # Default for unknown response types
            raise RqlDriverError("Unknown Response type %d encountered in "
                                 "response." % response.type)

        if response.profile is not None:
            value = {"value": value, "profile": response.profile}

        return value
