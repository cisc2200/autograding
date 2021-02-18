#!/usr/bin/env python

import json
import subprocess
import os
import sys
import signal
import shutil
from timeit import default_timer as timer
from colorama import Fore, Back

dir_path = os.path.dirname(os.path.realpath(__file__))


def read_json():
    with open('./tests/autograding.json') as f:
        return json.load(f)


def run(t, field='run'):
    proc = subprocess.Popen(t[field],
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True)
    try:
        timo = int(t['timeout']) * 60
        inpt = None if t['input'] == "" else t['input']
        start = timer()
        output, errs = proc.communicate(input=inpt, timeout=timo)
        end = timer()
        print("🕒 Finished in {:.5f} seconds".format(end - start))
    except subprocess.CalledProcessError as e:
        output = e.output
    except subprocess.TimeoutExpired:
        proc.kill()
        output = "Timeout expired in " + timo + " seconds"
    except UnicodeDecodeError:
        output = "Output decoding error"
    return output


def run_test(t, idx):
    print()
    print("=" * shutil.get_terminal_size().columns)
    print("📝 " + t['name'])

    try:
#         build_output = subprocess.check_output(t['setup'], shell=True)
        build_output = subprocess.check_output(t['setup'], shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(Fore.RED + "❌ Fail" + Fore.RESET)
        print()
        print(Fore.MAGENTA + "Compilation error..." + Fore.RESET)
        print(Fore.MAGENTA + "Please look at the error messages below for more details..." + Fore.RESET)
        print(e.output)
        return 0.0
#         pass
#     if not os.path.exists('./test.out'):
    
    output = run(t, 'valgrind')

    expected = t['output']
    pts = 0.0
    if output == expected:
        print(Fore.GREEN + "✅ Pass" + Fore.RESET)
        pts = float(t['points'])
    else:
        print(Fore.RED + "❌ Fail" + Fore.RESET)
        print()
        if output.startswith(expected) and output[len(expected)] == '=':
            print(Fore.MAGENTA +
                  "Output is as expected, but there are memory leaks..." +
                  Fore.RESET)
            print(output[len(expected):])
        else:
            print(Fore.MAGENTA + "Output not as expected..." + Fore.RESET)
            try:
                print("Output:   \"" + output[:output.index('==')] + "\"")
            except:
                print("Output:   \"" + output + "\"")
            print("Expected: \"" + expected + "\"")
            # expect_hex = ':'.join("{:02x}".format(ord(c)) for c in expected)
            # print("\t\t" + expect_hex)
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
    points = "{:.2f}".format(total_pts) + "/" + "{:.2f}".format(available_pts)
    print(Back.CYAN + Fore.BLACK + "Points:\t" + points + Fore.RESET +
          Back.RESET)

    with open('points', 'w') as f:
        f.write(points)

    if total_pts < available_pts:
        sys.exit(1)

    print("✨🌟💖💎🦄💎💖🌟✨🌟💖💎🦄💎💖🌟✨")
    sys.exit(0)
