#!/usr/bin/env python3

# Python script to install and configure OpenSSH server on Windows

import subprocess
import argparse
import getpass
import time
import os
import shutil
import socket

parser = argparse.ArgumentParser(description='Python script to install and '
                                             'configure OpenSSH server on '
                                             'Windows')


def escape_cmd(command):
    return command.replace('&', '^&')

def powershell(input_: list) -> str:
    """
    Returns a string when no error
    If an exception occurs the exeption is logged and None is returned
    """
    if sys.platform == 'win32':
        input_ = [escape_cmd(elem) for elem in input_]
    execute = ['powershell.exe'] + input_

    # if DEBUG:
    #     return ' '.join(execute)

    try:
        proc = subprocess.Popen(execute,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                stdin=subprocess.PIPE,
                                cwd=os.getcwd(),
                                env=os.environ)
        proc.stdin.close()
        outs, errs = proc.communicate(timeout=15)
        return outs.decode('U8')
    except Exception as e:
        print(e)
        # logging.warning(e)


def install():
    clear_screen()
    print('Installing OpenSSH server...')
    install_openssh_server()


def set_service_and_firewall():
    powershell(["Set-Service -Name sshd -StartupType 'Automatic'"])
    print('- OpenSSH service set to automatic')
    powershell(["Start-Service sshd"])
    print('- OpenSSH service started')
    powershell(["New-NetFirewallRule -Name sshd -DisplayName "
                "'OpenSSH Server (sshd)' -Enabled True -Direction "
                "Inbound -Protocol TCP -Action Allow -LocalPort 22"])
    print('- OpenSSH firewal rule set')


def install_openssh_server():
    powershell(['Add-WindowsCapability -Online -Name '
                'OpenSSH.Server~~~~0.0.1.0'])
    time.sleep(20)
    print('- OpenSSH server installed')
    set_service_and_firewall()


def show_openssh_server():
    show = powershell(["Get-WindowsCapability -Online | ? Name -like 'OpenSSH*'"])
    print(show)


def config_ssh():
    # backup old sshd_config file
    src = r'C:\ProgramData\ssh\sshd_config'
    dest = r'C:\ProgramData\ssh\sshd_config.bak'
    shutil.copyfile(src, dest)
    print(r'- Backup of c:\programdata\ssh\sshd_config.bak')

    # Read sshd_conf
    with open(r'C:\ProgramData\ssh\sshd_config', 'r') as sshd_config:
        filedata = sshd_config.read()

    filedata = filedata.replace('#PubkeyAuthentication yes',
                                'PubkeyAuthentication yes')
    filedata = filedata.replace('#PasswordAuthentication yes',
                                'PasswordAuthentication no')
    filedata = filedata.replace('Match Group administrators',
                                '#Match Group administrators')
    filedata = filedata.replace(
        'AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys',
        '#AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys')

    # Replace text
    with open(r'C:\ProgramData\ssh\sshd_config', 'w') as sshd_config:
        sshd_config.write(filedata)

    print('- Config file changed')

    restart_ssh()

    print('- sshd service restarted')


def setup_public_key():
    # Create .ssh folder
    powershell(["New-item -Path $env:USERPROFILE -Name .ssh "
                "-ItemType Directory -force"])

    print(f'- Create folder .ssh for user {getpass.getuser()}\n')

    print("Pull public key from master server")

    while True:
        ip_master = input("Enter IP-address of master: ")
        if ip_master == "":
            print('Enter an IP-address')
            continue
        else:
            break
    while True:
        user_master = input("Enter username of master: ")
        if user_master == "":
            print('Enter an username')
            continue
        else:
            break

    powershell([f'scp {user_master}@{ip_master}:'
                f'/home/{user_master}/.ssh/id_rsa.pub '
                f'c:\\users\\{getpass.getuser()}\\.ssh\\uploaded_key'])
    print('- id_rsa.pub copied to uploaded_key')


    if os.path.exists(f'c:\\users\\{getpass.getuser()}\\.ssh\\uploaded_key'):
        powershell([r"Get-Content $env:USERPROFILE\.ssh\uploaded_key | "
                    r"Out-File $env:USERPROFILE\.ssh\authorized_keys -Append "
                    r"-Encoding ascii"])
        print('- Public key master added to authorized_keys file')
    else:
        print('- Public key from master is not in folder .ssh')

    end()


def restart_ssh():
    powershell(["Restart-Service sshd"])


def clear_screen():
    powershell(["clear"])

def end():
    print('- OpenSSH server installed and configured\n- You are ready to '
          'test the connection from the master to this computer\n'
          f'{getpass.getuser()}@{socket.gethostbyname(socket.gethostname())}')

clear_screen()

# Optional arguments
parser.add_argument("--install", help="Install OpenSSH server",
                    action="store_true")
parser.add_argument("--show", help="Show info about OpenSSH server",
                    action="store_true")
parser.add_argument("--config", help="Configure OpenSSH server",
                    action="store_true")
parser.add_argument("--getkey", help="Get public key from master",
                    action="store_true")
parser.add_argument("--restart", help="Restart OpenSSH server",
                    action="store_true")
parser.add_argument("--complete", help="Install and configure OpenSSH server",
                    action="store_true")


args = parser.parse_args()

if args.install:
    install()
elif args.show:
    show_openssh_server()
elif args.config:
    config_ssh()
elif args.getkey:
    setup_public_key()
elif args.restart:
    restart_ssh()
elif args.complete:
    install()
    config_ssh()
    setup_public_key()
else:
    parser.print_help()
