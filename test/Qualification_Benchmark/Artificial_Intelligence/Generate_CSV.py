import argparse
import yaml
import csv
import os
import sys

def normalize_title(t):
    return t.lower().strip()

def load_master_papers(path):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
        paper_list = data.get("papers", [])  # expects: papers: [...]
    return paper_list

def extract_title_url_csv(papers, output_path):
    rows = [{"title": p["title"], "url": p.get("url", "")} for p in papers]
    rows.sort(key=lambda x: x["title"].lower())

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "url"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"✅ Title/URL CSV written to {output_path}")

def load_yaml_file(path):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        data = yaml.safe_load(f) or {}

    if isinstance(data, dict) and "papers" in data:
        return data["papers"]
    elif isinstance(data, list):
        return data
    else:
        return []

def main():
    parser = argparse.ArgumentParser(description="Generate CSV from paper metadata and decisions")
    parser.add_argument("base_paper", help="Master paper YAML (with 'papers: [...]')")
    parser.add_argument("qualified", nargs="?", default=None, help="qualified_papers.yaml (optional)")
    parser.add_argument("disqualified", nargs="?", default=None, help="disqualified_papers.yaml (optional)")
    parser.add_argument("-o", "--output", required=True, help="Output CSV filename")

    args = parser.parse_args()

    base_papers = load_master_papers(args.base_paper)

    # MODE 1: Only base_paper provided → dump title + url
    if not args.qualified and not args.disqualified:
        extract_title_url_csv(base_papers, args.output)
        return

    # MODE 2: Full model comparison mode
    master_map = {normalize_title(p["title"]): p.get("url", "") for p in base_papers}
    rows = []

    for file_path in [args.qualified, args.disqualified]:
        if not file_path:
            continue
        papers = load_yaml_file(file_path)
        print(f"✅ Loaded {len(papers)} papers from {file_path}")

        for paper in papers:
            title = paper.get("title", "").strip()
            title_key = normalize_title(title)
            url = master_map.get(title_key, "NOT FOUND")
            decisions = paper.get("decisions", {})
            rows.append({
                "title": title,
                "url": url,
                "evaluation_prompt": decisions.get("evaluation_prompt", ""),
                "related_work_prompt": decisions.get("related_work_prompt", ""),
                "novelty_prompt": decisions.get("novelty_prompt", ""),
                "review_only_prompt": decisions.get("review_only_prompt", "")
            })

    rows.sort(key=lambda x: x["title"].lower())

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "title", "url", "evaluation_prompt",
            "related_work_prompt", "novelty_prompt", "review_only_prompt"
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Full decision CSV written to {args.output}")

if __name__ == "__main__":
    main()