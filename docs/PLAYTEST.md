# Fresh-session alpha playtest

This is the remaining validation step for `0.1.0-alpha.1`. It measures a real player's comprehension and pacing; it is not another automated balance run.

## Start without touching an existing save

From the repository or extracted alpha package:

```powershell
python -B -m alpha.server --data-dir playtest-data
```

Open <http://127.0.0.1:8765>. Keep the terminal open. Delete `playtest-data` only when you intentionally want another fresh run.

## Session path

Play normally without simulator automation. Avoid reading source or economy tables during the session.

Record the elapsed time and any confusion at these moments:

1. First manual tap.
2. First Whisperer purchase.
3. First upgrade purchase.
4. First Omen noticed and collected or missed.
5. First fragment becomes available.
6. Two fragments become available.
7. Reawakening completed.
8. First memory and Sleeping vigil purchased.

After buying Sleeping vigil, use **Save & settings → Save now**, close the tab for at least 30 seconds, reopen it, and confirm that the welcome message reports offline earnings. Export the save once to confirm the download is understandable and easy to find.

Repeat these short checks at a narrow mobile viewport or on a phone:

- The vessel, quantity controls, producer costs, and settings button are readable without horizontal scrolling.
- Reawakening confirmation can be completed with the on-screen keyboard.
- The settings dialog and reset cancellation remain usable.

## Report

Copy this block into a note after the session:

```text
Platform/browser:
Session length:
First Whisperer:
First upgrade:
First Omen:
First fragment:
Two fragments:
Reawakening:
Offline earnings confirmed: yes/no
Mobile checks passed: yes/no

What was unclear:
What felt too slow or too fast:
Any error message, freeze, layout problem, or lost progress:
```

Do not tune from one player's exact completion time alone. Treat inability to understand the first purchase, save behavior, Reawakening, or offline unlock as an alpha blocker. Record pacing observations for comparison with the automated 69m15s–89m50s sample.
