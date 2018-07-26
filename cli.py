import logging
import subprocess

import click

from main import init

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('cli')


@click.group()
def cli():
    pass


@click.command(help='Programs 8K FFT into the FPGA. You need to run "restore_fpga" to restore default image')
def program_fpga():
    log.info('Programming FPGA, takes ~20 sec...')
    subprocess.run(
        ["LimeUtil", "--fpga=./LimeSDR-Mini_GW/LimeSDR-Mini_bitstreams/LimeSDR-Mini_lms7_trx_HW_1.2_auto.rpd"])
    log.info('Please unplug and replug the LimeSDR-Mini...')


@click.command(help='Programs default FPGA image')
def restore_fpga():
    log.info('Restoring default LimeSuite FPGA image, takes ~20 sec...')
    subprocess.run(["LimeUtil", "--update"])


@click.command(help='Runs the realtime spectrogram GUI')
def run():
    init()


cli.add_command(program_fpga)
cli.add_command(restore_fpga)
cli.add_command(run)

if __name__ == '__main__':
    cli()
