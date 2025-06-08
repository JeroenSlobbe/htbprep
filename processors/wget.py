import os
import re
import requests
from termcolor import colored

def process_wget_results(
    input_file="attacksurface/rawOutput/wget.txt",
    output_folder="attacksurface/processedOutputs/wget"
):
    os.makedirs(output_folder, exist_ok=True)

    # Define output files
    urls_200_file = os.path.join(output_folder, "urls.txt")
    urls_403_file = os.path.join(output_folder, "forbidden.txt")
    urls_other_file = os.path.join(output_folder, "urls_others.txt")
    directories_file = os.path.join(output_folder, "directories.txt")

    # Data containers
    seen_urls = set()
    seen_dirs = set()
    urls_200, urls_403, urls_other, dirs_403 = [], [], [], []

    # Extract URLs from wget spider output
    url_pattern = re.compile(r"--\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}--\s+(http[s]?://[^\s]+)")

    with open(input_file, "r") as f:
        for line in f:
            match = url_pattern.match(line.strip())
            if match:
                url = match.group(1)
                if url not in seen_urls:
                    seen_urls.add(url)
                    try:
                        response = requests.get(url, timeout=5)
                        code = response.status_code
                        if code == 200:
                            urls_200.append((url, "200"))
                        elif code == 403:
                            urls_403.append((url, "403"))
                        else:
                            urls_other.append((url, str(code)))
                    except requests.RequestException:
                        urls_other.append((url, "error"))

                    # Track directory
                    directory = "/".join(url.split("/")[:-1]) + "/"
                    if directory not in seen_dirs:
                        seen_dirs.add(directory)
                        try:
                            r = requests.get(directory, timeout=5)
                            if r.status_code == 403:
                                dirs_403.append((directory, "403 (DIR)"))
                        except:
                            pass

    # Write output files
    def dump(path, items):
        with open(path, "w") as f:
            for url, _ in sorted(items):
                f.write(url + "\n")

    dump(urls_200_file, urls_200)
    dump(urls_403_file, urls_403)
    dump(urls_other_file, urls_other)
    dump(directories_file, dirs_403)

    # Print summary
    print(f"{colored(str(len(urls_200)), 'green')} 200 OK URLs")
    print(f"{colored(str(len(urls_403)), 'red')} 403 Forbidden URLs")
    print(f"{colored(str(len(urls_other)), 'blue')} Other responses")
    print(f"{colored(str(len(dirs_403)), 'white')} 403 DIRs identified")

    # Print color-coded table
    print("\n### Wget Summary Table ###")
    print(f"{'URL or Directory':<60} {'Status':<10}")
    print("=" * 70)
    for group, color in [
        (urls_200, "green"),
        (urls_403, "red"),
        (urls_other, "blue"),
        (dirs_403, "white")
    ]:
        for url, code in sorted(group):
            print(colored(f"{url:<60} {code:<10}", color))
    print("=" * 70)
