from setuptools import setup, find_packages

setup(
    name="mlbb_bot",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        'pyTelegramBotAPI',
        'python-dotenv',
        'setuptools',
    ],
    python_requires='>=3.6',
    author='Your Name',
    description='Telegram бот для Mobile Legends: Bang Bang',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)