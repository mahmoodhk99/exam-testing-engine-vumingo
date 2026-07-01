#!/usr/bin/env python3
"""Build the SIP Drop Dashboard from the two source reports.

Usage:
    pip install openpyxl xlrd
    python build.py contactdetail_1.xlsx Test_PAS.xls

Produces (next to this script):
    data.json    per-agent / per-session / per-job data
    index.html   self-contained dashboard (data embedded)

What it shows
-------------
For each agent it compares two independent measures of dropped nailer calls:

  * In Job Break Count  -- from the POM Agent Summary Report (Test_PAS.xls).
    When the sip:100@zain.com nailer call to a nailed agent drops during a
    job, POM records one "In Job Break" for that job.
  * sip:100 nailer drops -- number of sip:100@zain.com contacts that ended
    in Far End Disconnect for that agent, from the contact detail report.

The PAS report is hierarchical: Agent -> Session (Login/Logout) ->
Job (Job Attach / Job Detach) with a Call Count, Talk Duration and
In Job Break Count per job. A job whose In Job Break Count is greater
than one (the nailer dropped more than once within the same Job
Attach-Detach window) is flagged red. All durations are reported in
minutes.
"""
import json
import os
import re
import sys
from collections import Counter

import openpyxl
import xlrd

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "template.html")

# Column positions in the PAS "Agent Summary Report" (0-based).
PAS = dict(agent_id=0, agent_name=2, session_id=6, login=8, logout=10,
           campaign=13, task=17, attach=19, detach=21, call_count=23,
           talk=25, in_job_break=31, in_job_break_dur=33)


def _dur_to_sec(s):
    s = str(s).strip()
    if not s or s == "None":
        return 0
    parts = s.split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
    except ValueError:
        return 0
    return 0


def _int(s):
    s = str(s).strip()
    try:
        return int(float(s))
    except ValueError:
        return 0


def load_nailer_drops(detail_path):
    """sip:100@zain.com Far-End-Disconnect drops per agent extension."""
    wb = openpyxl.load_workbook(detail_path, read_only=True, data_only=True)
    ws = wb["Details"]
    rows = list(ws.iter_rows(values_only=True))
    hdr = [str(h).strip() for h in rows[0]]
    dest = hdr.index("Destination #")
    drops = Counter(re.sub(r"sip:(\d+)@.*", r"\1", str(r[dest]))
                    for r in rows[1:])
    period = ""
    if "Summary" in wb.sheetnames:
        srows = list(wb["Summary"].iter_rows(values_only=True))
        if srows and len(srows[0]) > 1:
            period = str(srows[0][1])
    return drops, period


def load_pas(pas_path):
    """Parse the hierarchical PAS report into per-agent session/job data."""
    ws = xlrd.open_workbook(pas_path).sheet_by_index(0)

    def cv(r, c):
        return str(ws.cell_value(r, c)).strip()

    agents = {}          # ext -> agent dict
    cur = sess = None
    cur_campaign = ""
    for r in range(7, ws.nrows):
        aid = cv(r, PAS["agent_id"])
        if re.fullmatch(r"\d+(\.0)?", aid):
            cur = aid.replace(".0", "")
            m = re.search(r"\((.*?)\)", cv(r, PAS["agent_name"]))
            name = (m.group(1) if m else cv(r, PAS["agent_name"])).strip()
            agents.setdefault(cur, {"name": name, "ext": cur, "sessions": [],
                                    "ib": 0, "talk": 0, "jobs": 0})
            sess = None
        sid = cv(r, PAS["session_id"])
        if sid:
            sess = {"sid": sid, "login": cv(r, PAS["login"]),
                    "logout": cv(r, PAS["logout"]), "jobs": [], "ib": 0}
            agents[cur]["sessions"].append(sess)
        camp = cv(r, PAS["campaign"])
        if camp:
            cur_campaign = re.sub(r"\s*\(.*\)", "", camp).strip()
        if cv(r, PAS["task"]) == "Call_100" and cv(r, PAS["attach"]):
            ib = _int(cv(r, PAS["in_job_break"]))
            job = {"camp": cur_campaign, "attach": cv(r, PAS["attach"]),
                   "detach": cv(r, PAS["detach"]),
                   "cc": _int(cv(r, PAS["call_count"])),
                   "talk": _dur_to_sec(cv(r, PAS["talk"])), "ib": ib,
                   "ibdur": _dur_to_sec(cv(r, PAS["in_job_break_dur"]))}
            if sess is None:
                sess = {"sid": "?", "login": "", "logout": "",
                        "jobs": [], "ib": 0}
                agents[cur]["sessions"].append(sess)
            sess["jobs"].append(job)
            sess["ib"] += ib
            agents[cur]["ib"] += ib
            agents[cur]["talk"] += job["talk"]
            agents[cur]["jobs"] += 1
    return agents


def main():
    if len(sys.argv) >= 3:
        detail_path, pas_path = sys.argv[1], sys.argv[2]
    else:
        detail_path, pas_path = "contactdetail_1.xlsx", "Test_PAS.xls"

    drops, period = load_nailer_drops(detail_path)
    agents = load_pas(pas_path)

    out = []
    for ext, a in agents.items():
        a["sessions"] = [s for s in a["sessions"] if s["jobs"]]
        a["redjobs"] = sum(1 for s in a["sessions"]
                           for j in s["jobs"] if j["ib"] > 1)
        a["drops100"] = drops.get(ext, 0)
        out.append(a)

    data = {"period": period, "origin": "sip:100@zain.com",
            "totalDrops100": sum(drops.values()),
            "totalIB": sum(a["ib"] for a in out), "agents": out}
    json.dump(data, open(os.path.join(HERE, "data.json"), "w"),
              separators=(",", ":"))

    tpl = open(TEMPLATE).read()
    html = tpl.replace("__DATA__", json.dumps(data, separators=(",", ":")))
    open(os.path.join(HERE, "index.html"), "w").write(html)
    print("Built %d agents | In Job Break drops: %d | sip:100 drops: %d | "
          "repeat-break jobs: %d" %
          (len(out), data["totalIB"], data["totalDrops100"],
           sum(a["redjobs"] for a in out)))


if __name__ == "__main__":
    main()
