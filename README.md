#### Log Analyzer
Скрипт для анализа и формирования сводного отчета о содержимом логов в заданном формате.
##### Шаблон строк кода
- сам шаблон содержится в модуле [modules/line_attrs.py](modules/line_attrs.py#L30)
- изменения шаблона должно сопровождаться добавлением/изменением полей класса LineAttrs по следующим правилам:
    - в шаблоне переменная должна содержать знак "доллар" перед именем
    - атрибут класса не должен начинаться с нижнего подчёркивания или знака $
    - атрибут во время определения является строковой переменной, которая содержит шаблон регулярного выражения для
      парсинга (во время инициализации, указанный шаблон обогащает общий Config.template данными, указанными при
      инициализации)
##### Пример файла конфигурации [config.json](config.json)
```json
{
    "LOG_DIR": "./src_logs",
    "LOG_FILENAME": "./logs/my_log.log",
    "REPORT_SIZE": 10
    "REPORT_DIR": "./reports",
    "INVALID_PATTERN_LIMIT_PERC": 0.3,
    "BATCH_LINES_COUNT": 10000,
    "REPORT_PLACEHOLDER": "$table_json",
    "REPORT_TEMPLATE_FILENAME": "template/report.html",
    "FILENAME_TEMPLATE": "nginx-access-ui.log-\d{8}.(gz|txt)",
}
```
|Имя настройки|Описание|
|----------|-------------|
|LOG_DIR|Путь к файлу необработанных логов|
|LOG_FILENAME|Имя файла, который будет содержать логи выполнения скрипта|
|REPORT_SIZE|Количество строк, которые будет содержать файл отчета|
|REPORT_DIR|Путь к директории, в которую будет записываться отчет|
|INVALID_PATTERN_LIMIT_PERC|Отношение строк исходного лога, которые не удалось разобрать - 0..1 (в процентах)|
|BATCH_LINES_COUNT|Количество строк, которые будут обработаны до вывода текущего состояния в консоль (прогресс)|
|REPORT_PLACEHOLDER|Имя переменной в файле-шаблоне отчёта, которая будет заменена на подготовленные данные|
|REPORT_TEMPLATE_FILENAME|Путь к файлу-шаблону, на основе которого генерируется отчет|
|FILENAME_TEMPLATE|Регулярное выражение - шаблон имени файла исходных логов|
##### Запуск скрипта
- Скрипт не требует дополнительных зависимостей
- Запуск может осуществляться вызовом следующей команды
```bash
    python log_analyzer.py
```
##### Допустимые параметры, которые может принимать скрипт
```
    --config путь_к_файлу
    например, python log_analyzer.py --config my_config.json
```
- файл конфигурации должен быть в формате json
- настройки указанные в альтернативном файле конфигурации являются приоритетными, т.е. заменяют настройки "по умолчанию"
- файлом конфигурации "по умолчанию" является файл ./config.json
