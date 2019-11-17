"""
A tool executes commands on another computer, like ssh.
Author: sc-1123
This project will put in the North Pole!
"""

from click import group, argument, echo, STRING
from flask import Flask, request
from werkzeug.serving import run_simple as run
from requests import get
from requests.exceptions import ConnectionError
from re import compile as regex
from os import popen
from sys import platform, stderr
from getpass import getpass


def _shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    func()


def _get_ip():
    ip_regex = regex(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])')
    ip_page = get('http://ip.cn')
    return ip_regex.search(ip_page.text).group()


def _pack_command(command: str) -> str:
    packed = ''
    for char in command:
        packed += str(ord(char))
        packed += '%20'
    return packed


def _unpack_command(command: str) -> str:
    unpacked = ''
    for char in command.split():
        unpacked += chr(int(char))
    return unpacked


@group()
def commands():
    pass


@commands.command()
def run_command_collector():
    """Collects commands from other computers, enter password for secure."""
    password = getpass('Password: ')
    collector = Flask(__name__)
    platforms = {'win32': 'Windows', 'darwin': 'Mac', 'linux': 'Linux'}

    @collector.route('/')
    def main_page():
        return f'Airexec command collector running on {platforms[platform]}.'

    @collector.route('/<pwd>/<command>')
    def exec_command(pwd, command):
        if pwd == password:
            unpacked_command = _unpack_command(command)
            cmd = popen(unpacked_command)
            return cmd.read()
        else:
            return 'Invalid password.'

    @collector.route('/<pwd>/terminate')
    def terminate(pwd):
        if pwd == password:
            _shutdown_server()
            return 'Shutting down server...'
        else:
            return 'Invalid password.'

    echo(f'Host: {_get_ip()}')
    run('0.0.0.0', 23333, collector)


@commands.command()
@argument('ip', type=STRING)
def connect(ip: str):
    """Execute commands on the other computer via an activated command collector. Password required."""

    server = f'http://{ip}:23333'
    try:
        r = get(server)
    except ConnectionError:
        echo('Invalid ip.', file=stderr)
    else:
        prompt = f'{r.text.split()[-1][:-1]} >'

        password = getpass('Password: ')
        cur = 1
        echo('Enter ":exit" to quit.')
        while cur != ':exit':
            cur = input(prompt)
            r = get(server + f'/{password}/{_pack_command(cur)}')
            echo(r.text)
        echo('Airexec client terminated.')
        if input('Terminate the command collector?(y/n):') == 'y':
            get(server + f'/{password}/terminate')