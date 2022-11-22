#!/usr/bin/python3
import subprocess
import shlex
import sys
import time
from start import get_arguments, exe


# arguments same as for start-server


def run():
    args = get_arguments('upgrade EBO container.')
    name = args.name
    version = args.version

    old_image = exe('docker inspect ' + name + " --format='{{.Config.Image}}'")
    old_version = old_image.rpartition(':')[2]
    print(f'Upgrading {name} from {old_version} to {version}')
    db_vol = f'{name}-db'
    db_folder = '/var/sbo'

    exe(f'docker stop {name}')
    exe(f'docker rm {name}')
    exe(f'docker run --rm --mount source={db_vol},target={db_folder} {old_image} /opt/sbo/bin/prepare-upgrade')

    # start new server
    sys.argv[0] = sys.argv[0].rpartition('/')[0] + '/start.py'
    subprocess.check_call(sys.argv)
    image = exe('docker inspect ' + name + " --format='{{.Config.Image}}'")

    print(exe(f'docker run --rm --mount source={db_vol},target={db_folder} {image} /opt/sbo/bin/get-upgrade-log'))

if __name__ == '__main__':
    run()
