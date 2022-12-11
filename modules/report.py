from __future__ import annotations
import os
import re
import logging
import itertools
from pathlib import Path

from .report_item import ReportItem
from .line_attrs import LineAttrs


class Report:
    _items: dict[str, ReportItem]
    _src_filename: str  # имя исходного файла-лога
    _reports_dir: str  # директория с отчетами
    # Количество строк, которые не соответствуют шаблону
    _invalid_patterns_count: int

    def __init__(
        self,
        filename: str,
        logger: logging.Logger,
        config: dict,
    ) -> None:
        self._items = {}
        self._src_filename = filename
        self._logger = logger
        self._config = config
        self._invalid_patterns_count = 0
        self._reports_dir = config["REPORT_DIR"]

    @property
    def total_items(self) -> int:
        return len(self._items)

    def append(self, line_attrs: LineAttrs) -> None:
        """
        Добавление единицы отчета
            - подготовка данных в виде объекта
            - если запрос отсутствует в отчете
                - происходит его добавление
            - если запрос уже присутствует в отчете
                - происходит его дополнение информацией
        """
        if line_attrs.is_empty:
            self._invalid_patterns_count += 1
            return

        request: str = line_attrs.request
        if request in self._items:
            self._items[request] = self._items[request].append(
                line_attrs=line_attrs,
            )
        else:
            self._items[request] = ReportItem.from_line_attrs(
                line_attrs=line_attrs,
            )

    def __str__(self) -> str:
        return str(self._items)

    def calculate(self) -> Report:
        """ Формирование отсортированного, посчитанного объема """
        total_count: int = 0
        total_time: float = 0.
        for item in self._items.values():
            item.calculate()
            total_count += item.count
            total_time += item.time_sum
        self._logger.debug("Sort items by time_sum...")
        self._items = dict(
            sorted(
                self._items.items(),
                key=lambda item: item[1],
                reverse=True,
                )
        )
        self._logger.debug("Calculate slice of items by time_sum...")
        for item in self._items.values():
            item.count_perc = (item.count / total_count) * 100
            item.time_perc = (item.time_sum / total_time) * 100
        self._logger.debug(f"{total_count=}, {total_time=}")
        return self

    def having(self, count_gt: int = None) -> dict[str, ReportItem]:
        """ Срез данных, количество вызовов которых превышает count_gt """
        items: dict[str, ReportItem] = {}
        if count_gt:
            items = {
                key: item
                for key, item in self._items.items()
                if item.count > count_gt
            }
        return items

    def _get_report_name(self) -> str:
        """ Формирование имени файла-отчета """
        report_date: str = self._get_date_from_src_filename()
        report_filename: str = f"{self._reports_dir}/report-{report_date}.html"
        return report_filename

    def _get_report_items(self, count: int) -> str:
        """
        Формирование списка элементов для отчета
        Формат: {"url": "http://...","attr1":val1,"attr2":val2...}
        """
        result: list[str] = []
        for item in itertools.islice(self._items, count):
            result.append(f'{{"url":"{item}",{self._items[item]}}}')
        return f"[{','.join(result)}]"

    def save(self, size: int) -> None:
        """ Сохранение подготовленных данныхв файл-шаблон """
        # Сбор данных из шаблона отчета
        filename_template: str = self._config["REPORT_TEMPLATE_FILENAME"]
        template_data: str = Path(filename_template).read_text()
        # Подготовка данных
        dst_data: str = template_data.replace(
            self._config["REPORT_PLACEHOLDER"],
            self._get_report_items(count=size),
        )
        # Сохранение данных
        report_path: str = f"{self._get_report_name()}"
        Path(report_path).open("w").write(dst_data)

    def _get_date_from_src_filename(self) -> str:
        """
        Выбор даты в соответствующем формате, с учетом того,
            что она расположена вконце имени файла без разделителей
        """
        # Убарть расширение
        filename: str = self._src_filename
        # Исключить двойное расширение tar-архива
        if self._src_filename.endswith("tar.gz"):
            filename = "".join(filename.rsplit("tar.", 1))
        # Выбрать "сырую" дату из имени файла
        fname_without_extension: str = os.path.splitext(filename)[0]
        src_date: str = fname_without_extension[-8:]
        if not re.match(r"\d{8}", src_date):
            raise Exception("Ошибка парсинга даты из имени файла")
        # Формировать дату
        dst_date: str = f"{src_date[:4]}.{src_date[4:6]}.{src_date[6:]}"
        return dst_date

    def is_report_exists(self) -> bool:
        """ Проверка на присутствие ранее обработанного файла-отчета """
        return os.path.exists(self._get_report_name())
