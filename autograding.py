#!/usr/bin/env python

import json
import subprocess
import os
import sys
import signal
import shutil
from colorama import Fore, Back

dir_path = os.path.dirname(os.path.realpath(__file__))

def read_json():
    with open('./tests/autograding.json') as f:
        return json.load(f)


def run_test(t, idx):
    print()
    print("=" * shutil.get_terminal_size().columns)
    print("📝 " + t['name'])
    subprocess.call(t['setup'], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    proc = subprocess.Popen(t['run'],
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True)
    try:
        to = int(t['timeout']) * 60
        output, errs = proc.communicate(timeout=to)
    except subprocess.CalledProcessError as e:
        output = e.output
    except subprocess.TimeoutExpired:
        proc.kill()
        output = "Timeout expired in " + to + " seconds"
    except UnicodeDecodeError:
        output = "Output decode error"

    expected = t['output']
    pts = 0.0
    if output == expected:
        print(Fore.GREEN + "✅ Pass" + Fore.RESET)
        pts = float(t['points'])
    else:
        print(Fore.RED + "❌ Fail" + Fore.RESET)
        print()
        print("Output:\t\t\"" + output + "\"")
#         output_hex = ':'.join("{:02x}".format(ord(c)) for c in output)
#         print("\t\t" + output_hex)

        print("Expected:\t\"" + expected + "\"")
#         expect_hex = ':'.join("{:02x}".format(ord(c)) for c in expected)
#         print("\t\t" + expect_hex)

    return pts


if __name__ == "__main__":
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
    print(Back.CYAN + Fore.BLACK + "Points:\t" + "{:.1f}".format(total_pts) + "/" + "{:.1f}".format(available_pts) + Fore.RESET + Back.RESET)
    
    if total_pts < available_pts:
        sys.exit(1)
    print("✨🌟💖💎🦄💎💖🌟✨🌟💖💎🦄💎💖🌟✨")
    sys.exit(0)
