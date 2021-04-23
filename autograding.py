#!/usr/bin/env python

import json
import subprocess
import os
import sys
import signal
import shutil
import re
import pytz
from datetime import datetime
from timeit import default_timer as timer
from blessings import Terminal

term = Terminal(force_styling=True)

dir_path = os.path.dirname(os.path.realpath(__file__))


def read_json():
    with open('./tests/autograding.json') as f:
        return json.load(f)


def run(t, field='run'):
    proc = subprocess.Popen(t[field],
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True)
    try:
        timo = int(t['timeout'] * 60)
        inpt = None if t['input'] == "" else t['input']
        start = timer()
        output, errs = proc.communicate(input=inpt, timeout=timo)
        end = timer()
        print("🕒 Finished in {:.5f} seconds".format(end - start))
    except subprocess.TimeoutExpired:
        proc.kill()
        output = ""
        errs = "Timeout expired in " + str(timo) + " seconds"
    except UnicodeDecodeError:
        proc.kill()
        output = ""
        errs = "Output decoding error. Typically this is caused by incorrect initialization..."
    return output, errs


def check_output_correctness(output, expected, comparison, include=False):
    if comparison == 'exact':
        if include:
            return expected in output
        return output == expected
    if comparison == 'regex':
        return re.search(expected, output) != None


def partial_points(t, output):
    expected = ""
    pts = 0
    parts = t['partial']
    pts_per_part = float(t['points']) / len(parts)
    for p in parts:
        if check_output_correctness(output, p, t['comparison'], True):
            pts += pts_per_part
            expected += '\n'.join(term.black_on_green(x) for x in p.split('\n'))
        else:
            expected += '\n'.join(term.black_on_red(x) for x in p.split('\n'))
    # print("\nExpected:\n" + expected)
    return pts, expected


def run_test(t, idx):
    print()
    print("=" * shutil.get_terminal_size().columns)
    print("📝 " + t['name'])

    try:
        build_output = subprocess.check_output(t['setup'],
                                               shell=True,
                                               stderr=subprocess.STDOUT,
                                               universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(term.red("❌ Fail"))
        print()
        print(term.magenta("Compilation error..."))
        print(e.output)
        return 0.0

    output, errs = run(t, 'valgrind')

    expected = t['output']
    pts = 0.0

    if check_output_correctness(output, expected,
                                t['comparison']) and not errs:
        print(term.green("✅ Pass"))
        pts = float(t['points'])
    else:
        print(term.red("❌ Fail"))
        print()
        if 'case' in t:
            print(term.cyan("Input:"))
            print(t['case'])
        print()
        if errs:
            if check_output_correctness(output, expected, t['comparison']):
                pts = float(t['points'])
            elif 'partial' in t:
                pts, expected = partial_points(t, output)
            pts /= 2
            print(term.magenta("Error(s) during execution..."))
            print("\nOutput:\n" + output)
            print("\nExpected:\n" + expected)
            if t['comparison'] == 'regex':
                print(
                    '(Refer to https://docs.python.org/3/library/re.html for regex matching of output. TL;DR: "\s+" and "\s*" denote spaces and "\+" denotes "+".)'
                )
            print("\nError(s):")
            print(errs)
        else:
            print(term.magenta("Output not as expected..."))
            print("\nOutput:\n" + output)
            if 'partial' in t:
                pts, expected = partial_points(t, output)
            print("\nExpected:\n" + expected)
            if t['comparison'] == 'regex':
                print(
                    '(Refer to https://docs.python.org/3/library/re.html for regex matching of output. TL;DR: "\s+" and "\s*" denote spaces and "\+" denotes "+".)'
                )
            # expect_hex = ':'.join("{:02x}".format(ord(c)) for c in expected)
            # print("\t\t" + expect_hex)
    print()
    print(term.yellow("🎯 Points: {:.2f}".format(pts)))
    return pts


if __name__ == "__main__":
    current_datetime = datetime.now(pytz.timezone('US/Eastern'))
    github_sha = os.getenv("GITHUB_SHA")
    if github_sha:
        try:
            commit_date = subprocess.check_output(
                "git show -s --format=%cd --date=iso-strict {}".format(github_sha),
                shell=True,
                stderr=subprocess.STDOUT,
                universal_newlines=True)
            current_datetime = datetime.fromisoformat(commit_date.strip())
        except subprocess.CalledProcessError as e:
            print(term.blue("Get commit timestamp error: " + e.output))
            print(term.blue("Using the current date and time."))

    tests = read_json()
    total_pts = 0.0
    available_pts = 0.0
    idx = 0
    for t in tests['tests']:
        total_pts += run_test(t, idx)
        available_pts += t['points']
        idx += 1
    print()
    print("*" * shutil.get_terminal_size().columns)

    if 'bonus' in tests:
        for b in tests['bonus']:
            d = datetime.fromisoformat(b['date'])
            p = float(b['points'])
            #             print("commit time: " +str(current_datetime) + ", bonus time: " + str(d))
            if current_datetime < d:
                total_pts += p
                print(term.yellow("🎊 Bonus Points: " + str(p)))
                print()
                break

    points = "{:.2f}".format(total_pts) + "/" + "{:.2f}".format(available_pts)
    print(term.black_on_cyan("Total Points:\t" + points))

    with open('points', 'w') as f:
        f.write(points)

    if total_pts < available_pts:
        sys.exit(1)

    print("✨🌟💖💎🦄💎💖🌟✨🌟💖💎🦄💎💖🌟✨")
    sys.exit(0)
