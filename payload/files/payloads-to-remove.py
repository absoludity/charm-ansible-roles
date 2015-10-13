#!/usr/bin/env python
import argparse
import operator
import os
import sys


parser = argparse.ArgumentParser(
    description='Remove old payloads from disk.')
parser.add_argument('payload_dir',
                    help='The directory containing payloads')
parser.add_argument('--archives-dir',
                    help='The directory where downloaded archives are '
                         'stored. Defaults to payload_dir/archives')
parser.add_argument('--older-backups', type=int, default=3,
                    help='Number of backup payloads to keep that are '
                         'older than the current payload.')
parser.add_argument('--verbose', '-v', action='count')


args = parser.parse_args()
if args.archives_dir is None:
    args.archives_dir = os.path.join(args.payload_dir, 'archives')


current_dir = os.readlink(os.path.join(args.payload_dir, 'latest'))


def verify_directories(args):
    for directory in (args.payload_dir, args.archives_dir, current_dir):
        if not os.path.exists(directory):
            sys.stderr.write("Error: directory '{}' does not exist.\n".format(
                directory))
            sys.exit(1)


def get_ordered_payload_labels(args):
    labels_with_timestamps = [
        (label, os.path.getmtime(os.path.join(args.archives_dir, label)))
        for label in os.listdir(args.archives_dir)
        if os.path.isdir(os.path.join(args.archives_dir, label))]
    labels_with_timestamps = sorted(labels_with_timestamps,
                                    key=operator.itemgetter(1),
                                    reverse=True)
    return [label_timestamp[0] for label_timestamp in labels_with_timestamps]

verify_directories(args)
labels = get_ordered_payload_labels(args)
current_label = os.path.basename(current_dir)

current_label_index = labels.index(current_label)
deletion_index = current_label_index + args.older_backups + 1
if deletion_index >= len(labels):
    if args.verbose > 0:
        sys.stdout.write("Nothing to do. Current payloads are: {}\n".format(
            labels))
    sys.exit(0)

payloads_to_keep = labels[:deletion_index]
if args.verbose > 0:
    sys.stdout.write("Keeping the following payloads: {}\n".format(
        payloads_to_keep))

payloads_to_delete = labels[deletion_index:]
directories_to_delete = []
for payload in payloads_to_delete:
    directories_to_delete.extend([
        os.path.join(args.archives_dir, payload),
        os.path.join(args.payload_dir, payload),
    ])

sys.stdout.write("\n".join(directories_to_delete))
