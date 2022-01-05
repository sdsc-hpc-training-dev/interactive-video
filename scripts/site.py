import json
import requests
import argparse
import xml.etree.ElementTree as ET

def sync_events():
    res = requests.get("https://www.sdsc.edu/news_and_events/events.xml")
    resText = res.text
    root = ET.fromstring(resText)

    page_nodes = root.findall("system-page")

    events = {}

    for page_node in page_nodes:

        page_id = page_node.get("id")
        name = page_node.find("name").text
        title = page_node.find("display-name").text

        start = page_node.find("start-date")
        start_ts = int(start.text) if start is not None else None

        end = page_node.find("end-date")
        end_ts = int(end.text) if end is not None else None

        item_node = page_node.find("system-data-structure")
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

def build_html():

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

        if link is None:
            sections.append(f"""
                <h2>{item["title"]}</h2>
                <p>
                    <em>{item["desc"]["long"] or item["desc"]["short"]}</em>
                </p>
                """)
        else:
            sections.append(f"""
            <h2>
                <a href="{link}">{item["title"]}</a>
            </h2>
            <p>
                <em>{item["desc"]["long"] or item["desc"]["short"]}</em>
            </p>
            """)

    with open("dev.html", "w", encoding="utf8") as out:
        out.write(html.replace("{PAGES}", "</hr>".join(sections)))

    print(f"Built dev.html with {len(sections)} pages")
   
def main():
    parser = argparse.ArgumentParser()

    # Optional arguments
    
    # parser.add_argument("--verbose", help="Increase output verbosity", action="store_true")
    parser.add_argument("--sync", help="Sync events from SDSC main site", action="store_true")
    parser.add_argument("--build", help="Build list page from local event json databases", action="store_true")

    args = parser.parse_args()

    if args.sync:
        sync_events()

    if args.build:
        build_html()
    

if __name__ == "__main__":
    main()