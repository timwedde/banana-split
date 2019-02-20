#!/usr/bin/env python3

### System ###
import re
import sys
import time
import shutil
import argparse
from glob import glob
from tqdm import tqdm
from os import mkdir, remove, listdir
from os.path import join, dirname, exists
from signal import signal, SIGINT, SIG_IGN
from multiprocessing import cpu_count, Pool

### py-midicsv ###
import py_midicsv

### Local ###
from patterns import *
from scanner import scan


def check(args):
    if not exists(args.input_dir):
        print("Input directory does not exist!")
        sys.exit(1)
    if exists(args.output_dir):
        if listdir(args.output_dir):
            print("The output contains data. Do you want to overwrite it?")
            result = input("[y]es/[n]o: ").lower()
            if not result in ["y", "yes"]:
                print("Aborted")
                sys.exit(0)
        shutil.rmtree(args.output_dir)
    mkdir(args.output_dir)


def __midi_to_csv(file_in, file_out):
    with open(file_out, "w") as f:
        csv_string = py_midicsv.midi_to_csv(file_in)
        f.write("\n".join(csv_string))


def __csv_to_midi(file_in, file_out):
    with open(file_in, "r") as f:
        midi_object = py_midicsv.csv_to_midi(f.readlines())
    with open(file_out, "wb") as f:
        midi_writer = py_midicsv.FileWriter(f)
        midi_writer.write(midi_object)


def midi_to_csv(file):
    folder = join(args.output_dir, file["name"])
    csv_file = join(folder, "{}_full.csv".format(file["name"]))
    mkdir(folder)
    try:
        __midi_to_csv(file["path"], csv_file)
    except:
        shutil.rmtree(folder)
        if args.verbose:
            return "Could not convert '{}'".format(file["name"])


def csv_to_midi(file):
    midi_file = join(dirname(file["path"]), "{}.mid".format(file["name"]))
    try:
        __csv_to_midi(file["path"], midi_file)
    except:
        if args.verbose:
            return "An error occurred while converting '{}' in folder {}".format(file["name"], dirname(file["path"]))


def list_channels(file):
    channels = set()
    with open(file["path"], "r", encoding="latin-1") as f:
        for line in f:
            m = channel_pattern.match(line)
            if m:
                channels.add(m.group(1))
    return channels


def split_channel(file, data, channel):
    file_out = join(dirname(file["path"]), "channel_{}.csv".format(channel))
    with open(file_out, "w") as f:
        for line in data:
            if comment_pattern.match(line):
                continue
            m = channel_pattern.match(line)
            if m:
                if m.group(1) == channel:
                    f.write(line)
            else:
                if not lyric_pattern.match(line):  # skip lyrics
                    f.write(line)


def split_channels(file, channels):
    file_in = file["path"]
    data = open(file_in, "r", encoding="latin-1").readlines()
    for channel in channels:
        split_channel(file, data, channel)


def extract_channels(file):
    channels = list_channels(file)
    split_channels(file, channels)


def transpose(file):
    data = []
    with open(file["path"], "r", encoding="latin-1") as f:
        for line in f:
            m = note_pattern.match(line)
            if m:
                if m.group(2) != drum_channel:
                    note = int(m.group(5)) + args.offset
                    if note < 0:
                        note = 0
                    data.append(re.sub(note_pattern, "\\1, \\2, \\3, \\4, {}, \\6".format(note), line))
                else:
                    data.append(line)
            else:
                data.append(line)
    with open(file["path"], "w", encoding="latin-1") as f:
        for line in data:
            f.write(line)


def check_channel(file):
    file_in = file["path"]
    data = open(file_in, "r", encoding="latin-1").readlines()
    for line in data:
        if note_pattern.match(line):
            return
    remove(file_in)


def list_tracks(file):
    tracks = set()
    with open(file["path"], "r", encoding="latin-1") as f:
        for line in f:
            m = track_pattern.match(line)
            if m:
                tracks.add(m.group(1))
    return tracks


def split_track(file, data, track):
    folder = join(dirname(file["path"]), file["name"])
    file_out = join(folder, "track_{}.csv".format(track))
    if not exists(folder):
        mkdir(folder)
    with open(file_out, "w") as f:
        for line in data:
            if comment_pattern.match(line):  # skip comments
                continue
            m = track_pattern.match(line)
            if m:
                if m.group(1) == track:
                    f.write(line)
            else:
                if not lyric_pattern.match(line):  # skip lyrics
                    f.write(line)


