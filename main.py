import asyncio
import codecs
import datetime
import encodings
import json
import os
import shutil
import sys
import time
import traceback
from contextlib import suppress
from time import sleep
from typing import Union

import pandas as pd
import requests
from openpyxl.reader.excel import load_workbook
from pywinauto import keyboard
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import tg_bot
from config import (
    logger,
    process_list_path,
    engine_kwargs,
    meta_url,
    skillaz_url,
    skillaz_test_url,
    download_path,
    excels_saving_path,
    skillaz_login,
    skillaz_login_test,
    skillaz_pass,
    skillaz_pass_test,
    meta_login,
    meta_pass,
    mapping_file,
)
from models import Base, add_to_db, get_all_data_by_status, update_in_db
from tg_bot import check_for_commands, API_TOKEN, main_tg_bot
from tools.odines import Odines
from tools.process import kill_process_list
from tools.web import Web

import pyautogui as pag


step_meta = True
step_skillaz = True
step_excel = True

months = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}


def get_code(try_num):

    code = asyncio.run(main_tg_bot(try_num))

    # asyncio.run(main_tg_bot((API_TOKEN, try_num)))
    # asyncio.run(check_for_commands((API_TOKEN, try_num))
    # code = await check_for_commands(API_TOKEN, try_num)
    # print('###', code)

    return code


def wait_excel_downloaded():
    found = False
    path = None
    for i in range(230):
        for file in os.listdir(download_path):
            if (
                ".csv" in file
                and "crdownload" not in file
                and (time.time() - os.path.getmtime(os.path.join(download_path, file)))
                <= 100
            ):
                file_orig_name = os.path.splitext(file)[0]
                extension = os.path.splitext(file)[1]
                dt = str(datetime.datetime.now().strftime("%d_%m_%Y %H_%M_%S"))
                print(file_orig_name, extension)
                shutil.move(
                    os.path.join(download_path, file),
                    os.path.join(
                        excels_saving_path, f"{file_orig_name} {dt}{extension}"
                    ),
                )
                path = os.path.join(
                    excels_saving_path, f"{file_orig_name} {dt}{extension}"
                )
                found = True
                break
        if found:
            break
        sleep(1)

    return path


