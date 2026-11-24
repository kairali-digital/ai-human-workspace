# Windows 2.5.1 release assessment

The employee and reusable ZIPs were rebuilt and tested on GitHub-hosted Windows Server 2025. On each edition the updater verified the source, upgraded a synthetic 2.4.0 worker, and restored 2.4.0 with all 23 worker-owned files preserved. A direct upgrade from 2.3.0 was refused before worker changes. A separate check registered, fired, paused, resumed and removed a real Windows scheduled task. The runner confirmed the updater digest and the installer hashes. [Windows qualification](https://github.com/kairali-digital/ai-human-workspace/actions/runs/45353971929)

Release authorization is recorded separately for the exact signed commit and ZIP hashes after the final builder, Claude, Monitor, employee desktop and independent recovery checks. Installing this version does not enroll a worker in scheduled updates.
