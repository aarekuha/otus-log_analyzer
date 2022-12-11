import os
import re
import json
import argparse
import logging


def is_valid_filename(filename: str, filename_template: str) -> bool:
    """Проверка имени файла на соответствие требованиям именования"""
    is_match_pattern: bool = bool(re.match(filename_template, filename))
    return is_match_pattern


def get_last_file_name(folder: str, filename_template: str) -> str:
    """Поиск имени файла с самой поздней датой"""
    newest_filename: str = ""
    for filename in [
        f
        for f in os.listdir(folder)
        if os.path.isfile(f"{folder}/{f}")
        and is_valid_filename(
            filename=f,
            filename_template=filename_template,
        )
    ]:
        newest_filename = max(filename, newest_filename)

    return newest_filename


def get_src_log_filename(
    path: str,
    filename_template: str,
    logger: logging.Logger,
) -> str | None:
    """Путь к исходному файлу логов"""
    if not os.path.exists(path):
        message: str = f"Указан неправильный каталог к исходным логам: {path}"
        logger.exception(message, exc_info=False)
        raise Exception(message)
    filename: str = get_last_file_name(
        folder=path,
        filename_template=filename_template,
    )
    if not filename:
        return None

    return filename


def get_config(default_config: dict) -> dict:
    """
    Получить данные из файла конфигурации и слить их со
        словарём "по умолчанию"
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="config.json",
        help="json config filename",
    )
    args: argparse.Namespace = parser.parse_args()
    _config: dict = default_config.copy()

    try:
        if not os.path.exists(args.config):
            # Обработка ошибки производится во внешнем блоке
            raise Exception()
        with open(args.config, "rt") as config_file:
            _config.update(json.load(config_file))
    except Exception:
        logging.exception(f"Ошибка чтения файла конфигурации: {args.config}")

    return _config


def get_logger(_config: dict) -> logging.Logger:
    filename: str | None = None
    if _config.get("LOG_FILENAME", None):
        filename = _config["LOG_FILENAME"]

    log_format: str = "[%(asctime)s] %(levelname).1s %(message)s"
    date_format: str = "%Y.%m.%d %H:%M:%S"
    logging.basicConfig(
        filename=filename,
        level=logging.DEBUG,
        format=log_format,
        datefmt=date_format,
    )
    return logging.getLogger("__main__")
