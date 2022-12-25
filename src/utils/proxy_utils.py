"""proxy utils."""

def format_proxy(proxy):
    """Convert list to dict."""
    host, port = proxy
    return {'http': str(host)+":"+str(port)}

    