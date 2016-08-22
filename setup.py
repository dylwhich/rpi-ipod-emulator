from setuptools import setup, find_packages


def read_license():
    with open("LICENSE") as f:
        return f.read()

setup(
    name='rpi-ipod-emulator',
    packages=find_packages(),
    version='0.1',
    description='Bluetooth iPod emulator for the Raspberry Pi',
    long_description="""Proxies information between an iPod accessory and a bluetooth
device, allowing legacy systems such as car stereos to playback from
and control a bluetooth device""",
    license=read_license(),
    author='Dylan Whichard',
    author_email='dylan@whichard.com',
    url='https://github.com/dylwhich/rpi-ipod-emulator',
    keywords=[
        'ipod'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End-Users',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Linux',
        'Programming Language :: Python',
        'Topic :: Multimedia :: Sound/Audio',
    ],
    install_requires=open('requirements.txt').readlines(),
)
