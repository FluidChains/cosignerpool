#!/usr/bin/env python3
#
# Electrum - lightweight Bitcoin client
# Copyright (C) 2015 Thomas Voegtlin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import time
import calendar
import traceback
import threading

from socketserver import ThreadingMixIn
from xmlrpc.server import SimpleXMLRPCServer

import plyvel
from apscheduler.schedulers.background import BackgroundScheduler

from log_models import MyLoggerFactory

r_count, w_count = 0, 0
rmutex, wmutex = threading.Lock(), threading.Lock()
readTry, rw_mutex = threading.Lock(), threading.Lock()

class SimpleThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

def run_server(host, port, logger):

    server_addr = (host, port)
    server = SimpleThreadedXMLRPCServer(server_addr, logRequests=False, allow_none=True)

    server.register_function(delete, 'delete')
    server.register_function(get, 'get')
    server.register_function(put, 'put')
    server.register_function(announce, 'announce')
    server.register_function(message, 'message')
    server.register_function(ping, 'ping')
    server.register_function(get_current_time, 'get_current_time')
    server.running = True

    while server.running:
        try:
            server.handle_request()
        except KeyboardInterrupt:
            logger.info("Shutting down server")
            sys.exit(0)
        except Exception as e:
            logger.error(e)

    logger.info("Server stopped")

def get(key):
    """
    Get value from keystore, threadsafe.

    Arguments:
        key -- key to be retrieved
    """

    with readTry:
        with rmutex:
            global r_count
            r_count += 1
            if (r_count == 1):
                rw_mutex.acquire()

    o = db.get(key.encode("utf8"))
    if o:
        logger.info("GET :: {}, {}".format(key, len(o)))

    with rmutex:
        r_count -= 1
        if (r_count == 0):
            rw_mutex.release()

    return o.decode("utf8") if o else None

def put(key, value):
    """
    Put value on keystore, threadsafe.

    Arguments:
        key -- key to be added
        value -- value to be stored
    """

    with wmutex:
        global w_count
        w_count += 1
        if (w_count == 1):
            readTry.acquire()

    with rw_mutex:
        logger.info("PUT :: {}, {}".format(key, len(value)))
        db.put(key.encode("utf8"), value.encode("utf8"))

    with wmutex:
        w_count -= 1
        if (w_count == 0):
            readTry.release()


def delete(key):
    """
    Delete value from keystore, threadsafe.

    Arguments:
        key -- key to be removed
    """

    with wmutex:
        global w_count
        w_count += 1
        if (w_count == 1):
            readTry.acquire()

    with rw_mutex:
        logger.info("DEL :: {}".format(key))
        db.delete(key.encode("utf8"))

    with wmutex:
        w_count -= 1
        if (w_count == 0):
            readTry.release()


def announce(idx):
    """
    Function to announce connection from client. Ensures connection is
    alive and secure.

    Arguments:
        idx -- wallet id
    """

    logger.info("ANN :: announcing {}".format(idx))

def message(idx, msg):
    """
    Forward debug message, from client, to logger. Multi-purpose.

    Arguments:
        idx -- wallet id
        msg -- message to send to logger
    """

    logger.debug("MSG :: {}, {}".format(idx, msg))

def ping():
    """
    Return 'pong' if server is alive.
    """

    return 'pong'

def get_current_time():
    """
    Return current time on server.
    """

    return calendar.timegm(time.gmtime())

def collect_garbage(db, logger):
    """
    Delete any locks that are older than 10 minutes

    Arguments:
        db -- database connection
    """

    for index, kv, in enumerate(db):
        key, value = str(kv[0].decode('utf8')), kv[1]
        # we only want locks
        if "_lock" not in key:
            continue
        # if lock timestamp is greater than 10 minutes
        expired = (calendar.timegm(time.gmtime()) - int(value)) > (10 * 60)
        if expired:
            db.delete(key.encode('utf8'))
            logger.info("GBG :: {}:{}".format(key, value))

if __name__ == '__main__':

    # set logger
    logger = MyLoggerFactory.getLogger('cosignerpool')
    logger.setLevel('DEBUG')

    # set default host and port
    host = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
    port = sys.argv[2] if len(sys.argv) > 2 else 8080

    my_host = os.environ.get("LISTEN_HOST", host)
    my_port = int(os.environ.get("LISTEN_PORT", port))

    try:
        dbpath = '/db_cosigner'
    except KeyError as e:
        logger.error("Required variable {} not set".format(e))
        sys.exit(1)

    # create or set leveldb database at '/db_cosigner'
    db = plyvel.DB(dbpath, create_if_missing=True, compression=None)

    # start and configure scheduler for garbage collection
    scheduler = BackgroundScheduler()
    scheduler.start()
    job = scheduler.add_job(collect_garbage, 'interval', [db, logger], seconds=30)

    logger.info("Server starting on {}:{}".format(my_host, my_port))
    print("Server started. See '../log/server.log' for more information")
    run_server(my_host, my_port, logger)

    job.remove()
    db.close()
