#!/usr/bin/env python3

# Python script to install and configure OpenSSH server on Windows

import subprocess
import argparse
import getpass
import time
import os
import shutil

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
    clear_screen()
    powershell(["Set-Service -Name sshd -StartupType 'Automatic'"])
    powershell(["Start-Service sshd"])
    powershell(["New-NetFirewallRule -Name sshd -DisplayName "
                "'OpenSSH Server (sshd)' -Enabled True -Direction "
                "Inbound -Protocol TCP -Action Allow -LocalPort 22"])
    clear_screen()
    print('OpenSSH server installed')


def install_openssh_server():
    powershell(['Add-WindowsCapability -Online -Name '
                'OpenSSH.Server~~~~0.0.1.0'])
    time.sleep(20)
    set_service_and_firewall()


def show_openssh_server():
    powershell(["Get-WindowsCapability -Online | ? Name -like 'OpenSSH*'"])


def config_ssh():
    # backup old sshd_config file
    src = r'C:\ProgramData\ssh\sshd_config'
    dest = r'C:\ProgramData\ssh\sshd_config.bak'
    shutil.copyfile(src, dest)
    # Read sshd_conf
    with open(f'C:\\users\\{getpass.getuser()}\\desktop\\test.txt', 'r') as sshd_config:
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
    with open(f'C:\\users\\{getpass.getuser()}\\desktop\\test.txt', 'w') as sshd_config:
        sshd_config.write(filedata)

    restart_ssh()

def setup_public_key():
    clear_screen()
    # Create .ssh folder
    powershell(["New-item -Path $env:USERPROFILE -Name .ssh "
                "-ItemType Directory -force"])
    print("Get public key from master server")
    ip_master = input("Enter IP-address of master: ")
    user_master = input("Enter username of master: ")
    if ip_master == "":
        print('Enter a IP-address')
    elif user_master == "":
        print('Enter a username')
    else:
        powershell([f'scp {user_master}@{ip_master}:'
                    f'/home/{user_master}/.ssh/id_rsa.pub '
                    f'c:\\users\\{getpass.getuser()}\\.ssh\\uploaded_key'])
    if os.path.exists(f'c:\\users\\{getpass.getuser()}\\.ssh\\uploaded_key'):
        powershell([r"Get-Content $env:USERPROFILE\.ssh\uploaded_key | "
                    r"Out-File $env:USERPROFILE\.ssh\authorized_keys -Append "
                    r"-Encoding ascii"])
    else:
        print('Public key from master is not in folder .ssh')


def restart_ssh():
    powershell(["Restart-Service sshd"])


def clear_screen():
    powershell(["clear"])


# clear_screen()

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
else:
    parser.print_help()