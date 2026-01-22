import os

from dotenv import load_dotenv

from src.api_hh import get_vacancies_from_employers
from src.config import config
from src.database import create_database, save_to_database
from src.db_manager import DBManager


def main() -> None:
    """
    Основная функция приложения.

    Эта функция выполняет следующие шаги:
    1. Определяет список идентификаторов работодателей.
    2. Загружает параметры конфигурации из файла database.ini.
    3. Получает данные о вакансиях через API HeadHunter.
    4. Создаёт базу данных job_vacancy.
    5. Сохраняет полученные данные в созданную базу данных.
    6. Запускает интерактивный интерфейс для работы с данными.
    """

    load_dotenv()  # Загрузка переменных среды из .env файла
    password = os.getenv("DB_PASSWORD")

    # Список уникальных идентификаторов работодателей на сайте HeadHunter
    employer_ids = [1068, 2665531, 12346192, 4233, 907345, 1057, 1473866, 3959394, 1373, 4496]

    # Получаем параметры конфигурации из файла database.ini
    params = config()

    # Запрашиваем список вакансий указанных работодателей через API HeadHunter
    data = get_vacancies_from_employers(employer_ids)

    # Создаем новую базу данных с заданными параметрами
    create_database("job_vacancy", params)

    # Сохраняем полученные данные о вакансиях в созданную базу данных
    save_to_database(data, "job_vacancy", params)

    # Создаем экземпляр менеджера базы данных
    manager = DBManager(
        connection_params={
            "dbname": "job_vacancy",
            "user": "postgres",
            "password": password,
            "host": "localhost",
            "port": "5432",
        }
    )

    # Запускаем интерактивный интерфейс для работы с данными
    interact_with_user(manager)


def interact_with_user(manager: DBManager) -> None:
    """
    Функция взаимодействия с пользователем через командную строку.
    Предоставляет меню с возможностями и выводит результаты.
    """
    while True:
        print("\nДобро пожаловать в систему управления вакансиями!")
        print("Выберите действие:")
        print("1. Получить список компаний и количество вакансий у каждой")
        print("2. Просмотреть все вакансии с указанием компании, названия, зарплаты и ссылки на вакансию")
        print("3. Узнать среднюю зарплату по всем вакансиям")
        print("4. Показать вакансии с зарплатой выше средней")
        print("5. Найти вакансии по ключевому слову (например, 'Аналитик')")
        print("0. Завершить работу")

        choice = input("Введите номер выбранного пункта: ")

        if choice == "1":
            companies = manager.get_companies_and_vacancies_count()
            print("\nКомпании и количество вакансий:")
            for company_data in companies:
                print(f"- Компания '{company_data['company']}' имеет {company_data['vacancy_count']} вакансий.")

        elif choice == "2":
            vacancies = manager.get_all_vacancies()
            print("\nВсе вакансии:")
            for vacancy in vacancies:
                print(
                    f"Компания: {vacancy['company']}\nВакансия: {vacancy['position']}\nЗарплата: {vacancy['salary']}"
                    f"\nСсылка на вакансию: {vacancy['url']}\n"
                )

        elif choice == "3":
            avg_salary = manager.get_avg_salary()
            print(f"\nСредняя зарплата по всем вакансиям: {avg_salary:.0f} ₽.")

        elif choice == "4":
            high_salary_vacancies = manager.get_vacancies_with_higher_salary()
            print("\nВакансии с зарплатой выше средней:")
            for vacancy in high_salary_vacancies:
                print(f"Вакансия: {vacancy['vacancy_id']}")

        elif choice == "5":
            keyword = input("Введите ключевое слово для поиска: ").lower().strip()
            keyword_vacancies = manager.get_vacancies_with_keyword(keyword)
            print(f"\nВакансии, содержащие слово '{keyword}':")
            for vacancy in keyword_vacancies:
                print(f"Вакансия: {vacancy['position']}")

        elif choice == "0":
            print("\nДо свидания! Спасибо за использование нашей системы.")
            break

        else:
            print("\nНеверный выбор. Пожалуйста, выберите пункт из меню.")


if __name__ == "__main__":
    main()
