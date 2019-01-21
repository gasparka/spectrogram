from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    name='spectrogram',
    version='0.0.3',
    description="Spectrogram (80MHz bandwidth) accelerator for LimeSDR",
    long_description=readme,
    author="Gaspar Karm",
    author_email='gkarm@live.com',
    packages=find_packages(),
    url='https://github.com/gasparka/spectrogram',
    license="Apache Software License 2.0",
    keywords='spectrogram, fft, limesdr',
    entry_points={
        'console_scripts': [
            'spectrogram = spectrogram.cli:main',
        ],
    }
    # # scripts=['bin/spectrogram']
    # data_files=[('/usr/local/bin', 'bin/spectrogram')],
    # datr
)
