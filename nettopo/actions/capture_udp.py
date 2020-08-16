#!python

import kamene.all as kamene
from spylunking.log.setup_logging import console_logger
from celery_connectors.utils import ev
from network_pipeline.handle_packets import handle_packets


log = console_logger(
    name='cap_udp')


def capture_udp_packets():
    """capture_udp_packets

    Capture ``UDP`` packets and call the ``handle_packets`` method

    Change the network interface by ``export CAP_DEVICE=eth0``

    """
    dev = ev(
        "CAP_DEVICE",
        "lo")

    """
    Ignore ports for forwarding to consolidators:

    Redis VM: 6379, 16379
    RabbitMQ VM: 5672, 15672, 25672

    """

    # http://biot.com/capstats/bpf.html
    default_filter = "udp"
    custom_filter = ev(
        "NETWORK_FILTER",
        default_filter)

    log.info(("starting device={} filter={}")
             .format(
                dev,
                custom_filter))

    kamene.sniff(
        filter=custom_filter,
        prn=handle_packets)

    log.info("done")

# end of capture_udp_packets


if __name__ == "__main__":
    capture_udp_packets()
