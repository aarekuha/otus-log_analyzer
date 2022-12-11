import re
from typing import Union
from functools import lru_cache


class LineAttrs:
    """
    Строка лога преобразованная в объект по шаблону Config.template
    """

    remote_addr: str = r"[\d\.]+"
    remote_user: str = r".+"
    http_x_real_ip: str = r".+"
    time_local: str = r".+"
    type: str = r"(GET|POST|PATCH)"
    request: str = r".+"
    proto: str = r"HTTP/\d\.\d"
    status: str = r".+"
    body_bytes_sent: str = r".+"
    http_referer: str = r".+"
    http_user_agent: str = r".+"
    http_x_forwarded_for: str = r".+"
    http_X_REQUEST_ID: str = r".+"
    http_X_RB_USER: str = r".+"
    request_time: str = r".+"
    _is_empty: bool = False

    class Config:
        # Шаблон для парсинга логов
        template: str = (
            "^$remote_addr $remote_user $http_x_real_ip \\[$time_local\\] "
            '"$type $request $proto" $status $body_bytes_sent '
            '"$http_referer" "$http_user_agent" '
            '"$http_x_forwarded_for" "$http_X_REQUEST_ID" '
            '"$http_X_RB_USER" $request_time$'
        )

    @lru_cache
    def _get_template(self) -> str:
        """Формирование шаблона строки из атрибутов"""
        template: str = self.Config.template
        for attr in self.__annotations__:
            template = template.replace(
                f"${attr}",
                f"(?P<{attr}>{self.__class__.__dict__[attr]})",
                1,
            )
        return template

    def __init__(self, text_line: str) -> None:
        matches: Union[re.Match, None] = re.search(
            self._get_template(),
            text_line,
        )
        if matches:
            for attr in self.__annotations__:
                if not attr.startswith("_"):
                    self.__dict__[attr] = matches.group(attr)
        else:
            self._is_empty = True

    @property
    def is_empty(self) -> bool:
        """
        Признак несоответствия строки шаблону
        Парсинг строки не удался
        """
        return self._is_empty
