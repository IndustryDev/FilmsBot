from logger import logger


def async_log_message(func):
    """
    Decorator for logging user messages and function calls
    :param func:
    :return:
    """

    async def wrapper(*args, **kwargs):
        args_str = ', '.join([str(i) for i in args])
        kwargs_str = ', '.join([f'{k} = {v}' for k, v in kwargs.items()])
        logger.debug(f'Function call {func.__name__} with arguments {args_str} {kwargs_str}')
        return await func(*args, **kwargs)

    return wrapper
