import re
import json
import sys
import platform

import os
from os import system
from stat import *
import shutil

import requests
import argparse
import xml.etree.ElementTree as ET

from datetime import datetime

SAMPLE_CONFIG = {
    "title": "Sample Title",
    "subtitle": "Sample subtitle",
    "description": "Sample description",
    "toc": {
        "TOC1": "01:50",
        "TOC2": "20:30"
    },
    "links": {
        "Link1": "https://sdsc.edu",
        "Link2": "https://github.com"
    },
    "mp4_path": "",
    "vtt_path": "",
    "date": "1/1/2022"
}

LIST_PHP = """
<?php

if (file_exists("./page.json")) {
    $res = (array) json_decode(file_get_contents("./page.json"));
} else $res = array();

$res['list'] = array();
foreach (glob("./*/config.json") as $filename) {
    $config = file_get_contents($filename);
    $json = json_decode($config, true);
    $obj = array();
    $obj['path'] = explode("/", $filename)[1];
    $obj['title'] = $json['title'];
    $obj['subtitle'] = $json['subtitle'];
    $obj['description'] = $json['description'];
    $obj['time'] = strtotime($json['date']);
    array_push($res['list'], $obj);
}

echo json_encode($res);

?>
"""

def chmod_774(path):
    os.chmod(path, S_IRUSR | S_IWUSR | S_IXUSR | S_IRGRP | S_IWGRP | S_IXGRP | S_IROTH)

def sync_events():
    res = requests.get("https://sdsc.edu/education_and_training/training_hpc.xml")
    resText = res.text
    root = ET.fromstring(resText)

    page_nodes = root.findall("system-page")

    events = {}

    for page_node in page_nodes:

        page_id = page_node.get("id")
        name = page_node.find("name").text
        title = page_node.find("display-name").text

        item_node = page_node.find("system-data-structure")
        
        start = item_node.find("start_date")
        start_ts = int(start.text) // 1000 if start is not None else None

        end = item_node.find("end_date")
        end_ts = int(end.text) // 1000 if end is not None else None

        desc_long_node = item_node.find("description_long/p")
        long = ET.tostring(desc_long_node, encoding="unicode", method="html") if desc_long_node else None
        short = item_node.find("description_short").text
        
        instr_node = item_node.find("instructor")
        instr_label = instr_node.find("link_chooser/link_label").text
        instr_title = instr_node.find("instructor_title").text
        instr_bio = instr_node.find("instructor_bio").text

        external_links = page_node.findall(".//external_link")

        intvid_link = None
        for link_node in external_links:
            link = link_node.text
            if link is None:
                continue
            if link.startswith("https://education.sdsc.edu/training/interactive/"):
                intvid_link = link.replace("https://education.sdsc.edu/training/interactive/", "")

        events[page_id] = {
            "name": name,
            "title": title,
            "start": start_ts,
            "end": end_ts,
            "desc" : {
                "long": long,
                "short": short
            },
            "instr": {
                "label": instr_label,
                "title": instr_title,
                "bio": instr_bio
            },
            "vid_link": intvid_link
        }

    json.dump(events, open("events.json", "w"), indent=4)
    print(f"Sync {len(events)} events")

def build_list_html():

    try:
        with open("template.html") as f:
            html = f.read()
    except:
        print("template.html required, make sure it's in the same directory as the script")
        return

    try:
        events = json.load(open("events.json"))
    except:
        print("events.json required (run with --sync first before build)")
        return

    sections = []
    for key in events:

        item = events[key]
        link = item["vid_link"]

        start = datetime.fromtimestamp(item["start"])

        if start > datetime.now():
            continue

        end = datetime.fromtimestamp(item["end"])

        month_str = start.strftime("%b") if start.month == end.month else start.strftime("%b") + "-" + end.strftime("%b")
        day_str = start.day if start.day == end.day else str(start.day) + "-" + str(end.day)
        year_str = start.year if start.year == end.year else str(start.year) + "-" + str(end.year)

        content = ""

        time_box = f"""
            <div class="event-box">
                <span class="event-month">{month_str}</span>
                <span class="event-day">{day_str}</span>
                <span class="event-year">{year_str}</span>
            </div>
        """

        if link is None:
            content = f"""
                <h2>{item["title"]}</h2>
                <p>
                    <em>{item["desc"]["short"] or item["desc"]["long"]}</em>
                </p>
                """
        else:
            content = f"""
            <h2>
                <a href="{link}">{item["title"]}</a>
            </h2>
            <p>
                <em>{item["desc"]["short"] or item["desc"]["long"]}</em>
            </p>
            """

        sections.append(f"""
        <li class="event">
            {time_box}
            <div class="event-details">
                {content}
            </div>
        </li>
        """)

    with open("dev.html", "w", encoding="utf8") as out:
        out.write(html.replace("{PAGES}", "</hr>".join(sections)))

    print(f"Built dev.html with {len(sections)} pages")
   
