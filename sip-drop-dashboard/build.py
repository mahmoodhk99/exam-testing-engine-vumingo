#!/usr/bin/env python3
"""Build the SIP Drop Dashboard from the two source reports.

Usage:
    pip install openpyxl xlrd
    python build.py contactdetail_1.xlsx Test_PAS.xls

Produces (next to this script):
    data.json    aggregated + per-call data
    index.html   self-contained dashboard (data embedded)

A "drop" = an outbound call originating from sip:100@zain.com whose
End Type is "Far End Disconnect" (the agent / far end hung up). Every row
in the contact detail report is such a call, counted against the agent
identified by the destination extension. Agent names come from the POM
Agent Summary Report (Test_PAS.xls).
"""
import json
import os
import re
import sys

import openpyxl
import xlrd

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "template.html")


def load_agent_map(pas_path):
    """Map agent extension (Agent ID) -> agent name from the PAS report."""
    wb = xlrd.open_workbook(pas_path)
    ws = wb.sheet_by_index(0)
    amap = {}
    for r in range(7, ws.nrows):
        aid = str(ws.cell_value(r, 0)).strip().replace(".0", "")
        if not re.fullmatch(r"\d+", aid):
            continue
        raw = str(ws.cell_value(r, 2)).strip()
        m = re.search(r"\((.*?)\)", raw)
        amap[aid] = (m.group(1) if m else raw).strip()
    return amap


def load_calls(detail_path, amap):
    wb = openpyxl.load_workbook(detail_path, read_only=True, data_only=True)
    ws = wb["Details"]
    rows = list(ws.iter_rows(values_only=True))
    hdr = [str(h).strip() for h in rows[0]]
    idx = {name: hdr.index(name) for name in
           ("Start Time", "Destination #", "Duration", "End Details")}
    calls = []
    for r in rows[1:]:
        ext = re.sub(r"sip:(\d+)@.*", r"\1", str(r[idx["Destination #"]]))
        dur = r[idx["Duration"]]
        calls.append({
            "t": str(r[idx["Start Time"]]),
            "e": ext,
            "n": amap.get(ext, "Unknown (%s)" % ext),
            "d": int(dur) if dur not in (None, "") else 0,
            "r": str(r[idx["End Details"]]).replace("FarEndDisconnect : ", ""),
        })
    period = ""
    if "Summary" in wb.sheetnames:
        srows = list(wb["Summary"].iter_rows(values_only=True))
        if srows and len(srows[0]) > 1:
            period = str(srows[0][1])
    return calls, period


def main():
    if len(sys.argv) >= 3:
        detail_path, pas_path = sys.argv[1], sys.argv[2]
    else:
        detail_path, pas_path = "contactdetail_1.xlsx", "Test_PAS.xls"

    amap = load_agent_map(pas_path)
    calls, period = load_calls(detail_path, amap)
    data = {
        "period": period,
        "origin": "sip:100@zain.com",
        "total": len(calls),
        "calls": calls,
    }
    json.dump(data, open(os.path.join(HERE, "data.json"), "w"))

    tpl = open(TEMPLATE).read()
    html = tpl.replace("__DATA__", json.dumps(data, separators=(",", ":")))
    open(os.path.join(HERE, "index.html"), "w").write(html)
    print("Built %d calls across %d agents." %
          (len(calls), len({c["e"] for c in calls})))


if __name__ == "__main__":
    main()
