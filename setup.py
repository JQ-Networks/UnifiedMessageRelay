import sys
from setuptools import setup, find_packages
import unified_message_relay

if sys.version_info < (3, 7):
    raise Exception("Python 3.7 or higher is required. Your version is %s." % sys.version)

long_description = open('README.md', encoding="utf-8").read()

__version__ = unified_message_relay.__VERSION__

setup(
    name='unified-message-relay',
    packages=find_packages(include=['unified_message_relay', 'unified_message_relay.*']),
    version=__version__,
    description='Group Message Forward Framework (supports QQ Telegram Line Discord)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Curtis Jiang',
    url='https://github.com/jqqqqqqqqqq/UnifiedMessageRelay',
    license='MIT',
    python_requires='>=3.7',
    include_package_data=True,
    zip_safe=False,
    keywords=['UMR', 'UnifiedMessageRelay', 'Group chat relay', 'IM', 'messaging'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Typing :: Typed"
    ],
    install_requires=[
        'tgs',
        'imageio',
        'janus',
        'filetype',
        'cairosvg',
        'Pillow',
        'coloredlogs',
        'ffmpy',
        'Wand',
        'pyyaml'
    ],
    entry_points={
        "console_scripts": [
            'unified_message_relay = unified_message_relay.daemon:main'
        ]
    },
    project_urls={
        "Telegram Chat": "https://t.me/s/UnifiedMessageRelayDev",
    }
)
