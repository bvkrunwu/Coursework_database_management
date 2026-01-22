from configparser import ConfigParser
from typing import Any, Dict


def config(filename: str = "database.ini", section: str = "postgresql") -> Dict[str, Any]:
    """
    Читает конфигурационные параметры из INI-файла и возвращает их в виде словаря.

    Args:
        filename (str): Имя файла конфигурации (по умолчанию "database.ini").
        section (str): Раздел конфигурации, который нужно прочитать (по умолчанию "postgresql").

    Returns:
        Dict[str, Any]: Словарь с парами ключ-значение из указанного раздела конфигурации.

    Raises:
        Exception: Если указанный раздел не найден в файле конфигурации.
    """
    # Создание экземпляра парсера конфигурации
    parser = ConfigParser()

    # Чтение файла конфигурации
    parser.read(filename)

    # Инициализация пустого словаря для хранения параметров
    db = {}

    # Проверка наличия указанного раздела в файле конфигурации
    if parser.has_section(section):
        # Получение всех параметров из указанного раздела
        params = parser.items(section)

        # Заполнение словаря параметрами
        for param in params:
            db[param[0]] = param[1]
    else:
        # Генерация исключения, если раздел не найден
        raise Exception(f"Секция '{section}' не найдена в файле '{filename}'.")

    # Возвращение словаря с параметрами
    return db