def main():

    Session = sessionmaker()

    engine = create_engine(
        "postgresql+psycopg2://{username}:{password}@{host}:{port}/{base}".format(
            **engine_kwargs
        ),
        connect_args={"options": "-csearch_path=robot"},
    )
    Base.metadata.create_all(bind=engine)
    Session.configure(bind=engine)
    session = Session()

    if step_meta:

        web = Web()

        web.run()

        web.get(meta_url)

        if os.path.exists(
            r"\\172.16.8.87\d\.rpa\.agent\robot-meta-vacancies\cookies.json"
        ):
            with open(
                r"\\172.16.8.87\d\.rpa\.agent\robot-meta-vacancies\cookies.json", "r"
            ) as file:
                json_data = file.read()
                cookies = json.loads(json_data)
                # print(cookies)
                for cookie_key, cookie_val in cookies.items():
                    print(cookie_key, cookie_val)
                    if cookie_key == "datr":
                        continue
                    web.driver.add_cookie({"name": cookie_key, "value": cookie_val})
            web.driver.refresh()

        print()

        if web.wait_element(
            '//a[contains(text(), "Войти через Facebook")]', timeout=10
        ):

            web.driver.delete_all_cookies()
            web.driver.refresh()

            web.find_element('//a[contains(text(), "Войти через Facebook")]').click()

            web.find_element('//*[@id="email"]').click()
            web.find_element('//*[@id="email"]').type_keys(meta_login)

            web.find_element('//*[@id="pass"]').click()
            web.find_element('//*[@id="pass"]').type_keys(meta_pass)

            web.find_element('//*[@id="loginbutton"]').click()

            # 2FA AUTH #

            if web.wait_element('//*[@id="checkpointSubmitButton"]', timeout=30):

                for tries in range(10):
                    logger.info(f"LOGGING IN. TRY: {tries}")
                    code = get_code(tries)

                    web.find_element('//*[@id="approvals_code"]').click()
                    web.find_element('//*[@id="approvals_code"]').type_keys(code)

                    web.find_element('//*[@id="checkpointSubmitButton"]').click()

                    with suppress(Exception):
                        download_buttons = web.find_elements(
                            '//div[contains(text(), "Скачать")]'
                        )
                        print("SUCCESSFULLY LOGGED IN!")
                        break
        sleep(1)

        # I------I #
        # download_buttons = web.find_elements('//div[contains(text(), "Скачать")]')

        all_cookies = web.driver.get_cookies()
        cookies_dict = {}
        for cookie in all_cookies:
            cookies_dict[cookie["name"]] = cookie["value"]

        with open(
            r"\\172.16.8.87\d\.rpa\.agent\robot-meta-vacancies\cookies.json", "w"
        ) as outfile:
            json.dump(cookies_dict, outfile)

        download_buttons = web.find_elements(
            '//div[contains(text(), "Скачать")]', timeout=180
        )

        for download_button in download_buttons:

            try:

                download_button.click()

                sleep(2)

                if web.wait_element(
                    '//span[contains(text(), "Новые лиды: 0")]', timeout=10
                ):

                    web.find_element('//a[contains(text(), "Отмена")]').click()

                    continue

                if step_excel:

                    try:
                        new_leads = int(
                            web.find_element(
                                '//span[contains(text(), "Новые лиды")]', timeout=5
                            )
                            .get_attr("text")
                            .split(":")[1]
                            .replace(" ", "")
                        )
                    except:
                        new_leads = int(
                            web.find_element(
                                '//span[contains(text(), "новы")]', timeout=5
                            )
                            .get_attr("text")
                            .split()[0]
                            .replace(" ", "")
                        )

                    web.execute_script_click_xpath(
                        '//span[contains(text(), "Новые лиды")]'
                    )

                    web.find_element(
                        '//a[contains(text(), "CSV")]', timeout=150
                    ).click()
                    print(new_leads)

                    print("Clicked")

                    try:
                        path = wait_excel_downloaded()

                        file = path

                        df = pd.DataFrame()

                        if ".xlsb" in file:
                            df = pd.read_excel(file, engine="pyxlsb")
                        elif ".csv" in file:
                            df = pd.read_csv(
                                file,
                                delimiter="\t",
                                encoding="utf-16",
                                on_bad_lines="skip",
                            )
                        else:
                            df = pd.read_excel(file)

                        # df.columns = ['id', 'created_date', 'city', 'job', 'first_name', 'last_name', 'phone_number']

                        df = df.rename(
                            columns={
                                "created_time": "created_date",
                                "выберите_ваш_город": "city",
                                "выберите_желаемую_вакансию": "job",
                                "қалаңызды_таңдаңыз": "city",
                                "қажетті_бос_орынды_таңдаңыз": "job",
                            }
                        )

                        print(df.columns)

                        # df['created_date'] = pd.to_datetime(df['created_date'], unit='D', origin='1899-12-31')
                        df["created_date"] = pd.to_datetime(df["created_date"])

                        for i in range(len(df)):

                            created_date = df["created_date"].iloc[i]
                            print(created_date)
                            city = df["city"].iloc[i]
                            job = df["job"].iloc[i]
                            if "full_name" in df.columns:
                                full_name = str(df["full_name"].iloc[i])
                                first_name = full_name.split(" ", maxsplit=1)[0].strip()
                                last_name = (
                                    full_name.split(" ", maxsplit=1)[1].strip()
                                    if len(full_name.split(" ", maxsplit=1)) > 1
                                    else "."
                                )
                            else:
                                first_name = df["first_name"].iloc[i].strip()
                                last_name = df["last_name"].iloc[i].strip()
                            phone_number = str(df["phone_number"].iloc[i]).strip()[-10:]

                            add_to_db(
                                session=session,
                                status_="new",
                                skillaz_status_="new",
                                skillaz_action_=None,
                                response_date_=created_date,
                                city_=city,
                                job_=job,
                                first_name_=first_name,
                                last_name_=last_name,
                                phone_number_=phone_number,
                            )

                            # Add updating status to 'new' if already exists
                    except:
                        traceback.print_exc()

                    web.find_element('//a[contains(text(), "Закрыть")]').click()

                    # web.quit()

                    # break

            except:
                traceback.print_exc()

    rows = get_all_data_by_status(session, ["new", "processing"])

    while len(rows) != 0:

        rows = get_all_data_by_status(session, ["new"])

        try:
            row = rows[0]
        except:
            break

        # if row.job not in ['кассир', 'продавец', 'кассир', 'сатушы']:
        #     continue

        # if row.last_name != 'Арай':
        #     continue

        print(row.job, row.city, row.first_name, row.last_name)

        if step_skillaz:

            skillaz_action = None

            update_in_db(
                session=session,
                row=row,
                status_="processing",
                skillaz_status_="processing",
                skillaz_action_=skillaz_action,
                previous_status_=None,
                error_reason_=None,
                response_date_=row.response_date,
                city_=row.city,
                job_=row.job,
                first_name_=row.first_name,
                last_name_=row.last_name,
                phone_number_=row.phone_number,
            )

            try:
                web = Web()
                web.run()
                web.get(skillaz_url)

                web.find_element('//button[contains(text(), "корп")]').click()

                web.find_element('//*[@id="userNameInput"]').click()
                web.find_element('//*[@id="userNameInput"]').type_keys(skillaz_login)

                web.find_element('//*[@id="passwordInput"]').click()
                web.find_element('//*[@id="passwordInput"]').type_keys(skillaz_pass)

                web.find_element('//span[contains(text(), "Вход")]').click()

                web.find_element('//*[@id="filter-by-fio"]').click()
                web.find_element('//*[@id="filter-by-fio"]').type_keys(row.phone_number)
                web.find_element(
                    '//div[(text()="Точное совпадение") and (@class="WS__radio_option")]'
                ).click()
                sleep(1)
                print(f"Here1 | {datetime.datetime.now()}")
                web.wait_element('(//input[contains(@id, "react-select")])[4]')
                print(f"Here2 | {datetime.datetime.now()}")
                sleep(1.5)
                candidates_count = web.find_element(
                    '//div[@data-testid="candidates-found"]'
                ).get_attr("text")
                print(f"Here3 | {datetime.datetime.now()}")
                sleep(1)

                job_title = None
                city_skillaz = row.city
                previous_status = "-"

                mapping = pd.read_excel(mapping_file)

                job_title = mapping[
                    (mapping["рус"] == row.job) | (mapping["каз"] == row.job)
                ]["рус"].iloc[0]

                id_ = mapping[
                    (mapping["рус"] == row.job) | (mapping["каз"] == row.job)
                ]["ID"].iloc[0]

                # if row.job == 'кассир':
                #     job_title = 'кассир'
                # elif row.job == 'продавец' or row.job == 'сатушы':
                #     job_title = 'продавец'

                # if row.city == 'астана':
                #     city_skillaz = 'нур-султан'

                # ----- Добавляем нового кандидата -----

                if candidates_count == "Всего 0 кандидатов":

                    web.find_element(
                        '//button[contains(text(), "Добавить кандидата")]'
                    ).click()

                    web.wait_element('//*[@id="VacancyId"]')
                    sleep(1)

                    print()

                    web.find_element('//*[@id="VacancyId"]').click(double=False)
                    sleep(2.1)
                    keyboard.send_keys(str(id_))
                    sleep(2.1)
                    # web.execute_script_click_xpath('//*[@id="VacancyId"]')

                    all_vacancies = web.find_elements(
                        '//div[@class="WS_select__option css-yt9ioa-option"]'
                    )
                    all_vacancies.append(web.find_element('//span[@id="aria-context"]'))
                    print(all_vacancies)
                    print(
                        web.find_element('//span[@id="aria-context"]').get_attr("text")
                    )
                    print("CHPOK:", all_vacancies[-1].get_attr("text"))

                    for vacancy in all_vacancies:

                        vacancy_text = vacancy.get_attr("text").lower()
                        print(vacancy_text, " | ", vacancy.selector)

                    print("-----------------------------------")
                    for vacancy in all_vacancies:

                        vacancy_text = vacancy.get_attr("text").lower()
                        if vacancy_text == "":
                            vacancy_text = vacancy.get_attr("innerHTML").lower()

                        print(vacancy_text, " | ", vacancy.selector)

                        # if row.city == 'алматы'
                        if (
                            job_title in vacancy_text
                            and city_skillaz in vacancy_text
                            and vacancy.selector == '//span[@id="aria-context"]'
                        ):  # city_skillaz == 'нур-султан':
                            print("TYPING ENTER!!!")
                            # web.find_element('//*[@id="VacancyId"]').click(double=False)
                            sleep(1.5)
                            keyboard.send_keys("{ENTER}")
                            sleep(0.3)
                            keyboard.send_keys("{ENTER}")
                            break
                            # web.find_element('//*[@id="VacancyId"]').type_keys(web.keys.ENTER)
                        if (
                            job_title in vacancy_text
                            and city_skillaz in vacancy_text
                            and vacancy.selector != '//span[@id="aria-context"]'
                        ):  # city_skillaz != 'нур-султан':  # and '520000379' in vacancy_text:

                            print("HERE!!!")
                            print(vacancy.selector)
                            try:
                                vacancy.scroll()
                            except:
                                print("bad scroll")
                            vacancy.click()
                            # web.execute_script_click_xpath(vacancy.selector)
                            break

                    sleep(3)

                    web.find_element(
                        '//*[@id="LastName-createCandidateModelForm-input"]'
                    ).click()
                    web.find_element(
                        '//*[@id="LastName-createCandidateModelForm-input"]'
                    ).type_keys(row.last_name)

                    web.find_element(
                        '//*[@id="Name-createCandidateModelForm-input"]'
                    ).click()
                    web.find_element(
                        '//*[@id="Name-createCandidateModelForm-input"]'
                    ).type_keys(row.first_name)

                    web.find_element(
                        '//*[@id="PhoneNumber-createCandidateModelForm-input"]'
                    ).click()
                    web.find_element(
                        '//*[@id="PhoneNumber-createCandidateModelForm-input"]'
                    ).type_keys(row.phone_number)

                    found_duplicate = False

                    if web.wait_element(
                        '//*[contains(text(), "дубликат кандидата")]', timeout=2
                    ):
                        print("DUPLO")
                        found_duplicate = True

                    web.find_element(
                        '//*[@id="Email-createCandidateModelForm-input"]'
                    ).click()

                    if web.wait_element(
                        '//*[contains(text(), "дубликат кандидата")]', timeout=2
                    ):
                        print("DUPLO")
                        found_duplicate = True

                    # web.execute_script_click_xpath('//label/div[contains(@data-original-title, "Таргет")]')

                    web.find_element(
                        '//label/div[contains(@data-original-title, "Таргет")]'
                    ).click()

                    # Check for duplicates #

                    if web.wait_element(
                        '//*[contains(text(), "Найдено 0 дубликатов кандидата")]',
                        timeout=1,
                    ):

                        logger.info("Not found duplicate!")

                    # ---------------------

                    web.find_element(
                        '//*[@id="PhoneNumber-createCandidateModelForm-input"]'
                    ).click()

                    if web.wait_element(
                        '//*[contains(text(), "дубликат кандидата")]', timeout=10
                    ):
                        print("DUPLO")
                        found_duplicate = True

                    sleep(3)

                    if not found_duplicate:
                        # web.execute_script_click_xpath('//button[contains(text(), "Сохранить")]')
                        logger.info(
                            f"Успешно сохранён: {row.last_name} {row.first_name}"
                        )
                        skillaz_action = "New"
                        sleep(3)

                # ----- Редактируем существующего кандидата -----

                else:

                    sleep(3)

                    # web.driver.refresh()
                    #
                    # web.find_element('//*[@id="filter-by-fio"]').click()
                    # web.find_element('//*[@id="filter-by-fio"]').type_keys(row.phone_number)
                    # web.find_element('//div[(text()="Точное совпадение") and (@class="WS__radio_option")]').click()
                    #
                    # web.wait_element('//input[contains(@id, "react-select-16-input")]')

                    current_status = web.find_element(
                        '//span[@data-testid="candidate-status"]'
                    ).get_attr("text")

                    previous_status = current_status

                    if current_status != "Новый":

                        date_edited = web.find_element(
                            '//span[@data-testid="candidate-status"]/following-sibling::span[(string-length(text()) > 1) and (contains(text(), "20"))]'
                        ).get_attr("text")
                        date_edited = date_edited.replace(",", "")

                        day_ = int(date_edited.split()[0])
                        month_ = date_edited.split()[1]
                        year = int(date_edited.split()[2])
                        hour = int(date_edited.split(":")[0].split()[-1])
                        minute = int(date_edited.split(":")[1])

                        month_ = months.get(month_)

                        print(day_, month_, year)

                        day = datetime.datetime(year, month_, day_, hour, minute, 0)

                        # total_days = (datetime.date.today() - day).days
                        total_hours = (
                            datetime.datetime.now()
                            - datetime.datetime(year, month_, day_, hour, minute, 0)
                        ).total_seconds() / 3600
                        print(f"TOTAL HOURS: {total_hours}")

                        sleep(2)

                        change_status = False

                        # ALL STATEMENTS #

                        if current_status == "Выход на работу":
                            print("KEK1")
                            if total_hours >= 2160:
                                print("KEK1.1")
                                change_status = True
                                # web.execute_script_click_xpath('//div[(text()="Новый") and (@class="WS__radio_option")]')

                        if current_status in ["Полиграф", "ПФИ проведено", "Резерв"]:
                            print("KEK2")
                            if total_hours >= 720:
                                print("KEK2.1")
                                change_status = True
                                # web.execute_script_click_xpath('//div[(text()="Новый") and (@class="WS__radio_option")]')

                        if current_status in [
                            "Интервью с HR не предусмотрено",
                            'Не предусмотрен этап "Полиграф”',
                            'Не предусмотрен этап "Тестирование”',
                            "Не предусмотрена стажировка",
                            "«Не предусмотрено интервью с заказчиком",
                            "Недозвон",
                            "Неявка",
                            "Неявка на интервью",
                            "Неявка на полиграф",
                            "Отсутствует вакансия/Резерв",
                            "Перезвонить",
                            "Рекомендован на другой филиал",
                            "Телефонное интервью с HR не предусмотрено",
                        ]:
                            print("KEK3")
                            if total_hours >= 48:
                                print("KEK3.1")
                                change_status = True
                                # web.execute_script_click_xpath('//div[(text()="Новый") and (@class="WS__radio_option")]')

                        if current_status in [
                            "Видеоконференция",
                            "Интервью с заказчиком",
                            "Интервью с HR",
                            "Неявка на полиграф",
                            "Одобрен по резюме",
                            "Отсутствует вакансия/Резерв",
                            "Пригласить на собеседование",
                            "Проверка СБ",
                            "Риски выявлены/ На согласование руководителю",
                            "Риски выявлены/ На согласование руководителю",
                            "Риски не выявлены",
                            "Собеседование с заказчиком",
                            "Собеседование с руководителем подразделения",
                            "Согласовано (ознакомительный день пройден). Предоставление документов",
                            "Стажировка/Ознакомительный день",
                            "Телефонное интервью",
                            "Телефонное интервью с HR",
                            "Тестирование онлайн",
                            "Тестирование оффлайн",
                            "Пригласить на собеседование",
                            "Рекомендован на другую должность",
                            "ИС пройден",
                            "Испытательный срок пройден",
                        ]:
                            print("KEK4")
                            if total_hours >= 360:
                                print("KEK4.1")
                                change_status = True
                                # web.execute_script_click_xpath('//div[(text()="Новый") and (@class="WS__radio_option")]')

                        if current_status in [
                            "Документы приняты/на оформление",
                            "Документы отправлены на доработку",
                            "Подписание трудового договора/оформление",
                            "Проверка документов",
                            "Согласовано (ознакомительный день пройден). Предоставление документов",
                            "На рассмотрении у заказчика",
                            "Черный список",
                            "Приём кандидата согласован",
                            "Решение о найме",
                        ]:
                            print("KEK5")
                            change_status = False

                        if current_status in [
                            "Гарантийный период",
                            "Гарантийный период не предусмотрен",
                            "Гарантийный период пройден",
                            "Новый",
                            "Стажировка/Ознакомительный день не пройден",
                            "Гарантийный период не пройден",
                            "ИС не пройден",
                            "Испытательный срок не пройден",
                            "Не подтвержден",
                            "Отказ",
                            "Отказ от прохождения",
                            "Отказ по результатам проверки СБ",
                            "Отказ по резюме",
                            "Отказ/Проблемы с пакетом документов",
                            "Риски выявлены/Отказ (Полиграф)",
                            "Самоотказ (Завершен)",
                        ]:
                            print("KEK6")
                            change_status = True

                        # ----- Изменение статуса -----

                        print(f"STATUS: {change_status}")

                        if change_status:

                            print("CHANGING STATUS!")

                            web.find_element(
                                '//button[contains(text(), "Изменить статус")]'
                            ).click()

                            web.wait_element(
                                '//div[contains(text(), "возможные статусы")]'
                            )

                            web.execute_script_click_xpath(
                                '//div[contains(text(), "возможные статусы")]'
                            )

                            web.wait_element(
                                '//div[(text()="Новый") and (@class="WS__radio_option")]'
                            )

                            sleep(0.3)

                            web.execute_script_click_xpath(
                                '//div[(text()="Новый") and (@class="WS__radio_option")]'
                            )

                            print()
                            sleep(1.6)
                            web.find_element(
                                '//div[contains(text(), "Оставить комментарий")]/../textarea'
                            ).click()
                            web.find_element(
                                '//div[contains(text(), "Оставить комментарий")]/../textarea'
                            ).type_keys(".")

                            # web.find_element('//button[@data-testid="button-status-change"]').click()
                            #
                            # if web.wait_element('//div[contains(text(), "Текущий статус кандидата такой же как запрошен для изменения")]', timeout=5):
                            #     print('Closing the form')
                            #     web.find_element('//div[@data-testid="button-modal-close"]').click()
                            sleep(1.5)
                            web.find_element(
                                '//div[@data-testid="button-modal-close"]'
                            ).click()

                            # Editting the candidate

                            web.find_element(
                                '//span[contains(text(), "Редактировать кандидата")]'
                            ).click()

                            web.find_element(
                                '//div[@data-testid="VacancyId-input-clear"]'
                            ).click()

                            web.find_element('//*[@id="VacancyId"]').click(double=False)
                            sleep(2.1)
                            keyboard.send_keys(str(id_))
                            sleep(2.1)
                            # web.execute_script_click_xpath('//*[@id="VacancyId"]')

                            all_vacancies = web.find_elements(
                                '//div[@class="WS_select__option css-yt9ioa-option"]'
                            )
                            all_vacancies.append(
                                web.find_element('//span[@id="aria-context"]')
                            )
                            print(all_vacancies)
                            print(
                                web.find_element('//span[@id="aria-context"]').get_attr(
                                    "text"
                                )
                            )
                            print("CHPOK:", all_vacancies[-1].get_attr("text"))

                            for vacancy in all_vacancies:
                                vacancy_text = vacancy.get_attr("text").lower()
                                print(vacancy_text, " | ", vacancy.selector)

                            print("-----------------------------------")

                            for vacancy in all_vacancies:

                                vacancy_text = vacancy.get_attr("text").lower()
                                if vacancy_text == "":
                                    vacancy_text = vacancy.get_attr("innerHTML").lower()

                                print(vacancy_text, " | ", vacancy.selector)

                                # if row.city == 'алматы'
                                if (
                                    str(id_) in vacancy_text
                                    and city_skillaz in vacancy_text
                                    and vacancy.selector == '//span[@id="aria-context"]'
                                ):  # city_skillaz == 'нур-султан':
                                    print("TYPING ENTER!!!")
                                    # web.find_element('//*[@id="VacancyId"]').click(double=False)
                                    sleep(1.5)
                                    keyboard.send_keys("{ENTER}")
                                    sleep(0.3)
                                    keyboard.send_keys("{ENTER}")
                                    break
                                    # web.find_element('//*[@id="VacancyId"]').type_keys(web.keys.ENTER)

                                if (
                                    str(id_) in vacancy_text
                                    and city_skillaz in vacancy_text
                                    and vacancy.selector != '//span[@id="aria-context"]'
                                ):  # city_skillaz != 'нур-султан':  # and '520000379' in vacancy_text:

                                    print("HERE!!!")
                                    print(vacancy.selector)
                                    try:
                                        vacancy.scroll()
                                    except:
                                        print("bad scroll")
                                    vacancy.click()
                                    # web.execute_script_click_xpath(vacancy.selector)
                                    break

                            # all_vacancies = web.find_elements('//div[@class="WS_select__option css-yt9ioa-option"]')
                            # print(all_vacancies)
                            #
                            # for vacancy in all_vacancies:
                            #
                            #     print(vacancy.get_attr('text'))
                            #
                            #     vacancy_text = vacancy.get_attr('text').lower()
                            #
                            #     if job_title in vacancy_text and row.city in vacancy_text:  # and '520000379' in vacancy_text:
                            #
                            #         print('HERE!!!')
                            #         print(vacancy.selector)
                            #
                            #         vacancy.click()
                            #         break

                            sleep(3)
                            try:
                                web.find_element(
                                    '//label/div[contains(@data-original-title, "Таргет")]'
                                ).click()
                            except:
                                web.execute_script_click_xpath(
                                    '//label/div[contains(@data-original-title, "Таргет")]'
                                )

                            sleep(1)
                            # web.execute_script_click_xpath('//button[contains(text(), "Сохранить")]')

                            skillaz_action = "Изменил существующий"

                    sleep(10)

                update_in_db(
                    session=session,
                    row=row,
                    status_="success",
                    skillaz_status_="success",
                    skillaz_action_=skillaz_action,
                    previous_status_=previous_status,
                    error_reason_=None,
                    response_date_=row.response_date,
                    city_=row.city,
                    job_=row.job,
                    first_name_=row.first_name,
                    last_name_=row.last_name,
                    phone_number_=row.phone_number,
                )
                sleep(0.7)
                # status_: str, response_date_: datetime, city_: str, job_: str,
                # first_name_: str, last_name_: str, phone_number_: str, skillaz_status_: str
                web.quit()
                print()

            except:
                traceback.print_exc()
                # web.quit()
                update_in_db(
                    session=session,
                    row=row,
                    status_="failed",
                    skillaz_status_="failed",
                    skillaz_action_=skillaz_action,
                    previous_status_=None,
                    error_reason_=str(traceback.format_exc())[:500],
                    response_date_=row.response_date,
                    city_=row.city,
                    job_=row.job,
                    first_name_=row.first_name,
                    last_name_=row.last_name,
                    phone_number_=row.phone_number,
                )


if __name__ == "__main__":
    # noinspection PyTypeChecker
    app: Union[Web, Odines] = None
    # ? не убирать данный try, он необходим для того чтобы Pyinstaller не выводил traceback в окошко
    data = {
        "process": 51,
        "config": 62,
        "machines": [2]
    }

    try:

        logger.warning("START")

        main()

        logger.warning("END")

        requests.post('https://rpa.magnum.kz:8443/enqueue', json=data, verify=False)


    except (Exception,):
        with suppress(Exception):
            app.quit()
        kill_process_list(process_list_path)
        traceback.print_exc()
        sys.exit(1)