def split_tracks(file, tracks):
    file_in = file["path"]
    channel_target = join(dirname(file["path"]), file["name"], "{}.csv".format(file["name"]))
    data = open(file_in, "r", encoding="latin-1").readlines()
    for track in tracks:
        split_track(file, data, track)
    shutil.move(file["path"], channel_target)


def extract_tracks(file):
    tracks = list_tracks(file)
    split_tracks(file, tracks)


def clean(file):
    data = open(file["path"], "r", encoding="latin-1").readlines()
    with open(file["path"], "w") as f:
        for line in data:
            if comment_pattern.match(line) or unknown_event_pattern.match(line) or sequencer_specific_pattern.match(line):
                continue
            f.write(line)

# TODO: load the file to be processed into RAM once, instead of reading it from disk multiple times to improve performance
# Remove dependency of development version of python-midi (python3 branch)
# (pip install  https://github.com/vishnubob/python-midi/archive/feature/python3.zip)


def main(args):
    with tqdm(total=(6 if args.keep else 7), unit="step") as bar:
        tqdm.write("Converting input data...")
        files = scan(args.input_dir, "*.mid")
        for e in tqdm(worker_pool.imap_unordered(midi_to_csv, files), total=len(files), unit="files"):
            if e:
                tqdm.write(e)
        bar.update(1)

        tqdm.write("Cleaning input data...")
        files = scan(args.output_dir, "**/*_full.csv")
        for e in tqdm(worker_pool.imap_unordered(clean, files), total=len(files), unit="files"):
            if e:
                tqdm.write(e)
        bar.update(1)

        tqdm.write("Splitting channels...")
        files = scan(args.output_dir, "**/*_full.csv")
        for e in tqdm(worker_pool.imap_unordered(extract_channels, files), total=len(files), unit="files"):
            if e:
                tqdm.write(e)
        bar.update(1)

        tqdm.write("Removing empty channels...")
        files = scan(args.output_dir, "**/channel_*.csv", True)
        for e in tqdm(worker_pool.imap_unordered(check_channel, files), total=len(files), unit="files"):
            if e:
                tqdm.write(e)
        bar.update(1)

        tqdm.write("Splitting tracks...")
        files = scan(args.output_dir, "**/channel_*.csv", True)
        for e in tqdm(worker_pool.imap_unordered(extract_tracks, files), total=len(files), unit="files"):
            if e:
                tqdm.write(e)
        bar.update(1)

        tqdm.write("Converting output data...")
        files = scan(args.output_dir, "**/channel_*.csv", True)
        files += scan(args.output_dir, "**/track_*.csv", True)
        for e in tqdm(worker_pool.imap_unordered(csv_to_midi, files), total=len(files), unit="files"):
            if e:
                tqdm.write(e)
        bar.update(1)

        if not args.keep:
            tqdm.write("Removing intermediary artifacts...")
            files = scan(args.output_dir, "**/*.csv", True)
            files = [f["path"] for f in files]
            for e in tqdm(worker_pool.imap_unordered(remove, files), total=len(files), unit="files"):
                if e:
                    tqdm.write(e)
            bar.update(1)

        tqdm.write("Finished processing")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split MIDI files into channels and tracks.")
    parser.add_argument("-i", "--input", type=str, dest="input_dir", required=True,
                        metavar="dir", help="(required) The folder containing the input data")
    parser.add_argument("-o", "--output", type=str, dest="output_dir", required=True,
                        metavar="dir", help="(required) The folder containing the output data")
    parser.add_argument("-t", "--threads", type=int, dest="num_threads", default=cpu_count(),
                        metavar="N", help="The amount of threads to use (default: {})".format(cpu_count()))
    parser.add_argument("-k", "--keep", dest="keep", action="store_true",
                        help="When given, will keep the intermediary product of each file (.csv)")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                        help="When given, will produce more verbose output for debugging purposes")
    args = parser.parse_args()

    original_sigint_handler = signal(SIGINT, SIG_IGN)
    worker_pool = Pool(args.num_threads)
    signal(SIGINT, original_sigint_handler)

    check(args)

    try:
        main(args)
    except KeyboardInterrupt:
        print("Received SIGINT, terminating...")
        worker_pool.terminate()
    else:
        worker_pool.close()

    worker_pool.join()
