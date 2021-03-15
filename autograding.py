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
from colorama import Fore, Back, Style

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
        timo = int(t['timeout']) * 60
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


def partial_points(t, output):
    pts = 0
    parts = t['partial']
    pts_per_part = float(t['points']) / len(parts)
    for p in parts:
        if p in output:
            pts += pts_per_part
    return pts


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
        print(Fore.RED + "❌ Fail" + Fore.RESET)
        print()
        print(Fore.MAGENTA + "Compilation error..." + Fore.RESET)
        print(e.output)
        return 0.0

    output, errs = run(t, 'valgrind')

    expected = t['output']
    pts = 0.0
    if output == expected and not errs:
        print(Fore.GREEN + "✅ Pass" + Fore.RESET)
        pts = float(t['points'])
    else:
        print(Fore.RED + "❌ Fail" + Fore.RESET)
        print()
        if 'case' in t:
            print(Fore.CYAN + "Input:" + Fore.RESET)
            print(t['case'])
        print()
        if errs:
            if output == expected:
                pts = float(t['points'])
            elif 'partial' in t:
                pts = partial_points(t, output)
            pts /= 2
            print(Fore.MAGENTA + "Error(s) during execution..." + Fore.RESET)
            print("Output:   '" + output + "'")
            print("Expected: '" + expected + "'")
            print("Error(s):")
            print(errs)
        else:
            if 'partial' in t:
                pts = partial_points(t, output)
            print(Fore.MAGENTA + "Output not as expected..." + Fore.RESET)
            print("Output:   '" + output + "'")
            print("Expected: '" + expected + "'")
            # expect_hex = ':'.join("{:02x}".format(ord(c)) for c in expected)
            # print("\t\t" + expect_hex)
    print()
    print("🎯 " + Fore.YELLOW + "Points: " + "{:.2f}".format(pts) + Fore.RESET)
    return pts


if __name__ == "__main__":
    tests = read_json()
    total_pts = 0.0
    available_pts = 0.0
    
    if 'bonus' in tests:
        for b in tests['bonus']:
            d = datetime.fromisoformat(b['date'])
            p = float(b['points'])
            print("bonus time: " + str(d) + ": " + str(p))
            nyc_datetime = datetime.now(pytz.timezone('US/Eastern'))
            print("current time: " + str(nyc_datetime))
    
    idx = 0
    for t in tests['tests']:
        total_pts += run_test(t, idx)
        available_pts += t['points']
        idx += 1
    print()
    print("*" * shutil.get_terminal_size().columns)
            
    points = "{:.2f}".format(total_pts) + "/" + "{:.2f}".format(available_pts)
    print(Back.CYAN + Fore.BLACK + "Total Points:\t" + points + Fore.RESET +
          Back.RESET)
            
    with open('points', 'w') as f:
        f.write(points)

    if total_pts < available_pts:
        sys.exit(1)

    print("✨🌟💖💎🦄💎💖🌟✨🌟💖💎🦄💎💖🌟✨")
    sys.exit(0)
