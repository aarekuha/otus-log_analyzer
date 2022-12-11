#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gzip
import logging
from typing import Union

from modules import LineAttrs
from modules import Report
from modules import get_config
from modules import get_src_log_filename
from modules import get_logger

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "INVALID_PATTERN_LIMIT_PERC": 0.3,
    "LOG_FILENAME": None,
    "BATCH_LINES_COUNT": 10_000,
    "REPORT_PLACEHOLDER": "$table_json",
    "REPORT_TEMPLATE_FILENAME": "template/report.html",
    "FILENAME_TEMPLATE": r"nginx-access-ui.log-\d{8}.(gz|txt)",
}


def main(_config: dict, logger: logging.Logger) -> None:
    path: str = _config["LOG_DIR"]
    filename: Union[str, None] = get_src_log_filename(
        path=path,
        filename_template=_config["FILENAME_TEMPLATE"],
        logger=logger,
    )
    if not filename:
        return
    report: Report = Report(
        filename=filename,
        logger=logger,
        config=_config,
    )
    if report.is_report_exists():
        return
    parsed_lines_count: int = 0  # счетчик количества обработанных строк
    # Файл может быть архивом gz или plain (txt)
    context_manager = gzip.open if filename.endswith("gz") else open
    invalid_pattern_counter: int = 0
    with context_manager(f"{path}/{filename}", "rt") as file:
        count = 0
        for line in file:
            if line.strip():
                line_attrs: LineAttrs = LineAttrs(text_line=line)
                if line_attrs.is_empty:
                    invalid_pattern_counter += 1
                else:
                    report.append(line_attrs=line_attrs)
                    parsed_lines_count += 1
                    if not parsed_lines_count % _config["BATCH_LINES_COUNT"]:
                        print(f"{parsed_lines_count}...", end="\r")
            count += 1
            if count > 100_000:
                break
    inv_pattern_limit_perc: float = _config["INVALID_PATTERN_LIMIT_PERC"]
    invalid_percent: float = invalid_pattern_counter / report.total_items
    if invalid_percent > inv_pattern_limit_perc:
        logger.info(
            "Превышено допустимое отношение количества строк в "
            f"неправильном формате: {invalid_pattern_counter}/"
            f"{report.total_items} неправильных строк "
            f"({round(invalid_percent * 100, 2)}%)"
        )
        return
    report.calculate().save(size=_config["REPORT_SIZE"])


if __name__ == "__main__":
    logger: logging.Logger = logging.getLogger("")
    try:
        _config: dict = get_config(default_config=config)
        logger = get_logger(_config=_config)
        main(_config=_config, logger=logger)
    except Exception as exception:
        logger.exception(exception)
