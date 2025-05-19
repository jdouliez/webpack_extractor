import sys
import os
import json
import requests
import re
from colorama import Fore, Style
import argparse

requests.packages.urllib3.disable_warnings()

def usage():
    print(Fore.RED + "[!] Please provide at least a parameter -u/--url or -f/--file.\n\t* Either the url of a sourcemap file (https://site.com/source.js.map)\n\t* Either a local file." + Style.RESET_ALL)
    sys.exit(1) 

parser = argparse.ArgumentParser(description="Extracting source files from a webpack")
parser.add_argument("-s", "--silent", help="Decrease output verbosity", action="store_true")  #True/False
parser.add_argument("-H", "--headers", help="Additional HTTP headers (separated with ',')")

group = parser.add_mutually_exclusive_group()
group.add_argument("-u", "--url", dest="url", help="Url to get the mapping from")
group.add_argument("-f", "--file", dest="file", help="Local file to get the mapping from")

args = parser.parse_args()


if not (args.url or args.file):
    usage()


def get_json_data(headers=None):

    local_headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'}

    if headers:
        for header in headers.split(","):
            if ":" in header:
                key, value = header.split(":", 1)
                local_headers[key.strip()] = value.strip()
    

    if args.file and os.path.exists(args.file):
        print(f"{Fore.YELLOW}[>] Using local file \"{args.file}\"")
        with open(args.file, 'r') as file:
            json_data = json.load(file)
        return json_data

    elif args.url and is_valid_url(args.url):
        print(f"{Fore.YELLOW}[>] Using url \"{args.url}\"{Style.RESET_ALL}")        

        try:
            response = requests.get(args.url, verify=False, timeout=15, headers=local_headers)
            return response.json()
        except:
            print(f"{Fore.RED}[-] The url does not provid valid json data.{Style.RESET_ALL}")
            return None
    
    else:
        print(f"{Fore.RED}[-] The parameter provided is neither a local file nor a valid URL.{Style.RESET_ALL}")
        sys.exit(1)


def main():
    if len(sys.argv) == 1:
        usage()


    json_data = get_json_data(args.headers)

    files = []
    if json_data:
        for index, source in enumerate(json_data['sources']):
            dir_path = "./" + os.path.dirname(source).replace("webpack://", "webpack/")
            
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            
            file_name = os.path.basename(source)
            file_path = os.path.join(dir_path, file_name)
            file_path = os.path.normpath(file_path)        

            try:
                with open(file_path, 'w') as file:
                    file.write(json_data['sourcesContent'][index])
            except:
                print(f"{Fore.RED}[-] Can not write file \"{file_path}\"{Style.RESET_ALL}")
            
            files.append(file_path)

        print(f"{Fore.GREEN}[+] All source codes have been extracted from map file{Style.RESET_ALL}")
        
        if not args.silent:
            for filepath in files:
                print(f"\t[*] {filepath}")
        
    print()


def is_valid_url(url):
    """Checks if the URL is valid."""
    
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// ou https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domaine...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...ou ip
        r'(?::\d+)?'  # port optionnel
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return re.match(regex, url) is not None


if __name__ == "__main__":
    main()
