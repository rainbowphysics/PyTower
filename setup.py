from setuptools import setup

setup(
    name='towerpy',
    version='0.1.0',
    description='Python API for Tower Unite map-editing',
    url='https://github.com/kluberge/TowerPy',
    author='Physics System',
    author_email='rainbowphysicsystem@gmail.com',
    license='MIT License',
    packages=['pytower'],
    install_requires=['requests'],

    # https://pypi.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: File Formats :: JSON',
        'Topic :: Games/Entertainment'
    ]
)
