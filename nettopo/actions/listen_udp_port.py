#!python

import os
import sys
import datetime
import time
import socket


def listen_on_udp_port():
    """listen_on_udp_port

    Run a simple server for processing messages over ``UDP``.

    ``UDP_LISTEN_ON_HOST`` - listen on this host ip address

    ``UDP_LISTEN_ON_PORT`` - listen on this ``UDP`` port

    ``UDP_LISTEN_SIZE`` - listen on to packets of this size

    ``UDP_LISTEN_SLEEP`` - sleep this number of seconds per loop

    ``UDP_LISTEN_SHUTDOWN_HOOK`` - shutdown if file is found on disk

    """

    host = os.getenv(
        "UDP_LISTEN_ON_HOST",
        "127.0.0.1").strip().lstrip()
    port = int(os.getenv(
        "UDP_LISTEN_ON_PORT",
        "17000").strip().lstrip())
    backlog = int(os.getenv(
        "UDP_LISTEN_BACKLOG",
        "5").strip().lstrip())
    size = int(os.getenv(
        "UDP_LISTEN_SIZE",
        "1024").strip().lstrip())
    sleep_in_seconds = float(os.getenv(
        "UDP_LISTEN_SLEEP",
        "0.5").strip().lstrip())
    shutdown_hook = os.getenv(
        "UDP_LISTEN_SHUTDOWN_HOOK",
        "/tmp/udp-shutdown-listen-server-{}-{}".format(
            host,
            port)).strip().lstrip()

    if os.path.exists(shutdown_hook):
        print(("Please remove the UDP shutdown hook file: "
               "\nrm -f {}")
              .format(shutdown_hook))
        sys.exit(1)

    now = datetime.datetime.now().isoformat()
    print(("{} - Starting UDP Server address={}:{} "
           "backlog={} size={} sleep={} shutdown={}")
          .format(
            now,
            host,
            port,
            backlog,
            size,
            sleep_in_seconds,
            shutdown_hook))

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))

    msg = 0
    while 1:
        data = None
        address = None

        data, address = s.recvfrom(4096)

        if data:
            now = datetime.datetime.now().isoformat()
            print(("{} received UDP data={} ")
                  .format(
                    now,
                    data))
            msg += 1
            if msg > 1000000:
                msg = 0

            # if address:
            #     client.sendto("PROCESSED", address)
        else:
            time.sleep(sleep_in_seconds)

        if os.path.exists(shutdown_hook):
            now = datetime.datetime.now().isoformat()
            print(("{} detected shutdown "
                   "file={}")
                  .format(
                    now,
                    shutdown_hook))

    # end of loop

    print("Shutting down")

# end of listen_on_udp_port


if __name__ == '__main__':
    listen_on_udp_port()
