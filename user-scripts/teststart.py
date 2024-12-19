#!/usr/bin/python3
import argparse
import subprocess
import shlex
import os

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
    parser.add_argument('--graphdb', '-g', required=False, default=f'', help='the url to reach GraphDB')
    parser.add_argument('--type', '-t', required=False, default='ebo-edge-server', help='type of server, defaults to ebo-edge-server, other values are: ebo-enterprise-server or ebo-enterprise-central')
    parser.add_argument('--accept-eula', required=True, help='''for the server to
     start you need to accept eula.
    To accept use: --accept-eula=Yes
    You get link to eula if you start without 'Yes' and check with docker logs''', )
    parser.add_argument('--ca-folder', default=None, help='folder where ' \
        'containers get their ca certificates')
    parser.add_argument('--dns', default=None, help="optional dns server" \
        "address for when container can't reach host dns, because of, for example, VPN")
    parser.add_argument('--http-proxy', default=None, help="optional http proxy " \
        "if not given the host environment variables http_proxy or HTTP_PROXY will be used ")
    parser.add_argument('--https-proxy', default=None, help="optional https proxy " \
        "if not given the host environment variables https_proxy or HTTPS_PROXY will be used ")
    parser.add_argument('--no-proxy', default=None, help="optional no proxy " \
        "if not given the host environment variables no_proxy or NO_PROXY will be used ")
    return parser.parse_args()

def run():
    args = get_arguments('start EBO CS container.')
    name = args.name
    version = args.version
    ip = args.ip
    accept_eula = args.accept_eula
    ca_folder = args.ca_folder
    graphdb = args.graphdb
    server_type = args.type
    dns = args.dns
    http_proxy=args.http_proxy
    https_proxy=args.https_proxy
    no_proxy=args.no_proxy
    image = f'ghcr.io/schneiderelectricbuildings/{server_type}:{version}'
#    image = 'nsp'
    db_vol = f'{name}-db'
    db_folder = '/var/sbo'
    proxy = ''
    if http_proxy:
        proxy += f'-e http_proxy={http_proxy} '
    else:
        if "http_proxy" in os.environ:
            proxy += f'-e http_proxy={os.environ["http_proxy"]} '
        if "HTTP_PROXY" in os.environ:
            proxy += f'-e HTTP_PROXY={os.environ["HTTP_PROXY"]} '
    if https_proxy:
        proxy += f'-e https_proxy={https_proxy} '
    else:
        if "https_proxy" in os.environ:
            proxy += f'-e https_proxy={os.environ["https_proxy"]} '
        if "HTTPS_PROXY" in os.environ:
            proxy += f'-e HTTPS_PROXY={os.environ["HTTPS_PROXY"]} '
    if no_proxy:
        proxy += f'-e no_proxy={no_proxy} '
    else:
        if "no_proxy" in os.environ:
            proxy += f'-e no_proxy={os.environ["no_proxy"]} '
        if "NO_PROXY" in os.environ:
            proxy += f'-e NO_PROXY={os.environ["NO_PROXY"]} '

    cmd = f'docker run -d --name={name} -h {name} ' \
        '--ulimit core=-1 ' \
        '--network bridged-net ' \
        f'-e NSP_ACCEPT_EULA="{accept_eula}" ' \
        f'-e Semantic_Db_URL="{graphdb}" ' \
        f'{proxy}'\
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
