import psycopg2

from src.api_hh import get_salary


def create_database(database_name: str, params: dict) -> None:
    """
    Создает базу данных и таблицы для сохранения данных об организациях и предоставляемых ими вакансиях.

    Args:
        database_name (str): Имя создаваемой базы данных.
        params (dict): Параметры подключения к серверу PostgresSQL.

    Returns:
        None
    """
    # Подключаемся к серверу PostgresSQL
    conn = psycopg2.connect(dbname="postgres", **params)
    conn.autocommit = True
    cur = conn.cursor()

    # Удаляем существующую базу данных, если она уже существует
    cur.execute(f"DROP DATABASE IF EXISTS {database_name}")
    # Создаем новую базу данных
    cur.execute(f"CREATE DATABASE {database_name}")

    cur.close()
    conn.close()

    # Подключаемся к вновь созданной базе данных
    conn = psycopg2.connect(dbname=database_name, **params)
    with conn.cursor() as cur:
        # Создаем таблицу организаций
        cur.execute(
            """
        CREATE TABLE organizations (
            organization_id INT PRIMARY KEY,
            organization_name VARCHAR(255),
            organization_url TEXT,
            employer_reliability_indicator BOOLEAN
        )
        """
        )

    with conn.cursor() as cur:
        # Создаем таблицу вакансий
        cur.execute(
            """
        CREATE TABLE vacancies (
            vacancy_id INTEGER PRIMARY KEY,
            organization_id INTEGER REFERENCES organizations(organization_id),
            city_vacancies VARCHAR(100),
            vacancy_name VARCHAR(255),
            requirement TEXT,
            responsibility TEXT,
            salary INTEGER NULL,
            experience VARCHAR(255),
            type_of_employment VARCHAR(255),
            work_schedule VARCHAR(100),
            working_hours VARCHAR(100),
            published_at TIMESTAMP,
            vacancy_url TEXT
        )
        """
        )

    conn.commit()
    conn.close()


def save_to_database(data: dict, database_name: str, params: dict) -> None:
    """
    Сохраняет данные о работодателях и предоставляемых ими вакансиях в базу данных.

    Args:
        data (dict): Словарь с данными о вакансиях и работодателях.
        database_name (str): Имя базы данных.
        params (dict): Параметры подключения к базе данных.

    Returns:
        None
    """
    # Подключаемся к базе данных
    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        # Обрабатываем каждую вакансию из полученных данных
        for vacancy_id, vacancy in data.items():
            employer_id = vacancy["employer"]["id"]

            # Сохраняем данные о работодателе, игнорируя дубликаты
            cur.execute(
                """
                INSERT INTO organizations (
                    organization_id,
                    organization_name,
                    organization_url,
                    employer_reliability_indicator
                ) VALUES (%s, %s, %s, %s)
                ON CONFLICT (organization_id) DO NOTHING
                """,
                (
                    employer_id,
                    vacancy["employer"]["name"],
                    vacancy["employer"]["alternate_url"],
                    vacancy["employer"]["trusted"],
                ),
            )

            # Предварительная обработка поля salary
            salary_value = get_salary(vacancy.get("salary"))

            # Сохраняем данные о вакансии
            cur.execute(
                """
                INSERT INTO vacancies (
                    vacancy_id,
                    organization_id,
                    city_vacancies,
                    vacancy_name,
                    requirement,
                    responsibility,
                    salary,
                    experience,
                    type_of_employment,
                    work_schedule,
                    working_hours,
                    published_at,
                    vacancy_url
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    vacancy_id,
                    employer_id,
                    vacancy["area"]["name"],
                    vacancy["name"],
                    vacancy["snippet"]["requirement"],
                    vacancy["snippet"]["responsibility"],
                    salary_value,
                    vacancy["experience"]["name"],
                    vacancy["schedule"]["name"],
                    ",".join(vacancy["work_schedule_by_days"]),
                    ",".join(vacancy["working_hours"]),
                    vacancy["published_at"],
                    vacancy["alternate_url"],
                ),
            )

    conn.commit()
    conn.close()
