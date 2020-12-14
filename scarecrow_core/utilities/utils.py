import os 
import logging
import logging.config

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


def get_logger(conf_path='../../conf/logger.ini'):
    """Gets the standard logger
    
    Args:
        conf_path (str, optional): Config path. Defaults to '../conf/logger.ini'.
    
    Returns:
        logger: Logger
    """
    try:
        file_dir = os.path.split(os.path.realpath(__file__))[0]
        log_conf = os.path.join(file_dir, conf_path)
        logging.config.fileConfig(log_conf, disable_existing_loggers=False)
        logger = logging.getLogger('scarecrow')
        return logger
    except Exception:
        print(f'Cannot find logging config at {conf_path}')
        formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s %(filename)s:%(funcName)s():%(lineno)d - %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger = logging.getLogger('scarecrow')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        return logger