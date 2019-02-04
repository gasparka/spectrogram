import subprocess


# no_cache = '--no-cache'
no_cache = ''

subprocess.run(f'docker build {no_cache} -t gasparka/spectrogram .', shell=True)
subprocess.run(f'docker build {no_cache} -t gasparka/spectrogram:arm -f Dockerfile.arm .', shell=True)
subprocess.run(f'docker push gasparka/spectrogram', shell=True)