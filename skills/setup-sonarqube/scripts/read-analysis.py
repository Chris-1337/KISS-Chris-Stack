#!/usr/bin/env python3
"""Read analysis evidence using a user token with project read permissions."""
import argparse
import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def verify_read_access(project_key, analysis_id, task_id, source_key, request_json):
    queries = {
        "issues": ("/api/issues/search", {"componentKeys": project_key, "ps": 100}),
        "measures": ("/api/measures/component", {"component": project_key, "metricKeys": "bugs,vulnerabilities,code_smells,coverage"}),
        "source": ("/api/sources/lines", {"key": source_key, "from": 1, "to": 100}),
        "task": ("/api/ce/task", {"id": task_id}),
        "gate": ("/api/qualitygates/project_status", {"analysisId": analysis_id}),
    }
    return {name: request_json(path + "?" + urlencode(params)) for name, (path, params) in queries.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("project", "analysis-id", "task-id", "source-key"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    host = os.environ["SONAR_HOST_URL"].rstrip("/")
    token = os.environ["SONAR_READER_TOKEN"]

    def request_json(path):
        request = Request(host + path, headers={"Authorization": "Bearer " + token})
        with urlopen(request, timeout=30) as response:
            return json.load(response)

    evidence = verify_read_access(args.project, args.analysis_id, args.task_id, args.source_key, request_json)
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
