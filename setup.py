from setuptools import setup, find_packages

setup(
    name='kpo',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'kpo': [
            'background/*.jpg',
            'fonts/*.ttf',
            'fruits/*.png',
            'sounds/*.mp3',
            'best_scores.json',
        ],
    },
    install_requires=[
        'pygame',
    ],
    entry_points={
        'console_scripts': [
            'kpo=kpo.game:main',
        ],
    },
    author='Nagy Lóránt',
    author_email='h267962@stud.u-szeged.hu',
    description='My first python game. If you see a fruit you slice it. Lets have fun!',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Deux03/python_kpo.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
