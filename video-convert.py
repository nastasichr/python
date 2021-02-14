import argparse
import re
import os.path
import subprocess, shlex

def yes_or_no(question):
    while True:
        reply = str(input(question+' (y/n): ')).lower().strip()
        if not reply: continue
        if reply[0] == 'y': return True
        if reply[0] == 'n': return False

def run_ffmpeg(ifname, ofname, duration=None):
    ifname = shlex.quote(ifname)
    ofname = shlex.quote(ofname)
    duration = "-t {}".format(duration * 60) if duration else ""
    vcodec = "-vcodec libx264 -pix_fmt yuv420p -profile:v main"
    cmd = "ffmpeg -i {} {} {} {} {}".format(ifname, duration, vcodec, duration, ofname)
    subprocess.run(shlex.split(cmd))

def make_out_fname(ifname):
    suffix = "_ENC"
    m = re.search("(.*)(\.[^\.]*)$", ifname)
    if not m:
        return ifname + suffix
    else:
        return m.group(1) + suffix + m.group(2)

def convert(files, duration):
    if duration and duration < 0:
        print("Invalid negative duration. Nothing to do.")
        return
    for ifname in files:
        run_ffmpeg(ifname, make_out_fname(ifname), duration)

def discover_all(files, ask_prompt):
    ret = []
    for ifname in files:
        if not os.path.isfile(ifname):
            print("Input file '{}' does not exist. Skipping.".format(ifname))
            continue
        if not ask_prompt:
            ret.append(ifname)
        elif yes_or_no("Convert '{}'?".format(ifname)):
            ret.append(ifname)
    return ret

def main():
    parser = argparse.ArgumentParser(description='Re-encodes video using ffmpeg')
    parser.add_argument('files', metavar='file', type=str, nargs='+',
                        help='Files to encode')
    parser.add_argument('-p', dest='prompt', action='store_true',
                        help='prompt on each file to confirm')
    parser.add_argument('-t', metavar='duration', dest='duration', type=int,
                        help='Test conversion: encode the first <duration> minutes only')
    
    args = parser.parse_args()

    files = discover_all(args.files, args.prompt)

    if files:
        print("Going to covert these files:")
        for f in files: print(f)

    if not files or not yes_or_no("happy to proceed?"):
        print("Nothing to do")
        return


    convert(files, args.duration)

if __name__ == "__main__":
    main()
