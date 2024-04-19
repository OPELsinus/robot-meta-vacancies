import socket
import sys
from pathlib import Path

from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from tools.json_rw import json_read, json_write
from tools.logs import init_logger
from tools.names import get_hostname
from tools.net_use import net_use

disable_warnings(InsecureRequestWarning)

# ? ROOT
root_path = Path(sys.argv[0]).parent
download_path = Path.home().joinpath('Downloads')

# ? LOCAL
local_path = Path.home().joinpath(f'AppData\\Local\\.rpa')
local_path.mkdir(exist_ok=True, parents=True)
local_env_path = local_path.joinpath('env.json')
if not local_env_path.is_file():
    json_write(local_env_path, {
        "global_path": "\\\\172.16.8.87\\d\\.rpa",
        "global_username": "rpa.robot",
        "global_password": "Aa1234567"
    })
local_env_data = json_read(local_env_path)
process_list_path = local_path.joinpath('process_list.json')
if not process_list_path.is_file():
    process_list_path.write_text('[]', encoding='utf-8')

# ? GLOBAL
global_path = Path(local_env_data['global_path'])
global_username = local_env_data['global_username']
global_password = local_env_data['global_password']
net_use(global_path, global_username, global_password)
global_env_path = global_path.joinpath('env.json')
global_env_data = json_read(global_env_path)

orc_host = global_env_data['orc_host']
orc_port = global_env_data['new_orc_port']
tg_token = global_env_data['tg_token']
smtp_host = global_env_data['smtp_host']
smtp_author = global_env_data['smtp_author']
sprut_username = global_env_data['sprut_username']
sprut_password = global_env_data['sprut_password']
odines_username = global_env_data['odines_username_rpa']
odines_password = global_env_data['odines_password_rpa']
owa_username = global_env_data['owa_username']
owa_password = global_env_data['owa_password']
sed_username = global_env_data['sed_username']
sed_password = global_env_data['sed_password']

# ? PROJECT
project_name = 'robot-meta-vacancies'  # ! FIXME
chat_id = ''  # ! FIXME
robot_name = project_name

project_path = global_path.joinpath(f'.agent').joinpath(project_name).joinpath(get_hostname())
project_path.mkdir(exist_ok=True, parents=True)
config_path = project_path.joinpath('config.json')
if not config_path.is_file():
    json_write(config_path, {
        "share_path": "\\\\172.16.8.87\\d\\TEMP"  # ! FIXME
    })


config_data = json_read(config_path)
share_path = config_data['share_path']
meta_url = config_data['meta_url']
meta_login = config_data['meta_login']
meta_pass = config_data['meta_pass']
skillaz_url = config_data['skillaz_url']
skillaz_test_url = config_data['skillaz_test_url']
to_whom = config_data['to_whom']
excels_saving_path = config_data['excels_saving_path']
mapping_file = config_data['mapping_file']
skillaz_login = config_data['skillaz_login']
skillaz_pass = config_data['skillaz_pass']
skillaz_login_test = config_data['skillaz_login_test']
skillaz_pass_test = config_data['skillaz_pass_test']


download_path = Path.home().joinpath('downloads')
ip_address = socket.gethostbyname(socket.gethostname())

log_path = project_path.joinpath(f'{sys.argv[1]}.log' if len(sys.argv) > 1 else 'dev.log')
logger = init_logger(file_path=log_path, tg_token=tg_token, tg_chat_id=chat_id)

# ? EXAMPLES
# * root_path == C:\Users\user\PycharmProjects\pythonProject
# * local_path == C:\Users\user\AppData\Local\.rpa
# * global_path == \\172.16.8.87\d\.rpa
# * project_path == \\172.16.8.87\d\.rpa\.agent\REPLACE ME\127.0.0.1
# * share_path == \\172.16.8.87\d\TEMP
logger.info('root_path', root_path)
logger.info('local_path', local_path)
logger.info('global_path', global_path)
logger.info('project_path', project_path)
logger.info('share_path', share_path)

engine_kwargs = {
    'username': global_env_data['postgre_db_username'],
    'password': global_env_data['postgre_db_password'],
    'host': global_env_data['postgre_ip'],
    'port': global_env_data['postgre_port'],
    'base': 'orchestrator'
}


