#!/home/maksym/git/ec2-manager/venv/bin/python3.9
import argparse
import sys
import time

import boto3
from boto3_type_annotations.ec2.service_resource import Instance

from config import MAIN_DOMAIN_NAME, MAIN_DOMAIN_ID, MINECRAFT_SERVER_INSTANCE_ID
from src.freenom_interface import FreenomInterface

ec2 = boto3.resource('ec2')


def start_ec2_instance(instance: Instance):
    instance.start()
    print('starting the instance...')
    while instance.state['Name'] != 'running':
        print('the instance still hasn\'t started, current state:', instance.state['Name'])
        time.sleep(4)
        instance.load()
    print('instance is started!')


def stop_ec2_instance(instance: Instance):
    instance.stop()
    print('stopping the instance...')
    while instance.state['Name'] == 'stopping':
        print('the instance is still not stopped, current state:', instance.state['Name'])
        time.sleep(4)
        instance.load()
    print('instance is stopped!')


def minecraft_session():
    ms_instance = ec2.Instance(MINECRAFT_SERVER_INSTANCE_ID)
    try:
        start_ec2_instance(instance=ms_instance)
        print('public_ip_address', ms_instance.public_ip_address)
        print('trying assign', ms_instance.public_ip_address, 'to', MAIN_DOMAIN_NAME)
        freenom_interface = FreenomInterface()
        freenom_interface.change_dns_targer(MAIN_DOMAIN_NAME, MAIN_DOMAIN_ID, ms_instance.public_ip_address)
        print('start done. write "exit" or "stop" to exit.')
        input_string = ''
        while not (input_string.strip() == 'exit' or input_string.strip() == 'stop'):
            input_string = input()
    finally:
        stop_ec2_instance(ms_instance)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--type', help='Type of executed instance', required=True)
    args = parser.parse_args()
    if args.type == 'minecraft':
        minecraft_session()
    else:
        print('please, specify type of instance (--type)')
        sys.exit(1)

