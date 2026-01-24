from typing import Dict, List, Optional, Union

import requests


def get_salary(salary_input: Optional[Union[Dict, int, float]]) -> Optional[Union[str, int, float]]:
    """
    Извлекает числовое значение или диапазон зарплаты из словаря salary.

    Args:
        salary_input (dict/int/float/None): Данные о зарплате в произвольном формате.

    Returns:
        str или None: Строка с зарплатой ('от X до Y'), число или None, если данные отсутствуют.
    """

    if salary_input is None:
        return None

    # Если передан словарь, работаем с ним
    if isinstance(salary_input, dict):
        from_val = salary_input.get("from")
        to_val = salary_input.get("to")

        # Если оба значения существуют, возвращаем to_val
        if from_val is not None and to_val is not None:
            return to_val

        # Иначе выбираем первое существующее значение
        if from_val is not None:
            return from_val
        elif to_val is not None:
            return to_val

    # Для чисел и прочих типов возвращаем само значение
    return salary_input


def get_vacancies_from_employers(employer_ids: List[int]) -> Dict[str, Dict]:
    """
    Получает и фильтрует данные о вакансиях с сайта HeadHunter по списку идентификаторов работодателей.

    Эта функция отправляет HTTP-запросы к API HeadHunter для сбора информации о вакансиях,
    относящихся к указанным работодателям. По каждому работодателю обрабатываются до 10 страниц
    результатов (по 100 вакансий на страницу), ограничиваясь регионом Москва (идентификатор региона 1).

    Args:
        employer_ids (List[int]): Список идентификаторов работодателей, чьи вакансии необходимо получить.

    Returns:
        Dict[str, Dict]: Словарь, содержащий отфильтрованные данные о найденных вакансиях. Ключи словаря —
        уникальные идентификаторы вакансий, значения представляют собой словари с отобранными полями.

    Note:
        - Область поиска ограничена Москвой (region ID = 1).
        - Максимальное количество вакансий на одну страницу составляет 100.
        - При возникновении проблем с выполнением HTTP-запросов (ошибки сети, сервера и др.)
          функция продолжает работу, пропуская проблемные страницы и выдавая предупреждение.
    """

    # Создаем пустой словарь для накопления данных о вакансиях
    data_vacancies = {}

    # Устанавливаем параметры поиска: регион (Москва) и количество вакансий на страницу
    area = 1  # Код Москвы в API HeadHunter
    per_page = 100  # Максимально возможное количество вакансий на страницу

    # Проходим по каждому идентификатору работодателя из переданного списка
    for employer_id in employer_ids:

        # Перебираем страницы результатов (HeadHunter поддерживает максимум 10 страниц)
        for page in range(10):

            # Формируем URL для запроса к API HeadHunter с необходимыми параметрами
            url = (
                f"https://api.hh.ru/vacancies?"
                f"employer_id={employer_id}&"
                f"area={area}&"
                f"per_page={per_page}&"
                f"page={page}"
            )

            try:
                # Отправляем HTTP-запрос к API HeadHunter
                response = requests.get(url)

                # Проверяем успешность запроса по статус-коду ответа
                if response.status_code != 200:
                    print(f"HTTP ошибка: {response.status_code}. Пропуск страницы.")
                    continue  # Переходим к следующему номеру страницы

                # Преобразуем ответ сервера в JSON-структуру
                data = response.json()

                # Извлекаем список вакансий из полученного ответа
                vacancies = data.get("items", [])

                # Проходим по каждой вакансии в полученной выборке
                for vacancy in vacancies:
                    # Извлекаем необходимые поля из описания вакансии
                    vacancy_id = vacancy.get("id")
                    vacancy_name = vacancy.get("name")
                    vacancy_area = vacancy.get("area", {}).get("name")
                    vacancy_salary = get_salary(vacancy.get("salary"))  # <-- Здесь применяем нашу функцию!
                    vacancy_type = vacancy.get("type", {}).get("name")
                    vacancy_published_at = vacancy.get("published_at")
                    vacancy_alternate_url = vacancy.get("alternate_url")
                    vacancy_requirements = vacancy.get("snippet", {}).get("requirement")
                    vacancy_responsibilities = vacancy.get("snippet", {}).get("responsibility")
                    vacancy_schedule = vacancy.get("schedule", {}).get("name")
                    # Исправляем неразрывный пробел в working_hours
                    working_hours = [
                        hour.get("name").replace("\xa0", " ") for hour in vacancy.get("working_hours", [])
                    ]
                    work_schedule_by_days = [day.get("name") for day in vacancy.get("work_schedule_by_days", [])]
                    vacancy_experience = vacancy.get("experience", {}).get("name")
                    vacancy_employment = vacancy.get("employment", {}).get("name")
                    employer_data = vacancy.get("employer", {})

                    # Сохраняем данные о вакансии в результирующем словаре
                    data_vacancies[vacancy_id] = {
                        "id": vacancy_id,
                        "name": vacancy_name,
                        "area": {"name": vacancy_area},
                        "salary": vacancy_salary,
                        "type": {"name": vacancy_type},
                        "published_at": vacancy_published_at,
                        "alternate_url": vacancy_alternate_url,
                        "employer": {
                            "id": employer_data.get("id"),
                            "name": employer_data.get("name"),
                            "alternate_url": employer_data.get("alternate_url"),
                            "trusted": employer_data.get("trusted"),
                        },
                        "snippet": {"requirement": vacancy_requirements, "responsibility": vacancy_responsibilities},
                        "schedule": {"name": vacancy_schedule},
                        "working_hours": working_hours,
                        "work_schedule_by_days": work_schedule_by_days,
                        "experience": {"name": vacancy_experience},
                        "employment": {"name": vacancy_employment},
                    }

            # Обрабатываем возможные ошибки при выполнении HTTP-запросов
            except requests.RequestException:
                print("Ошибка при выполнении HTTP-запроса")

    # Возвращаем накопленные данные о вакансиях
    return data_vacancies
