import sys
import os
import argparse
import subprocess
import tempfile
import time
import socket

parser = argparse.ArgumentParser(description='Run a shell with a network namespace that isolates localhost ports.')
parser.add_argument('--sh', help='Path to the shell.', default='/bin/bash')
parser.add_argument('--ip', help='Path to the `ip` command.', default='/sbin/ip')
parser.add_argument('--unshare', help='Path to the `unshare` command.', default='/usr/bin/unshare')
parser.add_argument('--socat', help='Path to the `socat` command.', default='/usr/bin/socat')
parser.add_argument('--flair', help='Descriptive flair for shell prompt.', default='localhost-singularity')
parser.add_argument('--port', help='Port to proxy from in the inside namespace to the outside namespace.', type=int)
parser.add_argument('--setup', help='Run this command before entering the shell, and terminate it upon shell exit.')
parser.add_argument('--env', help='Pass through this environment variable. (Can be specified more than once.)', default=[], action='append')
parser.add_argument('--verbose', help='Print debug diagnostics.', action='store_true')
parser.add_argument('args', help='Arguments passed to shell.', nargs='*')

args = parser.parse_args()

myself = os.readlink('/proc/self/exe')
myargs = [ x.decode() for x
           in open('/proc/self/cmdline', 'rb').read().split(b'\0')[1:]
           if len(x) > 0]

PATH = os.getenv('PATH')

ENV = { env: os.getenv(env) or '' for env in args.env }

if os.getenv('LOCALHOST_SINGULARITY_PHASE2'):
    uid = os.getenv('LOCALHOST_SINGULARITY_UID')
    gid = os.getenv('LOCALHOST_SINGULARITY_GID')
    tmp = os.getenv('LOCALHOST_SINGULARITY_TMPDIR')

    socat = None
    if args.port:
        socket = os.path.join(tmp, 'wormhole.sock')
        socat = subprocess.Popen([ args.socat, f'UNIX-LISTEN:{socket},reuseaddr,fork', f'TCP:127.0.0.1:{args.port}' ])

    os.system(f'{args.ip} link set lo up')

    unshare = subprocess.run([ args.unshare, '--map-user', uid, '--map-group', gid, myself ] + myargs,
                             env={**ENV,
                                  'LOCALHOST_SINGULARITY_TMPDIR': tmp,
                                  'LOCALHOST_SINGULARITY_PHASE3': '1',
                                  'PATH': PATH})
    if args.verbose:
        print(unshare)

    if socat:
        socat.terminate()
    sys.exit()

if os.getenv('LOCALHOST_SINGULARITY_PHASE3'):
    tmp = os.getenv('LOCALHOST_SINGULARITY_TMPDIR')

    shell_rc = os.path.join(tmp, 'bashrc')
    open(shell_rc, 'w').write(f'''
export PS1="\[\033[01m\]{args.flair}:\[\033[00m\]\$ "
    ''')

    setup = None
    if args.setup:
        setup = subprocess.Popen([ args.setup ])

    shell = subprocess.run([ args.sh, '--rcfile', shell_rc, '-i' ] + args.args,
                           env={**ENV,
                                'PATH': PATH})

    if args.verbose:
        print(shell)

    if setup:
        setup.terminate()
        setup.wait()
    sys.exit(shell.returncode)

uid = os.getuid()
gid = os.getgid()

with tempfile.TemporaryDirectory() as tmp:

    socat = None
    if args.port:
        usocket = os.path.join(tmp, 'wormhole.sock')
        _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _sock.bind(('', 0))
        free_port = _sock.getsockname()[1]
        _sock.close()
        socat = subprocess.Popen([ args.socat, f'TCP-LISTEN:{free_port},reuseaddr,fork', f'UNIX-CLIENT:{usocket}' ])
        print('Proxy listening on port', free_port)

    unshare = subprocess.run([ args.unshare, '--map-root-user', '--net', myself ] + myargs,
                             env={**ENV,
                                  'LOCALHOST_SINGULARITY_UID': str(uid),
                                  'LOCALHOST_SINGULARITY_GID': str(gid),
                                  'LOCALHOST_SINGULARITY_TMPDIR': tmp,
                                  'LOCALHOST_SINGULARITY_PHASE2': '1',
                                  'PATH': PATH})
    if args.verbose:
        print(unshare)

    if socat:
        socat.terminate()
