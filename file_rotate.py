#!/usr/bin/env python3

"""
MIT License

Copyright (c) 2017 Stephen-Michael Brooks

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

""" Rotates files based on size of file or age of file """

import os
import sys
import argparse
import datetime


def rotate_by_time(time, directory):
    """ Appends all the filenames of files in arg:directory that are older than arg:time with
        today's date. """

    if time == 'day':
        diff = datetime.timedelta(days=1)
    elif time == 'week':
        diff = datetime.timedelta(weeks=1)
    elif time == 'month':
        diff = datetime.timedelta(weeks=4)
    elif time == '6months':
        diff = datetime.timedelta(weeks=26)
    else:
        diff = datetime.timedelta(weeks=52)

    dir_contents = os.scandir(directory)
    for item in dir_contents:
        file_stats = item.stat()
        creation_time = datetime.datetime.fromtimestamp(file_stats.st_ctime)
        if diff + creation_time < datetime.datetime.now():
            new_base_path = os.path.join(os.path.split(item.path)[0], 'bak', item.name)
            cur_date = datetime.datetime.now().strftime('%m-%d-%Y')
            os.rename(item.path, '.'.join([new_base_path, cur_date]))


def rotate_by_size(size, directory):
    """ Appends all the filenames of files in arg:directory that are larger than arg:size with
        today's date. """

    dir_contents = os.scandir(directory)
    for item in dir_contents:
        file_stats = item.stat()
        if item.is_file and file_stats.st_size > size:
            cur_date = datetime.datetime.now().strftime('%m-%d-%Y')
            new_base_path = os.path.join(os.path.split(item.path)[0], 'bak', item.name)
            os.rename(item.path, os.path.join(item.path, '.'.join([new_base_path, cur_date])))


def main(arguments):
    """ Parses CLI argv and determines intent of the user. """

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-d', '--directory',
                        metavar='',
                        required=True,
                        help='Specifies the directory that will be scanned for rotaions.'
                       )
    parser.add_argument('-s', '--size',
                        metavar='',
                        type=int,
                        help='Rotate by size and specify the size in bytes'
                       )
    parser.add_argument('-t', '--time',
                        metavar='',
                        type=str,
                        help='Rotate by time and specify the time.\n\
                              Usage: day, week, month, 6months, year'
                       )

    args = parser.parse_args(arguments)

    if args.size is None and args.time is None:
        print('ERROR: You must specify a rotation option.\
              Use --help to learn which options are available')
    elif args.size is not None and args.time is None:
        if args.size < 1e6:
            print('ERROR: Minimum size for rotation is 1 MB.')
        else:
            rotate_by_size(args.size, args.directory)
    elif args.time is not None and args.size is None:
        accept_args = ['day', 'week', 'month', '6months', 'year']
        if not any(args.time.lower() in arg for arg in accept_args):
            print('ERROR: The only acceptable arguments for --time are:\
                  day, week, month, 6months, year')
        else:
            rotate_by_time(args.time.lower(), args.directory)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
