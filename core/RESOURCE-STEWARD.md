# RESOURCE STEWARD

Take a read-only host snapshot before recommending cleanup. Keep current pressure,
physical memory, swap, process RSS and browser-tab evidence separate. Missing host or
browser signals stay `UNKNOWN`; do not infer current pressure merely because swap is
non-zero. Process RSS is a review ranking, not permission to quit an application.

A browser tab becomes a discard candidate only when the owner policy allows it and the
trusted adapter confirms every condition: public non-sensitive classification, inactive,
discard support, allowed ownership, no unsaved form, no authentication/payment/admin
page, no active download, no meeting and no playing audio. Unknown means not a candidate.
The core never force-quits an app, erases sessions/cookies or bypasses permission.

The plan does not operate the browser. It requires an approved host adapter and remains
bounded by the Work Governor. Record `USER_REFUSED` or `ADAPTER_UNAVAILABLE` truthfully.
After any execution, capture a later host snapshot. Report improvement only when the
host evidence shows lower classified pressure or both more available memory and lower
used percentage; otherwise record `EXECUTED_NO_IMPROVEMENT`.
