---
name: deploy-to-raspi
description: Deploy this repo's `remote/` bot to the Raspberry Pi it runs on — pull the latest master over SSH and restart the live `bot` systemd service. Use whenever the user asks to deploy, ship, push out, or roll out a change to the pi/raspberry pi/bot, or says "/deploy-to-raspi".
---

# Deploy to Raspberry Pi

The bot on the Pi is live — it's actively polling Telegram and controlling
real devices while you deploy. Every step here is deliberately boring and
sequential so a bad deploy fails loudly instead of leaving the service in a
broken half-updated state. Do this yourself, by hand, every time — don't
delegate it (see `delegate-grunt`'s exclusion for destructive/remote-prod
work; a model guessing at SSH output here is exactly the wrong place to
save effort).

## Steps

1. **Push first.** The Pi pulls from `origin/master`, so local commits
   that aren't pushed yet won't be there to pull.

2. **Check for local drift on the Pi — abort if any:**
   ```bash
   ssh pi "cd /home/pi/remote && git status --short"
   ```
   Any output here means someone edited files directly on the Pi. Stop and
   tell the user — pulling over uncommitted local changes can silently
   discard them or fail outright. Don't try to resolve it yourself.

3. **Pull — abort on any error or conflict:**
   ```bash
   ssh pi "cd /home/pi/remote && git pull"
   ```
   Expect `Fast-forward`. Anything else (merge conflict, diverged branches,
   network error) means stop and report it rather than guessing a fix.

4. **Restart the service:**
   ```bash
   ssh pi "sudo systemctl restart bot"
   ```

5. **Verify it actually came back up:**
   ```bash
   ssh pi "sleep 2 && systemctl status bot --no-pager -l | head -10"
   ```
   Confirm `Active: active (running)` with a recent start time and no
   immediate crash. If it's not active, or it stopped right after
   starting, the deploy failed — report the status output, don't restart
   again speculatively.

## Why each check matters

Steps 2 and 3 exist because `git pull` on a dirty tree or a diverged branch
can do something other than what you expect, and this is a live service —
better to stop and ask than to guess. Step 5 exists because `systemctl
restart` returning success only means systemd *tried* to start it; the
process can still crash immediately after (e.g. a bad import), and the only
way to know is to check.
