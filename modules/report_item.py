from __future__ import annotations
import statistics
from typing import Any
from dataclasses import dataclass

from .line_attrs import LineAttrs


@dataclass
class ReportItem:
    # сколько раз встречается URL, абсолютное значение
    count: int
    # сĸольĸо раз встречается URL, в процентнах относительно общего
    #   числа запросов
    count_perc: float
    # суммарный $request_time для данного URL'а, абсолютное значение
    time_sum: float
    # суммарный $request_time для данного URL'а, в процентах относительно
    #   общего $request_time всех запросов
    time_perc: float
    # средний $request_time для данного URL'а
    time_avg: float
    # маĸсимальный $request_time для данного URL'а
    time_max: float
    # медиана $request_time для данного URL'а
    time_med: float
    times: list[float]
    request: str = ""

    @classmethod
    def from_line_attrs(cls, line_attrs: LineAttrs) -> ReportItem:
        request_time: float = cls._try_float(line_attrs.request_time)

        return ReportItem(
            count=1,
            count_perc=0.,
            time_sum=request_time,
            time_perc=0.,
            time_avg=0,
            time_max=request_time,
            time_med=0,
            times=[request_time],
        )

    @classmethod
    def _try_float(cls, src_value: Any) -> float:
        float_value: float
        try:
            float_value = float(src_value)
        except ValueError:
            float_value = 0.
        return float_value

    def append(self, line_attrs: LineAttrs) -> ReportItem:
        request_time: float = self._try_float(
            src_value=line_attrs.request_time,
        )
        self.count += 1
        self.time_sum += request_time
        self.times.append(request_time)
        return self

    def calculate(self) -> ReportItem:
        """ Подготовка значений по всем собранным сведениям запроса """
        self.time_avg = sum(self.times) / self.count
        self.time_max = max(self.times)
        self.time_med = statistics.median(self.times)
        return self

    def __gt__(self, other: ReportItem) -> bool:
        return self.time_sum > other.time_sum

    def __str__(self) -> str:
        """ Преобразование в строку, которая будет подставлена в отчет """
        return ",".join([
            f'"{key}":{self.__getattribute__(key)}'
            for key in self.__annotations__.keys()
            if key not in ["times", "request"]
        ])
