from setuptools import setup, find_packages

setup(
    name='airexec',
    packages=find_packages(),
    version='0.0.1',
    entry_points={
        'console_scripts': [
            'airexec = airexec:commands'
        ]
    }
)
