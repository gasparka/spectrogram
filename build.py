import subprocess


def shell(path, cmd):
    subprocess.run(cmd, shell=True, cwd=path)


# no_cache = '--no-cache'
no_cache = ''

# build the spectrogram driver
n = 'spectrogram_driver:arm'
shell('driver/arm', f'docker build {no_cache} -t {n} .')
shell('driver/arm', f'docker tag {n} gasparka/{n}')
shell('driver/arm', f'docker push gasparka/{n}')

n = 'spectrogram_driver'
shell('driver', f'docker build {no_cache} -t  {n} .')
shell('driver', f'docker tag {n} gasparka/{n}')
shell('driver', f'docker push gasparka/{n}')


# build the spectrogram gui
n = 'spectrogram_gui:arm'
shell('gui', f'docker build {no_cache} -t {n} -f Dockerfile.arm .')
shell('gui', f'docker tag {n} gasparka/{n}')
shell('gui', f'docker push gasparka/{n}')

n = 'spectrogram_gui'
shell('gui', f'docker build {no_cache} -t {n} -f Dockerfile .')
shell('gui', f'docker tag {n} gasparka/{n}')
shell('gui', f'docker push gasparka/{n}')
