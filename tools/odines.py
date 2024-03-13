from contextlib import suppress
from pathlib import Path
from threading import Thread
from time import sleep

from pyautogui import moveTo
from pywinauto import mouse

from config import global_env_data
from tools.app import App, process_list_path
from tools.process import kill_process_list


class Odines(App):
    def __init__(
            self,
            timeout=60,
            base="go_copy",
            path=r"C:\Program Files\1cv8\8.3.13.1644\bin\1cv8.exe",
    ):
        self.base = base
        self.path = path
        self.version = "8.3.16.1148" if "8.3.16.1148" in path else "8.3.13.1644"
        super(Odines, self).__init__(Path(self.path), timeout=timeout, debug=True, clear='{VK_CLEAR}{VK_END}+{VK_HOME}{BACKSPACE}{VK_DELETE}')
        self.fuckn_tooltip = {
            "class_name": "V8ConfirmationWindow",
            "control_type": "ToolTip",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        self.root_selector = {
            "title_re": "1С:Предприятие - .*",
            "class_name": "V8TopLevelFrame",
            "control_type": "Window",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        self.root_window = None
        if self.wait_element(self.root_selector, timeout=1):
            self.root_window = self.find_element(self.root_selector, timeout=1)

    def wait_fuckn_tooltip(self):
        with suppress(Exception):
            window = self.find_element(self.root_selector)
            position = window.element.element_info.rectangle.mid_point()
            moveTo(position[0], position[1])
            self.wait_element(self.fuckn_tooltip, until=False)

    # * ----------------------------------------------------------------------------------------------------------------
    def auth(self, close_all=False):
        self.run()

        self.parent_switch(
            {
                "title": "Запуск 1С:Предприятия",
                "class_name": (
                    "V8TopLevelFrameTaxiStarter"
                    if self.version == "8.3.16.1148"
                    else "V8NewLocalFrameBaseWnd"
                ),
                "control_type": "Window",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
            }
        )
        self.find_element(
            {
                "title": self.base,
                "class_name": "",
                "control_type": "ListItem",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
            }
        ).click(double=True, set_focus=True)
        sleep(0.1)

        self.parent_switch(
            {
                "title": (
                    "1С:Предприятие"
                    if self.version == "8.3.16.1148"
                    else "1С:Предприятие. Доступ к информационной базе"
                ),
                "class_name": (
                    "V8TopLevelFrameTaxiStarter"
                    if self.version == "8.3.16.1148"
                    else "V8NewLocalFrameBaseWnd"
                ),
                "control_type": "Window",
                "found_index": 0,
            },
            timeout=30,
        )
        self.find_element(
            {
                "title": "",
                "class_name": "",
                "control_type": "ComboBox",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
            }
        ).type_keys(
            global_env_data["odines_username"],
            self.keys.TAB,
            clear=True,
            click=True,
            set_focus=True,
        )

        self.find_element(
            {
                "title": "",
                "class_name": "",
                "control_type": "Edit",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
            }
        ).type_keys(
            global_env_data["odines_password"],
            self.keys.TAB,
            clear=True,
            click=True,
            set_focus=True,
        )
        self.find_element(
            {
                "title": "OK",
                "class_name": "",
                "control_type": "Button",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
            }
        ).click(set_focus=True)

        # ? skip err
        message_ = {
            "title": "Конфигурация базы данных не соответствует сохраненной конфигурации.\nПродолжить?",
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        button_ = {
            "title": "Да",
            "class_name": "",
            "control_type": "Button",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if not self.wait_element(self.root_selector, timeout=15):
            if self.wait_element(message_, timeout=0.1):
                self.find_element(button_, timeout=1).click(double=True)
                self.wait_element(message_, timeout=5, until=False)

        self.parent_switch(self.root_selector, timeout=180, maximize=True)
        self._stack = {0: self.parent}
        self._current_index = 0
        self.root_window = self.parent
        if close_all:
            self.open('Окна', 'Закрыть все')
        self.close_all_windows(10, 1)
        Thread(target=self.close_1c_config, daemon=True).start()

    def quit(self):
        for i in range(10):
            if self.wait_element(
                    {
                        "class_name": "#32770",
                        "control_type": "Window",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.1,
            ):
                el = self.find_elements(
                    {
                        "class_name": "#32770",
                        "control_type": "Window",
                        "visible_only": True,
                        "enabled_only": True,
                        "parent": None,
                    },
                    timeout=0.1,
                )[-1]
                el.close()
                if el.wait_element(
                        {
                            "title": "Нет",
                            "class_name": "CCPushButton",
                            "control_type": "Button",
                            "visible_only": True,
                            "enabled_only": True,
                            "found_index": 0,
                            "parent": None,
                        },
                        timeout=0.1,
                ):
                    el.find_element(
                        {
                            "title": "Нет",
                            "class_name": "CCPushButton",
                            "control_type": "Button",
                            "visible_only": True,
                            "enabled_only": True,
                            "found_index": 0,
                            "parent": None,
                        },
                        timeout=0.1,
                    ).click()
            else:
                break
        for i in range(10):
            if self.wait_element(
                    {
                        "class_name": "V8NewLocalFrameBaseWnd",
                        "control_type": "Window",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.1,
            ):
                self.find_elements(
                    {
                        "class_name": "V8NewLocalFrameBaseWnd",
                        "control_type": "Window",
                        "visible_only": True,
                        "enabled_only": True,
                        "parent": None,
                    },
                    timeout=0.1,
                )[-1].close()
            else:
                break
        # * подключиться к окну если есть
        if self.wait_element(self.root_selector, timeout=0.1):
            self.root = self.find_element(self.root_selector)
            self.root.set_focus()
            # * закрыть окна
            with suppress(Exception):
                self.close_all_windows(10, 1, True)
                self.open("Файл", "Выход")
                if self.wait_element(
                        {
                            "title": "Завершить работу с программой?",
                            "class_name": "",
                            "control_type": "Pane",
                            "visible_only": True,
                            "enabled_only": True,
                            "found_index": 0,
                            "parent": None,
                        },
                        timeout=5,
                ):
                    self.find_element(
                        {
                            "title": "Да",
                            "class_name": "",
                            "control_type": "Button",
                            "visible_only": True,
                            "enabled_only": True,
                            "found_index": 0,
                            "parent": None,
                        },
                        timeout=1,
                    ).click()
                    self.wait_element(
                        {
                            "title": "Да",
                            "class_name": "",
                            "control_type": "Button",
                            "visible_only": True,
                            "enabled_only": True,
                            "found_index": 0,
                            "parent": None,
                        },
                        timeout=5,
                        until=False,
                    )
            sleep(2)

        kill_process_list(process_list_path)
        self._stack = {0: None}
        self._current_index = 0
        sleep(0.1)

    # * ----------------------------------------------------------------------------------------------------------------
    def open(self, *steps, maximize_inner=False):
        try:
            # sleep(1)
            self.wait_fuckn_tooltip()
            for n, step in enumerate(steps):
                if n:
                    if not self.wait_element(
                            {
                                "title": step,
                                "class_name": "",
                                "control_type": "MenuItem",
                                "visible_only": True,
                                "enabled_only": True,
                                "found_index": 0,
                                "parent": self.root,
                            },
                            timeout=2,
                    ):
                        if n - 1:
                            self.find_element(
                                {
                                    "title": steps[n - 1],
                                    "class_name": "",
                                    "control_type": "MenuItem",
                                    "visible_only": True,
                                    "enabled_only": True,
                                    "found_index": 0,
                                    "parent": self.root,
                                },
                                timeout=5,
                            ).click()
                        else:
                            self.find_element(
                                {
                                    "title": steps[n - 1],
                                    "class_name": "",
                                    "control_type": "Button",
                                    "visible_only": True,
                                    "enabled_only": True,
                                    "found_index": 0,
                                    "parent": self.root,
                                },
                                timeout=5,
                            ).click()
                    self.find_element(
                        {
                            "title": step,
                            "class_name": "",
                            "control_type": "MenuItem",
                            "visible_only": True,
                            "enabled_only": True,
                            "found_index": 0,
                            "parent": self.root,
                        },
                        timeout=5,
                    ).click()
                else:
                    self.find_element(
                        {
                            "title": step,
                            "class_name": "",
                            "control_type": "Button",
                            "visible_only": True,
                            "enabled_only": True,
                            "found_index": 0,
                            "parent": self.root,
                        },
                        timeout=5,
                    ).click()
            if maximize_inner:
                self.maximize_inner_window()
        except Exception as ex:
            # traceback.print_exc()
            print(f"exception while opening {ex}")

    def filter_date(
            self,
            date_form: str = None,
            date_to: str = None,
            parent: App.Element = None,
    ):
        if not any((date_form, date_to)):
            raise Exception("filter_date - укажите дату")

        self.find_element(
            {
                "title": "Установить интервал дат...",
                "class_name": "",
                "control_type": "Button",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
                "parent": parent or self.root,
            }
        ).click(set_focus=True)
        self.parent_switch(
            {
                "title": "Настройка периода",
                "class_name": "V8NewLocalFrameBaseWnd",
                "control_type": "Window",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
                "parent": self.root.element.parent(),
            },
            resize=True,
        )
        if date_form:
            self.find_element(
                {
                    "title": "",
                    "class_name": "",
                    "control_type": "RadioButton",
                    "visible_only": True,
                    "enabled_only": True,
                    "found_index": 0,
                }
            ).type_keys(self.keys.TAB, date_form, click=True)
        if date_to:
            self.find_element(
                {
                    "title": "",
                    "class_name": "",
                    "control_type": "RadioButton",
                    "visible_only": True,
                    "enabled_only": True,
                    "found_index": 1,
                }
            ).type_keys(self.keys.TAB, date_to, click=True)
        self.find_element(
            {
                "title": "OK",
                "class_name": "",
                "control_type": "Button",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
            }
        ).click(set_focus=True)
        if not self.wait_element(
                {
                    "title": "OK",
                    "class_name": "",
                    "control_type": "Button",
                    "visible_only": True,
                    "enabled_only": True,
                    "found_index": 0,
                },
                until=False,
                timeout=5,
        ):
            raise Exception("filter_date - ошибка")
        self.parent_back(1)

    def filter(self, params: dict, parent: App.Element = None):
        """
        Args:
            parent: your element or root window
            params: {<checkbox_title>: (<condition_value>, <input_1_value>, <input_2_value>, ...)}
        """
        self.find_element(
            {
                "title": "Установить отбор и сортировку списка...",
                "class_name": "",
                "control_type": "Button",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
                "parent": parent or self.root,
            }
        ).click(set_focus=True)
        self.parent_switch(
            {
                "title": "Отбор и сортировка",
                "class_name": "V8NewLocalFrameBaseWnd",
                "control_type": "Window",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
                "parent": self.root.element.parent(),
            },
            resize=True
        )
        section = self.find_element(
            {
                "class_name": "",
                "control_type": "CheckBox",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
            }
        ).parent()

        controls = dict()
        checkbox = None
        condition = None
        inputs = list()
        for element in section.element.children():
            if element.element_info.control_type == "CheckBox":
                if checkbox:
                    controls[checkbox.element_info.name] = {
                        "checkbox": {
                            "element": App.Element(checkbox),
                            "toggle_state": bool(
                                checkbox.iface_toggle.CurrentToggleState
                            ),
                            "enabled": checkbox.element_info.enabled,
                        },
                        "condition": {
                            "element": App.Element(condition),
                            "current_value": condition.iface_value.CurrentValue,
                            "enabled": condition.element_info.enabled,
                        },
                        "inputs": tuple(
                            {
                                "element": App.Element(e),
                                "current_value": e.iface_value.CurrentValue,
                                "enabled": e.element_info.enabled,
                            }
                            for e in inputs
                        ),
                    }
                    condition = None
                    inputs = list()
                checkbox = element
            if element.element_info.control_type == "Edit":
                if not condition:
                    condition = element
                else:
                    inputs.append(element)
        controls[checkbox.element_info.name] = {
            "checkbox": {
                "element": App.Element(checkbox),
                "toggle_state": bool(checkbox.iface_toggle.CurrentToggleState),
                "enabled": checkbox.element_info.enabled,
            },
            "condition": {
                "element": App.Element(condition),
                "current_value": condition.iface_value.CurrentValue,
                "enabled": condition.element_info.enabled,
            },
            "inputs": tuple(
                {
                    "element": App.Element(e),
                    "current_value": e.iface_value.CurrentValue,
                    "enabled": e.element_info.enabled,
                }
                for e in inputs
            ),
        }
        section_r = section.element.rectangle()
        section_m = section_r.mid_point()
        section_h = section_r.bottom - section_r.top
        for key in params:
            element_r = controls[key]["checkbox"]["element"].element.rectangle()
            if section_r.bottom < element_r.bottom:
                element_m = element_r.mid_point()
                wheel_dist = round((section_m.y - element_m.y) / (section_h / 8.66))
                mouse.scroll(coords=section_m, wheel_dist=wheel_dist)

            if not controls[key]["checkbox"]["toggle_state"]:
                controls[key]["checkbox"]["element"].draw_outline()
                controls[key]["checkbox"]["element"].click()
            if not controls[key]["condition"]["current_value"].lower() == params[key][0].lower():
                controls[key]["condition"]["element"].draw_outline()
                controls[key]["condition"]["element"].type_keys(
                    "^{VK_DOWN}", click=True
                )
                list_items = self.find_element(
                    {
                        "title": "",
                        "class_name": "",
                        "control_type": "List",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                    }
                ).element.children()
                [e for e in list_items if e.element_info.name.lower() == params[key][0].lower()][0].click_input()
            for n, value in enumerate(params[key][1:]):
                controls[key]["inputs"][n]["element"].draw_outline()
                controls[key]["inputs"][n]["element"].type_keys(
                    value, self.keys.TAB, click=True, clear=True, protect_first=True
                )

        self.find_element(
            {
                "title": "OK",
                "class_name": "",
                "control_type": "Button",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
            }
        ).click(set_focus=True)
        if not self.wait_element(
                {
                    "title": "OK",
                    "class_name": "",
                    "control_type": "Button",
                    "visible_only": True,
                    "enabled_only": True,
                    "found_index": 0,
                },
                until=False,
                timeout=5,
        ):
            raise Exception("filter - ошибка")
        self.parent_back(1)

    def action(
            self,
            name: str = "Вывести список...",
            parent: App.Element = None,
    ):
        self.find_element(
            {
                "title": "Действия",
                "class_name": "",
                "control_type": "Button",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
                "parent": parent or self.root,
            }
        ).click()
        self.parent_switch(
            {
                "title": "Действия",
                "class_name": "",
                "control_type": "Menu",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
                "parent": self.root.element.parent(),
            }
        )
        self.find_element(
            {
                "title": name,
                "class_name": "",
                "control_type": "MenuItem",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
            }
        ).click()
        if not self.wait_element(
                {
                    "title": "Действия",
                    "class_name": "",
                    "control_type": "Menu",
                    "visible_only": True,
                    "enabled_only": True,
                    "found_index": 0,
                    "parent": self.root.element.parent(),
                },
                until=False,
                timeout=5,
        ):
            raise Exception("action - ошибка")
        self.parent_back(1)

    def close_all(self):
        self.open("Окна", "Закрыть все")

    def save(self, path: Path):
        if path.is_file():
            path.unlink()
        self.open("Файл", "Сохранить")
        self.parent_switch(
            {
                "title": "Сохранение",
                "class_name": "#32770",
                "control_type": "Window",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
                "parent": self.root.element.parent(),
            }
        )
        self.find_element(
            {
                "title": "Тип файла:",
                "class_name": "AppControlHost",
                "control_type": "ComboBox",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
            }
        ).click()
        self.find_element(
            {
                "title": "Лист Excel2007-... (*.xlsx)",
                "class_name": "",
                "control_type": "ListItem",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
            }
        ).click()
        self.find_element(
            {
                "title": "Имя файла:",
                "class_name": "Edit",
                "control_type": "Edit",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
            }
        ).type_keys(path.__str__(), click=True, clear=True, protect_first=True)
        self.find_element(
            {
                "title": "Сохранить",
                "class_name": "Button",
                "control_type": "Button",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
            }
        ).click()
        if not self.wait_element(
                {
                    "title": "Сохранить",
                    "class_name": "Button",
                    "control_type": "Button",
                    "visible_only": True,
                    "enabled_only": True,
                    "found_index": 0,
                },
                until=False,
                timeout=5,
        ):
            raise Exception("export_table - ошибка")
        self.parent_back(1)

    def export_table(
            self,
            path: Path,
            parent: App.Element = None,
    ):
        self.action("Вывести список...", parent)
        self.parent_switch(
            {
                "title": "Вывести список",
                "class_name": "V8NewLocalFrameBaseWnd",
                "control_type": "Window",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
                "parent": self.root.element.parent(),
            },
            resize=True,
        )
        self.find_element(
            {
                "title": "ОК",
                "class_name": "",
                "control_type": "Button",
                "visible_only": True,
                "enabled_only": True,
                "found_index": 0,
            }
        ).click()
        if not self.wait_element(
                {
                    "title": "ОК",
                    "class_name": "",
                    "control_type": "Button",
                    "visible_only": True,
                    "enabled_only": True,
                    "found_index": 0,
                },
                until=False,
                timeout=1800,
        ):
            raise Exception("build_table - ошибка")
        self.parent_back(1)
        self.save(path)

    def maximize_inner_window(self, timeout=0.1):
        self.root.type_keys('%+r', set_focus=True)
        if self.wait_element(
                {
                    "title": "Развернуть",
                    "class_name": "",
                    "control_type": "Button",
                    "visible_only": True,
                    "enabled_only": True,
                    "found_index": 0,
                    "parent": self.root,
                },
                timeout=timeout,
        ):
            self.find_element(
                {
                    "title": "Развернуть",
                    "class_name": "",
                    "control_type": "Button",
                    "visible_only": True,
                    "enabled_only": True,
                    "found_index": 0,
                    "parent": self.root,
                }
            ).click()

    def check_1c_error(self, count=1):
        while count > 0:
            count -= 1
            # * Конфигурация базы данных не соответствует сохраненной конфигурации -------------------------------------
            if self.wait_element(
                    {
                        "title": "Конфигурация базы данных не соответствует сохраненной конфигурации.\nПродолжить?",
                        "class_name": "",
                        "control_type": "Pane",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.2,
            ):
                error_message = (
                    "Конфигурация базы данных не соответствует сохраненной конфигурации"
                )
                raise Exception(error_message)

            # * Ошибка при вызове метода контекста ---------------------------------------------------------------------
            if self.wait_element(
                    {
                        "title_re": "Ошибка при вызове метода контекста (.*)",
                        "class_name": "",
                        "control_type": "Pane",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.2,
            ):
                error_message = "Ошибка при вызове метода контекста"
                raise Exception(error_message)

            # * Ошибка исполнения отчета -------------------------------------------------------------------------------
            if self.wait_element(
                    {
                        "title": "Ошибка исполнения отчета",
                        "class_name": "",
                        "control_type": "Pane",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.2,
            ):
                error_message = "Ошибка исполнения отчета"
                raise Exception(error_message)

            # * Операция не выполнена ----------------------------------------------------------------------------------
            if self.wait_element(
                    {
                        "title": "Операция не выполнена",
                        "class_name": "",
                        "control_type": "Pane",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.2,
            ):
                error_message = "Операция не выполнена"
                raise Exception(error_message)

            # * Конфликт блокировок при выполнении транзакции ----------------------------------------------------------
            if self.wait_element(
                    {
                        "title_re": "Конфликт блокировок при выполнении транзакции:.*",
                        "class_name": "",
                        "control_type": "Pane",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.2,
            ):
                error_message = "Конфликт блокировок при выполнении транзакции"
                raise Exception(error_message)

            # * Введенные данные не отображены в списке, так как не соответствуют отбору -------------------------------
            if self.wait_element(
                    {
                        "title": "Введенные данные не отображены в списке, так как не соответствуют отбору.",
                        "class_name": "",
                        "control_type": "Pane",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.2,
            ):
                error_message = "Введенные данные не отображены в списке, так как не соответствуют отбору"
                raise Exception(error_message)

            # * critical В поле введены некорректные данные ------------------------------------------------------------
            if self.wait_element(
                    {
                        "title_re": "В поле введены некорректные данные.*",
                        "class_name": "",
                        "control_type": "Pane",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.2,
            ):
                error_message = "critical В поле введены некорректные данные"
                raise Exception(error_message)

            # * critical Не удалось провести ---------------------------------------------------------------------------
            if self.wait_element(
                    {
                        "title_re": "Не удалось провести.*",
                        "class_name": "",
                        "control_type": "Pane",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.2,
            ):
                error_message = "critical Не удалось провести"
                raise Exception(error_message)

            # * Сеанс работы завершен администратором ------------------------------------------------------------------
            if self.wait_element(
                    {
                        "title": "Сеанс работы завершен администратором.",
                        "class_name": "",
                        "control_type": "Pane",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.2,
            ):
                error_message = "critical Сеанс работы завершен администратором"
                raise Exception(error_message)

            # * Сеанс отсутствует или удален ---------------------------------------------------------------------------
            if self.wait_element(
                    {
                        "title_re": "Сеанс отсутствует или удален.*",
                        "class_name": "",
                        "control_type": "Pane",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.2,
            ):
                error_message = "critical Сеанс отсутствует или удален"
                raise Exception(error_message)

            # * Неизвестное окно ошибки ---------------------------------------------------------------------------
            if self.wait_element(
                    {
                        "title": "1С:Предприятие",
                        "class_name": "V8NewLocalFrameBaseWnd",
                        "control_type": "Window",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0.2,
            ):
                error_message = "critical Неизвестное окно ошибки"
                raise Exception(error_message)

    def close_1c_error(self):
        # * Ошибка исполнения отчета -----------------------------------------------------------------------------------
        selector_ = {
            "title": "Ошибка исполнения отчета",
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(selector_, timeout=0.1):
            with suppress(Exception):
                self.find_element(
                    {
                        "title": "OK",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=1,
                ).click(double=True)
            self.wait_element(selector_, timeout=5, until=False)
            return False

        # * Ошибка при вызове метода контекста -------------------------------------------------------------------------
        selector_ = {
            "title_re": "Ошибка при вызове метода контекста (.*)",
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(selector_, timeout=0.1):
            with suppress(Exception):
                self.find_element(
                    {
                        "title": "OK",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=1,
                ).click(double=True)
            self.wait_element(selector_, timeout=5, until=False)
            return False

        # * Завершить работу с программой? -----------------------------------------------------------------------------
        selector_ = {
            "title": "Завершить работу с программой?",
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(selector_, timeout=0.1):
            with suppress(Exception):
                self.find_element(
                    {
                        "title": "Да",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=1,
                ).click(double=True)
            self.wait_element(selector_, timeout=5, until=False)
            return False

        # * Операция не выполнена --------------------------------------------------------------------------------------
        selector_ = {
            "title": "Операция не выполнена",
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(selector_, timeout=0.1):
            with suppress(Exception):
                self.find_element(
                    {
                        "title": "OK",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=1,
                ).click(double=True)
            self.wait_element(selector_, timeout=5, until=False)
            return False

        # * Конфликт блокировок при выполнении транзакции --------------------------------------------------------------
        selector_ = {
            "title_re": "Конфликт блокировок при выполнении транзакции:.*",
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(selector_, timeout=0.1):
            with suppress(Exception):
                self.find_element(
                    {
                        "title": "OK",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=1,
                ).click(double=True)
            self.wait_element(selector_, timeout=5, until=False)
            return False

        # * Введенные данные не отображены в списке, так как не соответствуют отбору -----------------------------------
        selector_ = {
            "title": "Введенные данные не отображены в списке, так как не соответствуют отбору.",
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(selector_, timeout=0.1):
            with suppress(Exception):
                self.find_element(
                    {
                        "title": "OK",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=1,
                ).click(double=True)
            self.wait_element(selector_, timeout=5, until=False)
            return False

        # * Данные были изменены. Сохранить изменения? -----------------------------------------------------------------
        selector_ = {
            "title": "Данные были изменены. Сохранить изменения?",
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(selector_, timeout=0.1):
            with suppress(Exception):
                self.find_element(
                    {
                        "title": "Нет",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=1,
                ).click(double=True)
            self.wait_element(selector_, timeout=5, until=False)
            return False

        # * critical В поле введены некорректные данные ----------------------------------------------------------------
        selector_ = {
            "title_re": "В поле введены некорректные данные.*",
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(selector_, timeout=0.1):
            with suppress(Exception):
                self.find_element(
                    {
                        "title": "Да",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=1,
                ).click(double=True)
            self.wait_element(selector_, timeout=5, until=False)
            return True

        # * critical Не удалось провести -------------------------------------------------------------------------------
        selector_ = {
            "title_re": 'Не удалось провести ".*',
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(selector_, timeout=0.1):
            with suppress(Exception):
                self.find_element(
                    {
                        "title": "OK",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=1,
                ).click(double=True)
            self.wait_element(selector_, timeout=5, until=False)
            return True

        # * Сеанс работы завершен администратором ----------------------------------------------------------------------
        selector_ = {
            "title": "Сеанс работы завершен администратором.",
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(selector_, timeout=0.1):
            with suppress(Exception):
                self.find_element(
                    {
                        "title": "Завершить работу",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=1,
                ).click(double=True)
            self.wait_element(selector_, timeout=5, until=False)
            return True

        # * Сеанс отсутствует или удален -------------------------------------------------------------------------------
        selector_ = {
            "title_re": "Сеанс отсутствует или удален.*",
            "class_name": "",
            "control_type": "Pane",
            "visible_only": True,
            "enabled_only": True,
            "found_index": 0,
            "parent": None,
        }
        if self.wait_element(selector_, timeout=0.1):
            with suppress(Exception):
                self.find_element(
                    {
                        "title": "Завершить работу",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=1,
                ).click(double=True)
            self.wait_element(selector_, timeout=5, until=False)
            return True

    def close_1c_config(self):
        while True:
            with suppress(Exception):
                self.find_element(
                    {
                        "title_re": "В конфигурацию ИБ внесены изменения.*",
                        "class_name": "",
                        "control_type": "Pane",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0,
                )
                self.find_element(
                    {
                        "title": "Нет",
                        "class_name": "",
                        "control_type": "Button",
                        "visible_only": True,
                        "enabled_only": True,
                        "found_index": 0,
                        "parent": None,
                    },
                    timeout=0,
                ).click(log=False)

    def close_all_windows(self, count=10, idx=1, ext=False):
        root_window = self.root_window.element
        if ext:
            with suppress(Exception):
                # * закрыть всплывашку
                self.close_1c_error()
                self.open("Окна", "Закрыть все")
        while True:
            if (
                    len(
                        self.find_elements(
                            {
                                "title": "Закрыть",
                                "class_name": "",
                                "control_type": "Button",
                                "visible_only": True,
                                "enabled_only": True,
                                "parent": root_window,
                            },
                            timeout=0.1,
                        )
                    )
                    > idx
            ):
                # * закрыть всплывашку
                if len(list(self._stack.keys())) > 1:
                    self.close_1c_error()
                # * закрыть
                with suppress(Exception):
                    self.find_element(
                        {
                            "title": "Закрыть",
                            "class_name": "",
                            "control_type": "Button",
                            "visible_only": True,
                            "enabled_only": True,
                            "found_index": idx,
                            "parent": root_window,
                        },
                        timeout=0.1,
                    ).click()
                # * закрыть всплывашку
                if len(list(self._stack.keys())) > 1:
                    self.close_1c_error()
            else:
                break
            # ! выход
            count -= 1
            if count <= 0:
                raise Exception("Не все окна закрыты")


if __name__ == "__main__":
    app = Odines()
    app.auth()
    print("SUCCESS")
    print("sleep 3 sec")
    sleep(3)
    app.quit()
