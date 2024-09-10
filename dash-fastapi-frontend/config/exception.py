from dash import set_props, ctx, no_update
from utils.feedback_util import MessageManager, NotificationManager
from utils.log_util import logger


class AuthException(Exception):
    """
    自定义令牌异常AuthException
    """

    def __init__(self, data: str = None, message: str = None):
        self.data = data
        self.message = message


class RequestException(Exception):
    """
    自定义请求异常RequestException
    """

    def __init__(self, data: str = None, message: str = None):
        self.data = data
        self.message = message


class ServiceException(Exception):
    """
    自定义服务异常ServiceException
    """

    def __init__(self, data: str = None, message: str = None):
        self.data = data
        self.message = message


class ServiceWarning(Exception):
    """
    自定义服务警告ServiceWarning
    """

    def __init__(self, data: str = None, message: str = None):
        self.data = data
        self.message = message


def global_exception_handler(error):
    if isinstance(error, AuthException):
        set_props('token-invalid-modal', {'visible': True})
    elif isinstance(error, RequestException):
        NotificationManager.error(description=error.message, message='请求异常')
    elif isinstance(error, ServiceWarning):
        MessageManager.warning(content=error.message)
    elif isinstance(error, ServiceException):
        MessageManager.error(content=error.message)
    else:
        logger.exception(f'[exception]{error}')
        NotificationManager.error(description=str(error), message='服务异常')
    # dash2.18版本对输出为字典形式的回调进行异常处理会报错，临时采用此方法解决
    outputs_grouping = ctx.outputs_grouping
    if isinstance(outputs_grouping, dict):
        return {
            key: [no_update] * len(value)
            if isinstance(value, list) and len(value) > 0
            else no_update
            for key, value in outputs_grouping.items()
        }
