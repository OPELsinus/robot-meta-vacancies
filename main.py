import sys
import traceback
from contextlib import suppress
from typing import Union

from config import logger, process_list_path
from tools.odines import Odines
from tools.process import kill_process_list
from tools.web import Web


def main():
    pass


if __name__ == '__main__':
    # noinspection PyTypeChecker
    app: Union[Web, Odines] = None
    # ? не убирать данный try, он необходим для того чтобы Pyinstaller не выводил traceback в окошко
    try:
        logger.warning("START")

        main()

        logger.warning("END")
    except (Exception,):
        with suppress(Exception):
            app.quit()
        kill_process_list(process_list_path)
        traceback.print_exc()
        sys.exit(1)
