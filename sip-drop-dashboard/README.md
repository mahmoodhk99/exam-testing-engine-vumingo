# SIP Drop Dashboard — sip:100@zain.com

A self-contained webpage that shows, per agent, how many `sip:100@zain.com`
calls were **dropped by the agent** (Far End Disconnect).

## How to use
Open **`index.html`** in any web browser (no server needed — the data is
embedded in the file).

Features:
- Summary cards: total drops, agents involved, top agent, quick (≤5s) drops, date period.
- Sortable / searchable table of every agent with their drop count, a share
  bar, total & average talk time, and number of very short (≤5s) drops.
- Click any agent row to expand the individual dropped calls
  (start time, destination, duration, end detail).

## What counts as a "drop"
Every record in the source `contactdetail` report is an **outbound** call
originating from `sip:100@zain.com` whose **End Type = Far End Disconnect**
— i.e. the agent (the far/destination end) hung up the call. Each such
record is counted as one drop against that agent.

## Data sources
- **contactdetail_1.xlsx** — Avaya Experience Portal contact detail report.
  Provides each call: start time, originating (`sip:100@zain.com`),
  destination agent extension, duration, and end type.
- **Test_PAS.xls** — POM Agent Summary Report. Maps each agent extension
  (Agent ID) to the agent's name. All 174 extensions in the call report
  matched a name.

## Rebuilding
If the source reports change, regenerate the page with:

```bash
pip install openpyxl xlrd
python build.py contactdetail_1.xlsx Test_PAS.xls
```

This rewrites `data.json` and `index.html`.
