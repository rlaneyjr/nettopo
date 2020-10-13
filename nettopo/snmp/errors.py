class NettopoSNMPError(Exception):
    pass

class NettopoTypeError(Exception):
    pass

class ArgumentError(NettopoSNMPError):
    pass


class SnmpError(NettopoSNMPError):
    pass
