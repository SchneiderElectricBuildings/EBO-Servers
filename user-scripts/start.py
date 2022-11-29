#!/usr/bin/python3
import argparse
import subprocess
import shlex

def exe(cmd):
    try:
        print('running:', cmd)
        return subprocess.check_output(shlex.split(cmd)).decode('utf-8').strip()
    except Exception as e:
        print('Exception', e)
        raise


def get_arguments(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--name', '-n', required=True, help='name of the container')
    parser.add_argument('--version', '-v', required=True, help='version of server to start')
    parser.add_argument('--ip', '-i', required=True, help='ip address of the container')
    parser.add_argument('--accept-eula', required=True, help='''for the server to
     start you need to accept eula.
    To accept use: --accept-eula=Yes
    You get link to eula if you start without 'Yes' and check with docker logs''', )
    parser.add_argument('--crashes-folder', default='/var/crash', help='folder shared ' \
        'between containers that stores crash dumps')
    parser.add_argument('--ca-folder', default=None, help='folder where ' \
        'containers get their ca certificates')
    parser.add_argument('--dns', default=None, help="optional dns server" \
        "address for when container can't reach host dns, because of, for example, VPN")
    return parser.parse_args()

def run():
    args = get_arguments('start EBO CS container.')
    name = args.name
    version = args.version
    ip = args.ip
    accept_eula = args.accept_eula
    crash_folder = args.crashes_folder
    ca_folder = args.ca_folder
    dns = args.dns
    image = f'ghcr.io/schneiderelectricbuildings/ebo-edge-server:{version}'
    db_vol = f'{name}-db'
    db_folder = '/var/sbo'

    cmd = f'docker run -d --name={name} -h {name} ' \
        '--ulimit core=-1 ' \
        '--restart always ' \
        '--network bridged-net ' \
        f'--mount type=bind,source={crash_folder},target=/var/crash ' \
        f'-e NSP_ACCEPT_EULA="{accept_eula}" ' \
        f'--ip {ip} ' \
        f'--mount source={db_vol},target={db_folder} '
    if ca_folder:
        cmd += f'--mount type=bind,source={ca_folder},target=/usr/local/share/ca-certificates '
    if dns:
        cmd += f'--dns {dns} '
    cmd += image
    exe(cmd)

if __name__ == '__main__':
    run()
