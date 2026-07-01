# Nailer Drop Abuse Dashboard — sip:100@zain.com

A self-contained webpage that flags agents who **drop the nailer call from
their softphone** — abuse — by comparing dropped `sip:100@zain.com` nailer
calls against POM's In Job Break records, per login session.

## The abuse rule
When a nailed agent's `sip:100@zain.com` call drops **legitimately**, POM
records one **In Job Break** for that session. So a nailer drop with **no
matching In Job Break is abuse**: the agent hung up the nailer from the
softphone rather than it dropping as part of normal job handling.

Each dropped nailer call (from the contact-detail report) is attributed to
the login **session** whose Login–Logout window contains the call time, then
compared with that session's In Job Break count:

```
abuse (per session) = max(0, nailer drops − in-job breaks)
```

In the current data this flags **951 abusive drops** across **500 sessions**
by **136 of 177 agents**.

## How to use
Open **`index.html`** in any web browser (no server needed — the data is
embedded in the file).

Features:
- Summary cards: abusive drops, agents flagged, sessions with abuse,
  total sip:100 nailer drops, total In Job Break drops, date period.
- Per-agent table: **abuse drops (no break)**, **abuse sessions**,
  **sip:100 drops**, **In Job Breaks**, job count and total talk time (in
  **minutes**). Sort, search, and an "Only flagged agents" filter.
- Agent rows with any abuse are tinted red.
- Click any agent to expand their **sessions** (Login → Logout). Each session
  header shows its **nailer drops** vs **In Job breaks**; when drops exceed
  breaks the session is **red** with an `abuse: N drops w/o break` badge. The
  jobs in the session (Job Attach → Job Detach) are listed with call count,
  talk minutes and break count.

## Data sources
1. **In Job Break Count** — from `Test_PAS.xls`, the POM Agent Summary
   Report (hierarchical: Agent → Session (Login/Logout) → Job
   (Job Attach/Detach)). POM logs one In Job Break when the nailer drops as
   part of normal job handling.
2. **sip:100 nailer drops** — from `contactdetail_1.xlsx`, each
   `sip:100@zain.com` contact that ended in Far End Disconnect, with its
   start time (used to place each drop in a session).

## Rebuilding
If the source reports change, regenerate the page with:

```bash
pip install openpyxl xlrd
python build.py contactdetail_1.xlsx Test_PAS.xls
```

This rewrites `data.json` and `index.html` from `template.html`.
