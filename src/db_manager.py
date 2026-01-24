from typing import Dict, List, Optional, Union

import psycopg2


class DBManager:
    """
    Менеджер базы данных для работы с PostgresSQL.

    Attributes:
        params (dict): Параметры подключения к базе данных.
        conn (Optional[psycopg2.extensions.connection]): Экземпляр соединения с базой данных.
    """

    def __init__(self, connection_params: dict) -> None:
        """
        Инициализация класса DBManager и установка соединения с БД.
        """
        self.params = connection_params
        self.conn = None
        self.connect()

    def connect(self) -> None:
        """
        Устанавливает соединение с базой данных.
        """
        try:
            self.conn = psycopg2.connect(**self.params)
            print("✅ Соединение с базой данных успешно установлено.")
        except psycopg2.Error as error:
            print(f"❗ Произошла ошибка при подключении к базе данных: {error}")

    def close_connection(self) -> None:
        """
        Закрытие соединения с БД.
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            print("⚠️ Соединение с базой данных закрыто.")

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Union[str, int]]]:
        """
        Получает список всех компаний и количество вакансий у каждой компании.

        Returns:
            List[Dict]: Список словарей с информацией о компаниях и количестве вакансий.
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        o.organization_name AS "Компания",
                        COUNT(v.vacancy_id) AS "Количество вакансий"
                    FROM
                        organizations o
                    LEFT JOIN
                        vacancies v ON o.organization_id = v.organization_id
                    GROUP BY
                        o.organization_name
                    ORDER BY
                        COUNT(v.vacancy_id) DESC
                    """
                )
                rows = cursor.fetchall()
                return [{"company": row[0], "vacancy_count": row[1]} for row in rows]
        except psycopg2.Error as error:
            print(f"❗ Ошибка при выполнении запроса: {error}")
            return []

    def get_all_vacancies(self) -> List[Dict[str, Union[str, int, Optional[int]]]]:
        """
        Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию.

        Returns:
            List[Dict]: Список словарей с информацией о вакансиях.
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        o.organization_name AS "Название компании",
                        v.vacancy_name AS "Название вакансии",
                        v.salary AS "Зарплата",
                        v.vacancy_url AS "Ссылка на вакансию"
                    FROM
                        vacancies v
                    JOIN
                        organizations o ON v.organization_id = o.organization_id
                    """
                )
                rows = cursor.fetchall()
                return [{"company": row[0], "position": row[1], "salary": row[2], "url": row[3]} for row in rows]
        except psycopg2.Error as error:
            print(f"❗ Ошибка при выполнении запроса: {error}")
            return []

    def get_avg_salary(self) -> Optional[float]:
        """
        Получает среднюю зарплату по вакансиям.

        Returns:
            Optional[float]: Среднее значение зарплаты или None при отсутствии данных.
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT AVG(salary) AS average_salary
                    FROM vacancies
                    WHERE salary IS NOT NULL;
                    """
                )
                result = cursor.fetchone()
                return result[0] if result else None
        except psycopg2.Error as error:
            print(f"❗ Ошибка при выполнении запроса: {error}")
            return None

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Union[str, int]]]:
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.

        Returns:
            List[Dict]: Список словарей с информацией о вакансиях.
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    WITH AverageSalary AS (
                        SELECT AVG(salary) AS avg_salary
                        FROM vacancies
                        WHERE salary IS NOT NULL
                    )
                   SELECT
                       v.vacancy_id,
                       o.organization_name,
                       v.vacancy_name,
                       v.salary
                   FROM
                       vacancies v
                   INNER JOIN
                       organizations o ON v.organization_id = o.organization_id
                   WHERE
                       v.salary > (SELECT avg_salary FROM AverageSalary)
                    """
                )
                rows = cursor.fetchall()
                return [{"vacancy_id": row[0]} for row in rows]
        except psycopg2.Error as error:
            print(f"❗ Ошибка при выполнении запроса: {error}")
            return []

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Union[str, int, Optional[int]]]]:
        """
        Получает список всех вакансий, в названии которых содержатся переданные в метод слова.

        Args:
            keyword (str): Ключевое слово для поиска.

        Returns:
            List[Dict]: Список словарей с информацией о найденных вакансиях.
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT *
                    FROM vacancies
                    WHERE LOWER(vacancy_name) LIKE LOWER(%s)
                    """,
                    (f"%{keyword}%",),
                )
                rows = cursor.fetchall()
                return [{"position": row[1]} for row in rows]
        except psycopg2.Error as error:
            print(f"❗ Ошибка при выполнении запроса: {error}")
            return []
