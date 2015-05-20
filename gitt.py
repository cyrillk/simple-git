#!/usr/bin/env python

import argparse
from tabulate import tabulate


class bcolours:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def xstr(s):
    return '' if s is None else str(s)


def paint(data, colour):
    return [colour + xstr(s) + bcolours.ENDC for s in data]


def build_row(inst):
    return [inst.id, inst.tags['Name'], inst.ip_address,
            inst.public_dns_name, inst.vpc_id, inst.state]


def build_headers():
    return ["ID", "NAME", "PUBLIC IP", "PUBLIC DNS", "VPC", "STATE"]


def get_instances(profile):
    reg = next(x for x in boto.ec2.regions() if x.name == 'eu-west-1')
    conn = boto.ec2.EC2Connection(profile_name=profile, region=reg)
    # conn = boto.ec2.EC2Connection(profile_name='heal')
    # conn = boto.ec2.connect_to_region('eu-west-1')
    # print conn
    return conn.get_all_instances()


def parse_args():
    parser = argparse.ArgumentParser(description='Simple AWS EC2 grep')
    parser.add_argument('-p', '--profile', nargs='?', help='aws profile')
    parser.add_argument('search', nargs='+', help='search string')
    return parser.parse_args()


def filter_instances(instances, search):
    data = []
    for res in instances:
        for inst in res.instances:
            count = len(data)
            for key, val in inst.tags.iteritems():  # loop tags
                for s in search:  # chech search strings
                    if s in val:
                        data.append(build_row(inst))
                        break  # break if found
                if count < len(data):
                    break  # break if found
    return data


def paint_data(row):
    if row[5] == 'stopped':
        return paint(row, bcolours.FAIL)
    elif row[5] == 'running' and row[4] is None:
        return paint(row, bcolours.OKBLUE)
    elif row[5] == 'running' and row[4] is not None:
        return paint(row, bcolours.OKGREEN)
    return row


def prepare_data():
    args = parse_args()
    data = filter_instances(get_instances(args.profile), args.search)
    sorted_data = sorted(data, key=lambda x: x[1])
    return [paint_data(s) for s in sorted_data]


def main():
    data = prepare_data()
    heads = paint(build_headers(), bcolours.HEADER)
    print tabulate(data, headers=heads, tablefmt="orgtbl")


if __name__ == "__main__":
    main()
