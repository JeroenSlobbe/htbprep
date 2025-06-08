import os
import re
from termcolor import colored

def process_dirb_results(
    input_file="attacksurface/rawOutput/dirb.txt",
    output_folder="attacksurface/processedOutputs/dirb"
):
    os.makedirs(output_folder, exist_ok=True)

    # Define output file paths
    urls_200 = os.path.join(output_folder, "urls.txt")
    urls_302 = os.path.join(output_folder, "urls_forbidden.txt")
    urls_other = os.path.join(output_folder, "urls_others.txt")
    directories = os.path.join(output_folder, "directories.txt")

    # Initialize lists
    urls_200_list = []
    urls_302_list = []
    urls_other_list = []
    directories_list = []

    # Regex patterns
    url_pattern = re.compile(r"\+ (http[s]?://\S+) \(CODE:(\d+)")
    dir_pattern = re.compile(r"==> DIRECTORY: (http[s]?://\S+)")

    # Read and categorize the URLs
    with open(input_file, "r") as f:
        for line in f:
            line = line.strip()
            if (dir_match := dir_pattern.match(line)):
                directories_list.append((dir_match.group(1), "DIR"))
            elif (url_match := url_pattern.match(line)):
                url, code = url_match.groups()
                if code == "200":
                    urls_200_list.append((url, code))
                elif code == "302":
                    urls_302_list.append((url, code))
                else:
                    urls_other_list.append((url, code))

    # Write to file (URL only)
    def write_to_file(filepath, data):
        with open(filepath, "w") as f:
            for item in data:
                f.write(f"{item[0]}\n")

    write_to_file(urls_200, urls_200_list)
    write_to_file(urls_302, urls_302_list)
    write_to_file(urls_other, urls_other_list)
    write_to_file(directories, directories_list)

    # Summary
    print(f"{colored(str(len(urls_200_list)), 'green')} URLs found")
    print(f"{colored(str(len(directories_list)), 'white')} directories found")

    # Table output
    print("\n### Summary Table ###")
    print(f"{'URL':<60} {'Code':<10}")
    print("=" * 70)
    for category, color in [
        (urls_200_list, "green"),
        (urls_302_list, "red"),
        (urls_other_list, "blue"),
        (directories_list, "white")
    ]:
        for url, code in category:
            print(colored(f"{url:<60} {code:<10}", color))
    print("=" * 70)