def init_webinar(folder_name):
    m = re.match(r"^20(\d{2})(0[1-9]|1[012])_([a-z|_]+)$", folder_name)
    if not m:
        print(f"{colors.FAIL}Please follow the webinar folder naming convention: YYYYMM_lower_case e.g. 202202_hello_world{colors.ENDC}")
        return

    try:
        os.mkdir(folder_name)
        chmod_774(folder_name)
    except:
        print(f"{colors.WARNING}Folder already exists{colors.ENDC}")
        return
        
    shutil.copy2("webinar.html", os.path.join(folder_name, "index.html"))
    chmod_774(os.path.join(folder_name, "index.html"))

    with open(os.path.join(folder_name, "config.json"), "w") as f:
        json.dump(SAMPLE_CONFIG, f, indent=4)
    chmod_774(os.path.join(folder_name, "config.json"))

    print(f"{colors.OKGREEN}Webinar created: {colors.ENDC}{colors.UNDERLINE}https://education.sdsc.edu/training/interactive/{folder_name}{colors.ENDC}")

def init_series(folder_name, title):
    # enforce naming convention here?

    try:
        os.mkdir(folder_name)
        chmod_774(folder_name)
    except:
        print(f"{colors.WARNING}Folder already exists{colors.ENDC}")
        return
        
    shutil.copy2("series_list.html", os.path.join(folder_name, "index.html"))
    chmod_774(os.path.join(folder_name, "index.html"))

    with open(os.path.join(folder_name, "page.json"), "w") as f:
        json.dump({ "title": title }, f, indent=4)
    chmod_774(os.path.join(folder_name, "page.json"))

    with open(os.path.join(folder_name, "list.php"), "w") as f:
        f.write(LIST_PHP)
    chmod_774(os.path.join(folder_name, "list.php"))

    print(f"{colors.OKGREEN}Series created:{colors.ENDC} {colors.UNDERLINE}https://education.sdsc.edu/training/interactive/{folder_name}{colors.ENDC}")

def add_series(series_name, folder_name):

    if not os.path.exists(series_name):
        print(f"{colors.FAIL}Series does not exists{colors.ENDC}")
        return

    vid_path = os.path.join(series_name, folder_name)
    
    try:
        os.mkdir(vid_path)
        chmod_774(vid_path)
    except:
        print(f"{colors.WARNING}Folder already exists{colors.ENDC}")
        return

    shutil.copy2("series.html", os.path.join(vid_path, "index.html"))
    chmod_774(os.path.join(vid_path, "index.html"))
    
    with open(os.path.join(vid_path, "config.json"), "w") as f:
        json.dump(SAMPLE_CONFIG, f, indent=4)
    chmod_774(os.path.join(vid_path, "config.json"))

    print(f"{colors.OKGREEN}Added video to{colors.ENDC} {colors.OKCYAN}{series_name}{colors.ENDC}: " +
        f"{colors.UNDERLINE}https://education.sdsc.edu/training/interactive/{series_name}/{folder_name}{colors.ENDC}")

class colors:
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    UNDERLINE = '\033[4m'

def hide_colors():
    colors.OKCYAN = ''
    colors.OKGREEN = ''
    colors.WARNING = ''
    colors.FAIL = ''
    colors.ENDC = ''
    colors.UNDERLINE = ''

def main():
    parser = argparse.ArgumentParser()

    # Optional arguments
    
    # parser.add_argument("--verbose", help="Increase output verbosity", action="store_true")
    parser.add_argument("--sync", help="Sync events from SDSC main site", action="store_true")
    parser.add_argument("--build", help="Build list page from local event json databases", action="store_true")
    parser.add_argument("--webinar", help="Initialize a folder for a webinar", type=str)
    parser.add_argument("--series", help="Initialize a folder for a series, --title or --add is required", type=str)
    parser.add_argument("--init", help="Init a video series with a title (depends on --series)", type=str)
    parser.add_argument("--add", help="Add a video to the series (depends on --series)", type=str)

    args = parser.parse_args()

    if args.sync:
        sync_events()

    if args.build:
        build_list_html()

    if args.webinar:
        init_webinar(args.webinar)

    if args.series:
        if args.init:
            init_series(args.series, args.init)
        elif args.add:
            add_series(args.series, args.add)
        else:
            print(f"{colors.WARNING}Either --add or --init is required with --series{colors.ENDC}")
    else:
        if args.init or args.add:
            print("--series [series_name] is required")
    
if __name__ == "__main__":
    
    if not sys.stdout.isatty() or not sys.stderr.isatty():
        hide_colors()
    elif platform.system() == "Windows":
        system("color")

    main()
