# rvision-dozor-connector
Коннектор для сбора отмеченных инцидентов из DLP Solar Dozor и заведения их в R-Vision SOAR 

Настройка:

В файле `settings_template.ini1` укажите актуальные данные для подключения к R-Vision SOAR, DLP Solar Dozor, а также пути для логирования и сохранения данных инцидентов.

Использование:
  
```shell 
python3 nad_connector.py <Отправитель> <Получатель> <Имя сработавшего правила> <Идентификатор инцидента в R-Vision SOAR> 
```

В будущем будет доработана интеграция с другими популярными SOAR
