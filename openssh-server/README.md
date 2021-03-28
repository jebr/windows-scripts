<p align="center">
	<img alt="Logo" src="https://raw.githubusercontent.com/jebr/windows-scripts/main/images/banner-openssh-server.png">
</p>

# Install and configure OpenSSH server on Windows

A Python executable to install and configure OpenSSH sever on Windows

# Preparations 
Before you can install the OpenSSH server, you must make sure that the master is reachable via the network 
and that a private and public key have been created on the master. 
The master computer is assumed to be a Linux Ubuntu server.

# Preview
<img src="https://raw.githubusercontent.com/jebr/windows-scripts/main/images/openssh-server.png">

# Installation and Usage

> Please note, for the program to work it is important that there is a network connection to the master

To use this application follow the steps below.
1. Download the executable 
2. Start Powershell with Administrator privileges
3. Navigate to the download folder
4. Start the program
5. Follow the steps in the program to install and configure the OpenSSH server
6. Test your SSH connection

The following options are available for using the application:

| Option     | Explanation                             |
|------------|-----------------------------------------|
| --complete | Install and configure OpenSSH server    |
| --install  | Install OpenSSH server                  |
| --config   | Configure OpenSSH server                |
| --getkey   | Get public key from master              |
| --show     | Show info about OpenSSH server          |
| --restart  | Restart OpenSSH server                  |

# Download
[Download link](https://github.com/jebr/windows-scripts/raw/main/openssh-server/openssh-server.exe)

# License

[GNU General Public License version 3](https://raw.githubusercontent.com/jebr/windows-scripts/main/LICENSE)

<hr>

:star: this project in GitHub if you found this automation scripts helpful.
