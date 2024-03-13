import sys
from pathlib import Path
from subprocess import call

import yaml
from pyinstaller_versionfile import MetaData, create_versionfile_from_input_file

root_path = Path(__file__).parent
build_path = root_path.joinpath('build')
metadata_path = root_path.joinpath('metadata.yml')
resources_path = root_path.joinpath('resources')
icon_path = resources_path.joinpath('app.ico')
translations = [{'langID': 1033, 'charsetID': 1200}]


def yaml_read(path: Path):
    with open(str(path), 'r', encoding='utf-8') as fp:
        data = yaml.safe_load(fp)
    return data


def yaml_write(path: Path, data):
    with open(str(path), 'w') as fp:
        yaml.dump(data, fp, default_flow_style=False, encoding='utf-8')


class Builder:
    def __init__(self, script_name='__main__.py'):
        self.script_name = script_name
        self.__gen_metadata()

    @property
    def metadata(self):
        return MetaData.from_file(metadata_path.__str__())

    def __gen_metadata(self):
        if not metadata_path.is_file():
            metadata = MetaData(
                version='1.0.0.0',
                company_name='Magnum Cash&Carry',
                file_description='rpamini',
                internal_name='rpamini',
                legal_copyright='Magnum Cash&Carry',
                original_filename=input('original_filename: '),
                product_name='rpamini',
                translations=translations
            )
            yaml_write(metadata_path, metadata.to_dict())
        return self

    @property
    def version_file(self):
        return build_path.joinpath(f'{self.metadata.original_filename}.version')

    def __gen_version_file(self):
        create_versionfile_from_input_file(self.version_file.__str__(), metadata_path.__str__())
        return self

    @property
    def version_list(self):
        return [int(v) for v in self.metadata.version.split('.')]

    def upd_metadata(self, major=False, minor=False, micro=False):
        version = self.version_list
        major_ = version[0] + 1 if major else version[0]
        minor_ = version[1] + 1 if minor else 0 if major else version[1]
        micro_ = version[2] + 1 if micro else 0 if any([major, minor]) else version[2]
        build = version[3] + 1
        metadata = self.metadata
        metadata.set_version(f'{major_}.{minor_}.{micro_}.{build}')
        metadata.translations = translations
        yaml_write(metadata_path, metadata.to_dict())
        self.__gen_version_file()
        return self

    @classmethod
    def build(cls, command):
        call(command)

    def post(self):
        version = ".".join([str(i) for i in self.version_list])
        command = [
            'gh',
            'release',
            'create',
            f'v{version}',
            root_path.joinpath(f'dist\\{builder.metadata.original_filename}.exe').__str__()
        ]
        # call(command)
        print(' '.join(command))


if __name__ == '__main__':
    sys.path.append(root_path.parent.joinpath('venv\\Scripts').__str__())
    build_path.mkdir(exist_ok=True)
    builder = Builder()
    builder.upd_metadata(major=False, minor=False, micro=False)
    command_ = [
        'pyinstaller.exe',
        '-F',
        '-w',
        '--clean',
        '-n',
        builder.metadata.original_filename,
        builder.script_name,
        '--specpath',
        build_path.__str__(),
        '--version-file',
        f'{builder.version_file.name}',
        '-i',
        icon_path.__str__(),
        '--add-data',
        f'{resources_path};se/resources'
    ]
    builder.build(command_)
    builder.post()
