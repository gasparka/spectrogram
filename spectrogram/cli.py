#!/usr/bin/env python

import argparse
import logging
import os
import platform
import subprocess

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('main')

IMAGE_NAME = 'gasparka/spectrogram{}'.format(":arm" if os.uname()[4].startswith("arm") else "")


def docker_pull():
    log.info('Pulling latest docker image...')
    subprocess.run('docker pull {}'.format(IMAGE_NAME),
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
        'docker run -i --net=host --env="DISPLAY" --volume="$HOME/.Xauthority:/root/.Xauthority:rw" --name gqrx --rm {} gqrx'.format(IMAGE_NAME),
        shell=True,
        check=True)


def docker_start_server_daemon():
    log.info('Starting server daemon...')
    subprocess.run('docker kill spectrogram_server', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(
        'docker run -d --name spectrogram_server --rm --privileged {} SoapySDRServer --bind'.format(IMAGE_NAME),
        shell=True,
        check=True)


def docker_program_fpga():
    log.info('Programming FPGA, takes ~20 sec...')
    subprocess.run('docker run -i --privileged {} LimeUtil --fpga=/LimeSDR-Mini_lms7_trx_HW_1.2_auto.rpd'.format(IMAGE_NAME),
                   shell=True,
                   check=True)


def docker_restore_fpga():
    log.info('Restoring FPGA, takes ~20 sec...')
    subprocess.run('docker run -i --privileged {} LimeUtil --update'.format(IMAGE_NAME),
                   shell=True,
                   check=True)


def probe_devices():
    log.info('Probing for LimeSDR-Mini devices...')
    res = subprocess.run('docker run -i --privileged {} SoapySDRUtil --probe="driver=remote"'.format(IMAGE_NAME),
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    output = res.stdout.decode()

    remote_available = 'LimeSDR-Mini' in output and 'gatewareVersion=1.0' in output

    # probe for local device
    res = subprocess.run('docker run -i --privileged {} SoapySDRUtil --probe="driver=lime"'.format(IMAGE_NAME),
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    output = res.stdout.decode()

    local_available = 'LimeSDR-Mini' in output
    local_fpga_ok = 'gatewareVersion=1.0' in output
    log.info('remote_available={}, local_available={}, local_fpga_ok={}'.format(remote_available, local_available, local_fpga_ok))
    return remote_available, local_available, local_fpga_ok


def main():
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('--server_only', help='Description for foo argument', action='store_true')
    parser.add_argument('--fpga_restore', help='Description for foo argument', action='store_true')
    args = vars(parser.parse_args())

    if platform.system() != 'Linux':
        log.error('Sorry, this currently only works on Linux. Data rates are low, so you could try Virtual Machine.')
        return

    if not docker_installed():
        log.error('Docker is not installed, cant continue. Fix: \n'
                  '$ curl -fsSL https://get.docker.com | sh \n'
                  '$ sudo groupadd docker \n'
                  '$ sudo usermod -aG docker $USER \n'
                  'Log out and log back in so that your group membership is re-evaluated.'
                  'Note: Only the server runs in "--privileged" mode.')
        return

    docker_pull()

    remote_available, local_available, local_fpga_ok = probe_devices()

    if args['server_only']:
        if not local_available:
            log.info('No local device found, cant start the server')
            return
        if not local_fpga_ok:
            docker_program_fpga()
        docker_start_server_daemon()
        log.info('Server is started!')
        return

    if args['fpga_restore']:
        if not local_available:
            log.info('No local device found, cant restore the FPGA.')
            return
        docker_restore_fpga()
        return

    # default behaviour (no args)
    if remote_available:
        docker_start_gqrx()
    elif local_available:
        if not local_fpga_ok:
            docker_program_fpga()

        docker_start_server_daemon()
        try:
            docker_start_gqrx()
        except:
            pass  # yolo

        log.info('Killing local server...')
        subprocess.run('docker kill spectrogram_server', shell=True)

    log.info('Done!')


if __name__ == '__main__':
    main()
