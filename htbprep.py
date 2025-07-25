import subprocess
import sys
import os
import shutil
import importlib.util
import argparse

# Command index map
command_map = {
    1: ("wafwoof", "wafw00f {url} >> {out}/wafwoof.txt"),
    2: ("curl", "curl -I {url} -o {out}/curlHeaders.txt"),
    3: ("whatweb", "whatweb -a 3 {url} >> {out}/whatweb.txt"),
    4: ("nmap", "nmap -sV {url} -oN {out}/nmap.txt"),
    5: ("gobuster", "gobuster dns -d {url} -w /usr/share/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt -o {out}/gobuster.txt"),
    6: ("ffuzz", "ffuf -u {prefix}{url} -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -H "Host:FUZZ.{url}" -mc 200",
    6: ("dirb", "dirb {prefix}{url} /usr/share/dirb/wordlists/common.txt -o {out}/dirb.txt"),
    7: ("wget", "wget --spider --recursive --level=5 -nd {url} -o {out}/wget.txt"),
    8: ("fallparams", "fallparams -u {prefix}{url} -c -o {out}/fallparam.txt"),
    9: ("subfinder", "subfinder -d {url} -all -recursive >> {out}/subfinder.txt"),
    10: ("nuclei", " nuclei -u {url} >> {out}/nuclie.txt")
}

# Argument parser
parser = argparse.ArgumentParser(description="ToolHarmonize: Modular Recon Scanner")
parser.add_argument("target_url", nargs="?", help="Target URL or domain (required)")
parser.add_argument("--prefix", default="http://", help="Optional prefix like http:// or https:// (used by specific tools)")
parser.add_argument("--only", nargs="+", type=int, help="Run only these command numbers (see --help-screen)")
parser.add_argument("--exclude", nargs="+", type=int, help="Exclude these command numbers (see --help-screen)")
parser.add_argument("--processors-only", action="store_true", help="Run processors without executing scans")
parser.add_argument("--skip-processors", action="store_true", help="Skip all processors (only scan)")
parser.add_argument("--help-screen", action="store_true", help="Show command options and exit")
args = parser.parse_args()

if args.help_screen or not args.target_url:
    print("\n🛠 Available Commands:")
    for index, (name, _) in command_map.items():
        print(f"{index}. {name}")
    print("\nExamples:")
    print("  python scanner.py target.htb --exclude 4 5")
    print("  python scanner.py target.htb --only 1 6")
    print("  python scanner.py target.htb --prefix=https://")
    print("  python scanner.py target.htb --processors-only")
    print("  python scanner.py target.htb --skip-processors")
    sys.exit(0)

target = args.target_url
prefix = args.prefix
base = "attacksurface"
raw = os.path.join(base, "rawOutput")

if not args.processors_only:
    # Prepare folders
    for path in [base, raw]:
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)

    # Command selection
    selected = set(command_map.keys())
    if args.only:
        selected = set(args.only)
    elif args.exclude:
        selected -= set(args.exclude)

    # Run each command
    for index in sorted(selected):
        name, cmd_template = command_map[index]
        command = cmd_template.format(url=target, prefix=prefix, out=raw)
        print(f"[+] Running {name}...")
        try:
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                print(line.strip())
            proc.wait()
            if proc.returncode == 0:
                print(f"[+] {name} completed successfully!\n")
            else:
                print(f"[-] {name} exited with code {proc.returncode}\n")
        except Exception as e:
            print(f"[-] Error running {name}: {e}\n")

# Run processors unless explicitly skipped
if not args.skip_processors:
    print("[+] Executing processors...\n")
    processors_dir = "processors"
    if os.path.exists(processors_dir):
        for filename in os.listdir(processors_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_path = os.path.join(processors_dir, filename)
                module_name = filename[:-3]
                try:
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for attr in dir(module):
                        if attr.startswith("process_") and callable(getattr(module, attr)):
                            print(f"[+] Running {module_name}.{attr}()")
                            getattr(module, attr)()

                except Exception as e:
                    print(f"[-] Failed in {module_name}: {e}")
    else:
        print("[-] No 'processors/' folder found.")
else:
    print("[*] Skipping processors as requested.")
