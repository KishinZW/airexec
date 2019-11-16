"""
A tool executes commands on another computer, like ssh.
Author: sc-1123
This project will put in the North Pole!
"""

from click import group, argument, option, echo
from flask import Flask, request
from werkzeug.serving import run_simple
from requests import get
from re import compile as regex
from os import system


def _shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    func()


def _get_ip():
    ip_regex = regex(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])')
    ip_page = get('http://ip.cn')
    return ip_regex.search(ip_page.text).group()


def _pack_command(command: str):
    packed = ''
    for char in command:
        packed += str(ord(char))
        packed += '%20'
    return packed


def _unpack_command(command: str):
    unpacked = ''
    for char in command.split():
        unpacked += str(ord(char))
        unpacked += '&20'
    return unpacked


@group()
def commands():
    pass


@commands.command()
@option('--password', '-p')
def run_command_collector(password):
    """Collects commands from other computers, enter password for secure."""
    collector = Flask(__name__)

    @collector.route('/')
    def main_page():
        return f'Airexec command collector running on {_get_ip()}.'

    @collector.route('/<pwd>/<command>')
    def exec_command(pwd, command):
        if pwd == password:
            unpacked_command = _unpack_command(command)
            system(unpacked_command)
            return f'ran "{unpacked_command}"'
        else:
            return 'Invalid password.'

    @collector.route('/<pwd>/terminate')
    def terminate(pwd):
        if pwd == password:
            _shutdown_server()
            return 'Shutting down server...'
        else:
            return 'Invalid password.'

    run_simple('0.0.0.0', 23333, collector)
