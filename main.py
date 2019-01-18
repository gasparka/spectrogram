import argparse
import logging
import os
import subprocess

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('main')

parser = argparse.ArgumentParser(description='Description of your program')
parser.add_argument('--fpga_program', help='Description for foo argument', action='store_true')
parser.add_argument('--fpga_restore', help='Description for foo argument', action='store_true')
parser.add_argument('--start_server', help='Description for foo argument', action='store_true')
parser.add_argument('--start_gqrx', help='Description for foo argument', action='store_true')
args = vars(parser.parse_args())


def is_arm():
    return os.uname()[4].startswith("arm")


def docker_pull_images():
    log.info('Pulling latest docker images...')
    subprocess.run(f'docker pull gasparka/spectrogram_driver{":arm" if is_arm() else ""}',
                   shell=True,
                   check=True)

    subprocess.run(f'docker pull gasparka/gqrx{":arm" if is_arm() else ""}',
                   shell=True,
                   check=True)


def docker_installed():
    try:
        subprocess.run('docker --version', shell=True, check=True, stdout=subprocess.PIPE)
        return True
    except:
        return False


def docker_image_running(name):
    try:
        res = subprocess.run('docker inspect --format="{{.State.Running}}" ' + name, shell=True, check=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return bool(res)
    except:
        # assume that error is because image does not exist i.e. is not running
        return False


def docker_start_gqrx():
    log.info('Starting gqrx...')
    subprocess.run(
        f'docker run -i --net=host --env="DISPLAY" --volume="$HOME/.Xauthority:/root/.Xauthority:rw" --name gqrx --rm '
        f'gqrx{":arm" if is_arm() else ""}',
        shell=True,
        check=True)


def docker_start_server_daemon():
    log.info('Starting server daemon...')
    subprocess.run(
        f'docker run -d --name spectrogram_driver --rm --privileged '
        f'gasparka/spectrogram_driver{":arm" if is_arm() else ""}',
        shell=True,
        check=True,
        stdout=subprocess.PIPE)


def docker_program_fpga():
    log.info('Programming FPGA, takes ~20 sec...')
    subprocess.run(f'docker run -i --privileged gasparka/spectrogram_driver{":arm" if is_arm() else ""} '
                   'LimeUtil --fpga=LimeSDR-Mini_GW/LimeSDR-Mini_bitstreams/LimeSDR-Mini_lms7_trx_HW_1.2_auto.rpd',
                   shell=True,
                   check=True)


def docker_restore_fpga():
    log.info('Restoring FPGA, takes ~20 sec...')
    subprocess.run(f'docker run -i --privileged gasparka/spectrogram_driver{":arm" if is_arm() else ""} '
                   'LimeUtil --update',
                   shell=True,
                   check=True)


def probe_devices():
    log.info('Probing for devices...')
    # probe for remote driver
    res = subprocess.run(f'docker run -i --privileged gasparka/gqrx{":arm" if is_arm() else ""} '
                         f'/etc/init.d/dbus start; /etc/init.d/avahi-daemon start; SoapySDRUtil --probe="driver=remote"',
                         shell=True,
                         check=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    output = res.stdout.decode()

    remote_available = 'LimeSDR-Mini' in output and 'gatewareVersion=1.65535' in output

    # probe for local device
    res = subprocess.run(f'docker run -i --privileged gasparka/gqrx{":arm" if is_arm() else ""} '
                         f'/etc/init.d/dbus start; /etc/init.d/avahi-daemon start; SoapySDRUtil --probe="driver=lime"',
                         shell=True,
                         check=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    output = res.stdout.decode()

    local_available = 'LimeSDR-Mini' in output
    local_fpga_ok = 'gatewareVersion=1.65535' in output
    log.info(f'remote_available={remote_available}, local_available={local_available}, local_fpga_ok={local_fpga_ok}')
    return remote_available, local_available, local_fpga_ok


if __name__ == '__main__':
    if not docker_installed():
        log.error('Docker is not installed, cant continue. Fix: \n'
                  '$ curl -fsSL https://get.docker.com | sh \n'
                  '$ sudo groupadd docker \n'
                  '$ sudo usermod -aG docker $USER \n'
                  'Log out and log back in so that your group membership is re-evaluated.')
        exit(707)

    docker_pull_images()

    remote_available, local_available, local_fpga_ok = probe_devices()
    if remote_available:
        docker_start_gqrx()
    elif local_available:
        if not local_fpga_ok:
            docker_program_fpga()

        docker_start_server_daemon()
        docker_start_gqrx()

        log.info('Killing local server...')
        subprocess.run('docker kill spectrogram_driver', shell=True)

    log.info('Done!')
