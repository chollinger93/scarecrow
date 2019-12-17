
def get_local_ip():
    """**UNUSED**
    
    Gets local IP

    Source: https://stackoverflow.com/a/166589
    
    Returns:
        str: Local IP
    """
    # Clever! https://stackoverflow.com/a/166589
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    print(s.getsockname()[0])
    s.close()
    return s.getsockname()[0]