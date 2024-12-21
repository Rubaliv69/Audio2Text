from setuptools import setup, find_packages

setup(
    name="audio2text",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'PyQt6>=6.8.0',
        'pydub>=0.25.1',
        'SpeechRecognition>=3.10.0',
        'python-docx>=0.8.11',
    ],
    entry_points={
        'console_scripts': [
            'audio2text=src.main:main',
        ],
    },
    author="Liv",
    author_email="liv@example.com",
    description="Une application de conversion audio en texte avec interface graphique",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    keywords="audio, text, conversion, speech recognition",
    url="https://github.com/yourusername/audio2text",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
    ],
    python_requires='>=3.13',
)
