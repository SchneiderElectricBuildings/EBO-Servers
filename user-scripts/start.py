#!/usr/bin/python3
import argparse
import subprocess
import os

def exe(cmd):
    try:
        print('running:', cmd)
        return subprocess.check_output(cmd).decode('utf-8').strip()
    except Exception as e:
        print('Exception', e)
        raise


def _validate_arg(value, name):
    """Reject values that contain whitespace or shell metacharacters to prevent argument injection."""
    if not value:
        return value
    # Allow only alphanumeric, dots, hyphens, underscores, colons, slashes, and equals
    import re
    if not re.fullmatch(r'[A-Za-z0-9._:/@=\-]+', value):
        raise ValueError(f"Invalid characters in {name}: {value!r}")
    return value


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

        # Validate all user-supplied values to prevent Docker argument injection
    _validate_arg(name, '--name')
    _validate_arg(version, '--version')
    _validate_arg(ip, '--ip')
    _validate_arg(server_type, '--type')
    _validate_arg(accept_eula, '--accept-eula')
    _validate_arg(graphdb, '--graphdb')
    _validate_arg(ca_folder, '--ca-folder')
    _validate_arg(dns, '--dns')

    cmd = [
        'docker', 'run', '-d',
        f'--name={name}',
        '-h', name,
        '--ulimit', 'core=-1',
        '--restart', 'always',
        '--network', 'bridged-net',
        '-e', f'NSP_ACCEPT_EULA={accept_eula}',
        '-e', f'Semantic_Db_URL={graphdb}',
    ]
    if http_proxy:
        cmd += ['-e', f'http_proxy={http_proxy}']
    else:
        if "http_proxy" in os.environ:
            cmd += ['-e', f'http_proxy={os.environ["http_proxy"]}']
        if "HTTP_PROXY" in os.environ:
            cmd += ['-e', f'HTTP_PROXY={os.environ["HTTP_PROXY"]}']
    if https_proxy:
        cmd += ['-e', f'https_proxy={https_proxy}']
    else:
        if "https_proxy" in os.environ:
            cmd += ['-e', f'https_proxy={os.environ["https_proxy"]}']
        if "HTTPS_PROXY" in os.environ:
            cmd += ['-e', f'HTTPS_PROXY={os.environ["HTTPS_PROXY"]}']
    if no_proxy:
        cmd += ['-e', f'no_proxy={no_proxy}']
    else:
        if "no_proxy" in os.environ:
            cmd += ['-e', f'no_proxy={os.environ["no_proxy"]}']
        if "NO_PROXY" in os.environ:
            cmd += ['-e', f'NO_PROXY={os.environ["NO_PROXY"]}']
    cmd += [
        '--ip', ip,
        '--mount', f'source={db_vol},target={db_folder}',
    ]
    if ca_folder:
        cmd += ['--mount', f'type=bind,source={ca_folder},target=/usr/local/share/ca-certificates']
    dump_path = '/var/crash'
    if os.path.exists(dump_path):
        cmd += ['--mount', f'type=bind,source={dump_path},target={dump_path}']
    if dns:
        cmd += ['--dns', dns]
    cmd.append(image)
    exe(cmd)

if __name__ == '__main__':
    run()
