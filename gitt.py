#!/usr/bin/env python

import os
from tabulate import tabulate
from git import Repo
import argparse


class TerminalColours:
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
    return [colour + xstr(s) + TerminalColours.ENDC for s in data]


def git_fetch(origin, dir):
    try:
        origin.fetch()
    except Exception:
        print('Failed to fetch for ' + dir)


def git_pull(origin, dir):
    try:
        origin.pull()
    except Exception:
        print('Failed to pull for ' + dir)


def git_dirty(repo):
    return repo.is_dirty(untracked_files=True)


def git_branch(repo):
    return str(repo.active_branch)


def git_ahead(repo):
    if repo.remotes:
        branch = git_branch(repo)
        return len(list(repo.iter_commits(branch + '@{u}..' + branch)))


def git_behind(repo):
    if repo.remotes:
        branch = git_branch(repo)
        return len(list(repo.iter_commits(branch + '..' + branch + '@{u}')))


def process_dir(path, dir, is_fetch, is_pull):
    data = []
    if os.path.isdir(path + dir):
        git_path = path + dir + "/.git"
        if os.path.isdir(git_path):  # is git repo
            repo = Repo(git_path)

            if is_fetch and repo.remotes:
                git_fetch(repo.remotes.origin, dir)

            if is_pull and repo.remotes and not git_dirty(repo):
                git_pull(repo.remotes.origin, dir)

            try:
                branch = git_branch(repo)
                ahead = git_ahead(repo)
                behind = git_behind(repo)
                dirty = '-' if git_dirty(repo) else '+'

                state = ''
                if ahead and behind:
                    state = '+' + str(ahead) + ' / ' + '-' + str(behind)
                elif ahead and not behind:
                    state = '+' + str(ahead)
                elif not ahead and behind:
                    state = '-' + str(behind)

                data = [dir, branch, dirty, state]
            except Exception:
                print('Failed to process for ' + dir)
        else:
            data = [dir, '', '', '']
    print('.')
    return data


def paint_data(row):
    if row[2] == '+' and row[3]:
        return paint(row, TerminalColours.UNDERLINE + TerminalColours.OKBLUE)
    elif row[2] == '+' and not row[3]:
        return paint(row, TerminalColours.OKBLUE)
    elif row[2] == '-' and row[3]:
        return paint(row, TerminalColours.UNDERLINE + TerminalColours.FAIL)
    elif row[2] == '-' and not row[3]:
        return paint(row, TerminalColours.FAIL)
    elif not row[1]:
        return paint(row, TerminalColours.OKGREEN)
    return row


def build_headers():
    return ['NAME', 'BRANCH', 'CLEAN', 'STATE']


def parse_args():
    parser = argparse.ArgumentParser(description='Simple GIT table view')
    parser.add_argument('-f', '--fetch', action='store_true',
                        help='git fetch')
    parser.add_argument('-p', '--pull', action='store_true',
                        help='git pull')
    parser.add_argument('path', nargs='?', help='local path', default='./')
    return parser.parse_args()


def main():
    # command line arguments
    args = parse_args()
    path = args.path
    fetch = args.fetch
    pull = args.pull

    # directory processing
    data = [process_dir(path, d, fetch, pull) for d in os.listdir(path)]
    data = filter((lambda q: q != []), data)
    data = map(paint_data, data)

    # headers created
    heads = paint(build_headers(), TerminalColours.HEADER)

    # output result
    print tabulate(data, headers=heads, tablefmt="orgtbl")


if __name__ == "__main__":
    main()
