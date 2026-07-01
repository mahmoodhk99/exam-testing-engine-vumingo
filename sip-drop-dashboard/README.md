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
- Summary cards: **total abuse time** (sum of all abuse times), abusive
  drops, agents flagged, sessions with abuse, dropped-w/o-break-then-off,
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
- Between two consecutive sessions a dashed **⏳ logged out … between
  sessions** line shows the **away time** — from the earlier session's logout
  to the next session's login (e.g. logout 05:20:33 PM → login 05:22:37 PM =
  2 min).
- Each session header also shows **Abuse time** (total time off a job caused
  by that session's abuse drops) and **Off after** = the time the agent was
  logged out after this session (next session's login − this session's
  logout). An **⚠ amber** badge flags the strong case: a session with an
  abuse drop (no break) that is then followed by an off-gap before the next
  login. The summary card **Dropped w/o break → then off** counts these.
- For every nailer drop a red **🔴 Nailer dropped** row shows the **date/time
  of the dropped call** and its **abuse time** = time from the drop until the
  next job the agent attached to (how long they stayed off a job after
  dropping). Shows "no job afterwards" when it was the last drop of the day.
- Inside each session the jobs are listed **by date/time** (chronological),
  and a **⏳ detached …** row marks idle time when the agent was **not
  attached to any job** — measured as one job's detach to the next job's
  attach (also login → first attach, and last detach → logout). The session
  header's **Detached** total sums all of it. Example: last job detaches
  06:07:07 PM and the next attaches 06:17:06 PM ≈ 10 min detached. Idle
  markers show for gaps ≥ 60 seconds.

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
