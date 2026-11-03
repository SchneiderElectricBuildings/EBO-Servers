#!/usr/bin/python3
import subprocess
import sys
from start import get_arguments, exe, _validate_arg


# arguments same as for start-server


def run():
    args = get_arguments('upgrade EBO container.')
    name = args.name
    version = args.version

    _validate_arg(name, '--name')
    _validate_arg(version, '--version')

    old_image = exe(['docker', 'inspect', name, '--format={{.Config.Image}}'])
    old_version = old_image.rpartition(':')[2]
    print(f'Upgrading {name} from {old_version} to {version}')
    db_vol = f'{name}-db'
    db_folder = '/var/sbo'

    exe(['docker', 'stop', name])
    exe(['docker', 'rm', name])
    exe(['docker', 'run', '--rm', '--mount', f'source={db_vol},target={db_folder}', old_image, '/opt/sbo/bin/prepare-upgrade'])

    # start new server
    sys.argv[0] = sys.argv[0].rpartition('/')[0] + '/start.py'
    subprocess.check_call(sys.argv)
    image = exe(['docker', 'inspect', name, '--format={{.Config.Image}}'])

    print(exe(['docker', 'run', '--rm', '--mount', f'source={db_vol},target={db_folder}', image, '/opt/sbo/bin/get-upgrade-log']))

if __name__ == '__main__':
    run()
