# SIP Drop Dashboard — In Job Break vs sip:100@zain.com nailer drops

A self-contained webpage that shows, per agent, how many `sip:100@zain.com`
nailer calls were dropped, measured two ways and compared side by side.

## How to use
Open **`index.html`** in any web browser (no server needed — the data is
embedded in the file).

Features:
- Summary cards: total In Job Break drops, total sip:100 nailer drops,
  agents, repeat-break jobs, date period.
- Per-agent table: **In Job Break Count**, **sip:100 drops**, a match
  indicator, job count, total talk time (in **minutes**), and the number of
  repeat-drop sessions.
- Sort, search, and a "Only agents with repeat-drop sessions" filter.
- Click any agent to expand their **sessions** (Login → Logout). Each session
  header shows, for that session, how many **nailer calls dropped**
  (sip:100 drops attributed to the session by call time) and its
  **In Job break count**, followed by the **jobs** in the session
  (Job Attach → Job Detach) with per-job call count, talk minutes and break
  count.
- **Red sessions** = login sessions where the nailer dropped **more than
  once**. Individual **job rows** are also red when that job's break count
  is greater than 1.

## The two drop measures
1. **In Job Break Count** (from `Test_PAS.xls`, the POM Agent Summary
   Report). When the `sip:100@zain.com` nailer call to a nailed agent drops
   during a job, POM records one "In Job Break" for that job.
2. **sip:100 nailer drops** (from `contactdetail_1.xlsx`). Count of
   `sip:100@zain.com` contacts that ended in Far End Disconnect for the agent.

### Note on the totals
Across all agents these come to **820 in-job breaks** vs **1,718 sip:100
drops**, and they match exactly for only 35 of 177 agents. So in this data
the two measures are **not** identical — the contact-detail report counts
more nailer disconnects than POM logs as in-job breaks (a nailer call that
ends normally at job detach also shows as Far End Disconnect but is not an
in-job break). The dashboard shows both numbers and the delta per agent so
the difference is visible.

## Data sources
- **contactdetail_1.xlsx** — Avaya Experience Portal contact detail report
  (each sip:100@zain.com nailer call, its destination agent extension,
  duration and end type).
- **Test_PAS.xls** — POM Agent Summary Report. Hierarchical:
  Agent → Session (Login/Logout) → Job (Job Attach/Detach) with Call Count,
  Talk Duration and In Job Break Count per job. Also maps each extension to
  the agent name.

## Rebuilding
If the source reports change, regenerate the page with:

```bash
pip install openpyxl xlrd
python build.py contactdetail_1.xlsx Test_PAS.xls
```

This rewrites `data.json` and `index.html` from `template.html`.
