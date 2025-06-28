import os
import re
import requests
from termcolor import colored

def process_gobuster_results(
    input_file="attacksurface/rawOutput/gobuster.txt",
    output_folder="attacksurface/processedOutputs/gobuster"
):
    os.makedirs(output_folder, exist_ok=True)

    # Define output file paths
    all_subdomains_file = os.path.join(output_folder, "subdomains_all.txt")
    online_subdomains_file = os.path.join(output_folder, "subdomains_online.txt")

    # Regex pattern to extract subdomains
    subdomain_pattern = re.compile(r"Found: (\S+)")

    # Initialize lists
    subdomains_list = []
    online_subdomains_list = []

    # Read and clean subdomains from input file
    with open(input_file, "r") as f:
        for line in f:
            line = line.strip()
            if (subdomain_match := subdomain_pattern.match(line)):
                subdomains_list.append(subdomain_match.group(1))

    # Write all subdomains to file
    with open(all_subdomains_file, "w") as f:
        for subdomain in subdomains_list:
            f.write(f"{subdomain}\n")

    # Check if subdomains are online
    print("\n### Checking Subdomain Availability ###")
    for subdomain in subdomains_list:
        try:
            response = requests.get(subdomain, timeout=5)
            if response.status_code < 400:
                online_subdomains_list.append(subdomain)
                print(colored(f"{subdomain} is UP", "green"))
            else:
                print(colored(f"{subdomain} returned {response.status_code}", "red"))
        except requests.exceptions.RequestException:
            print(colored(f"{subdomain} is DOWN", "red"))

    # Write online subdomains to file
    with open(online_subdomains_file, "w") as f:
        for subdomain in online_subdomains_list:
            f.write(f"{subdomain}\n")

    print("\nProcessing complete!")
    print(f"{colored(str(len(subdomains_list)), 'blue')} subdomains found")
    print(f"{colored(str(len(online_subdomains_list)), 'green')} online subdomains detected")

# Example usage
process_gobuster_results()
