# How to read the Nailer Drop Abuse Dashboard

This guide explains, in plain language, what the dashboard shows and how every
number is worked out. (The same guide is built into the page — click
**📖 How to read this dashboard** at the top.)

## What it finds

It flags agents who **hang up the `sip:100@zain.com` nailer call from their
softphone** to avoid taking calls. When a nailer call drops legitimately, POM
records an **In Job Break** for that session. So:

> A nailer drop with **no matching In Job Break = abuse.**

## Words to know

- **Nailer call (`sip:100@zain.com`)** — the always-on call that keeps a
  "nailed" agent connected to the dialer; customer calls bridge into it.
- **In Job Break** — POM's record of a *legitimate* nailer drop while the
  agent is working a job.
- **Session** — one agent login (**Login → Logout**).
- **Job** — a campaign the agent attached to (**Job Attach → Job Detach**).

## The top cards

| Card | Meaning |
|---|---|
| **Abusive drops (no break)** | Total nailer drops with no matching break. |
| **Agents flagged** | How many agents have any abuse. |
| **Sessions with abuse** | Sessions containing an abuse drop. |
| **Dropped w/o break → then off** | Sessions where an abuse drop was followed by going off before the next login. |
| **sip:100 nailer drops** / **In Job Break drops** | Raw totals, for reference. |

## The agent table

| Column | Meaning |
|---|---|
| **Abuse drops (no break)** | `nailer drops − in-job breaks` for the agent. |
| **Abuse sessions** | How many of the agent's sessions had any abuse. |
| **Abuse time** | Total off-work time caused by abuse drops (see formula below). |
| **sip:100 drops** | All nailer drops for the agent. |
| **In Job Breaks** | Breaks POM logged for the agent. |
| **Jobs** | Number of jobs attached. |
| **Talk (min)** | Total talk time. |

Use the **search** box, the **sort** menu (or click a column header), and the
**Only flagged agents** checkbox to focus. **Click any agent row** to expand.

## Inside an expanded agent

Each **session** has a header bar:

- **Nailer dropped: N times** — nailer drops in that session.
- **In Job breaks: N** — breaks POM logged that session.
- **Abuse time** — off-work time from that session's abuse drops.
- **Off after** — time logged out after this session (`next login − this logout`).
- 🚩 **abuse: N drops w/o break** (red) — the session had abuse drops.
- ⚠ **dropped w/o break, then off N before next login** (amber) — an abuse
  drop **and** then off before the next login, i.e. the agent dropped the
  nailer to take an **unlogged gap**.

Below the header:

- 🔴 **Nailer dropped: &lt;date&gt;** — one row per drop, showing the drop's
  date/time and how long the agent was off until the **date of the next job
  they attached to** (marked "logged off first" if they logged out in
  between).
- The **jobs list** (in date/time order): each campaign with Job Attach, Job
  Detach, Calls, Talk (min) and Breaks.

## Colours

- **Red** = abuse (a drop with no break).
- **Amber** = dropped without a break, then went off before the next login.

## How the key numbers are calculated

- A **nailer drop** = a `sip:100@zain.com` call that ended in *Far End
  Disconnect*, assigned to the session whose Login–Logout window contains it.
- **abuse (per session)** = `nailer drops − in-job breaks`.
- **abuse time** = the **merged** (union of) spans from each abuse drop to the
  **next job the agent attached to**. Merging means several drops before one
  re-attach are counted **once** (first drop → next job attach), not summed —
  so an agent's abuse time never exceeds their working day.

## A quick workflow

1. Sort by **Abuse drops** or **Abuse time** (or tick **Only flagged agents**).
2. Open the worst agents.
3. Read their **red 🔴 drop rows** (when they dropped, how long they stayed
   off) and **amber sessions** (dropped then took an unlogged gap).
