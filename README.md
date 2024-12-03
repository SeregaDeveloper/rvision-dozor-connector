# rvision-dozor-connector
Коннектор для сбора отмеченных инцидентов из DLP Solar Dozor и заведения их в R-Vision SOAR 

Принцип работы: 

Скрипт авторизуется в Dozor, собирает последние 50 отмеченных инцидентов (по желанию значение и принцип отбора можно изменить, строка скрипта: 65). Если ID инцидента уже есть в списке заведенных, то инцидент пропускается (так как он ранее отработан), а если нет - то обрабатывается и заводится в R-Vision, а его ID попадает в список `last_dozor_id.txt`. 

Настройка:

В файле, оформленном по образу `settings_template.ini`, укажите актуальные данные для подключения к R-Vision SOAR, DLP Solar Dozor, а также пути для логирования и сохранения данных о инцидентах.

В скрипте `python3 dozor-to-rvision.py` вместо `path/to/config/file` укажите путь к актуальному файлу конфигурации.

Использование:

```shell 
python3 dozor-to-rvision.py
```

В будущем будет доработана интеграция с другими популярными SOAR
