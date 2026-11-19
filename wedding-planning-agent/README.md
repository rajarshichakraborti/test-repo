# Wedding Planning Agent

An open-source, **local-first** wedding planning assistant, including optional WhatsApp/Instinct message handoffs. It can organize guests, RSVPs, flights, accommodation, vendors, events, tasks, and draft personalized communication. All example records are **fictional**.

**Privacy commitment:** This public repository contains no real wedding information, guest names, phone numbers, flight itineraries, booking references, addresses, family records, menus from private events, or account credentials. Store your real information only in a private local `data.json` file, which is ignored by Git.

## Quick start

Requires Python 3.10+ and no extra Python packages.

```bash
git clone https://github.com/rajarshichakraborti/test-repo.git
cd test-repo/wedding-planning-agent
cp data.example.json data.json
python3 wedding_agent.py summary
python3 wedding_agent.py dashboard
```

On Windows, use `copy data.example.json data.json` and `python` instead of `python3` if needed. The dashboard opens at `http://127.0.0.1:8765`, accessible only on your own computer.

## Commands

```bash
python3 wedding_agent.py summary
python3 wedding_agent.py guests
python3 wedding_agent.py tasks
python3 wedding_agent.py draft guest-001 --kind rsvp
python3 wedding_agent.py whatsapp guest-001 --kind travel
python3 wedding_agent.py instinct guest-001 --kind accommodation
python3 wedding_agent.py instinct-rules
python3 wedding_agent.py dashboard
```

- `draft`: print a message for review.
- `whatsapp`: open the named guest's WhatsApp chat with the message **prefilled**, no copy/paste necessary; **you review and press Send**. Requires a guest phone with international country code in *private* `data.json`.
- `instinct`: open a draft in WhatsApp addressed to the Instinct agent number if `settings.instinct_whatsapp_number` has been configured locally; otherwise opens a generic WhatsApp share composer to select the Instinct chat. **The Instinct chat must first be connected separately.**
- `instinct-rules`: open a proposed instruction set in WhatsApp for your Instinct chat, asking approval before messaging guests or acting on bookings.
- `dashboard`: show a localhost-only guest list with no-copy-paste WhatsApp draft links.

All commands are opt-in. **No command automatically sends a WhatsApp message.**

## Connecting Circles to Instinct (one-time account authorization)

Circles advertises a one-tap Instinct connection on its own service. To use it, visit [Circles for Instinct](https://usecircles.app/en/agents/instinct), sign in, link **your** WhatsApp account following its on-screen steps, select **Connect Instinct**, and approve the connection in WhatsApp. The one-time pairing/permissions must be authorized by the WhatsApp account owner and **cannot be completed by this GitHub project or a remote ChatGPT chat**. Verify independently that you trust this third-party provider; Circles' linked-device approach is not the same as a Meta-official WhatsApp Business API integration.

Once you have connected Instinct, send a rules handoff:
```bash
python3 wedding_agent.py instinct-rules
```

For each guest message, the app can open Instinct's WhatsApp chat with the proposed instruction and recipient:
```bash
python3 wedding_agent.py instinct guest-001
```

**Limitation:** Whether Instinct can actually send a message via Circles depends on the permissions and capabilities you enable in Instinct/Circles. This repository has **no verified direct Instinct API integration or autonomous send functionality** and must not be represented as connected or able to deliver messages. You can instead use `whatsapp` for a one-click draft that you manually send.

## Optional read-only Circles diagnostic

If you have obtained a Circles-issued API credential from Circles, you may test read-only allowed-chat access by setting `CIRCLES_KEY` in your shell and running `python3 wedding_agent.py circles-check`. API functionality can change; this is optional and is not needed for the Instinct WhatsApp pairing described above. Never put tokens into GitHub or `data.json`.

## Data format and guardrails

Use `data.example.json` as a template. All records in the example are intentionally fictional; `phone` is empty by default. Keep real event information in local `data.json`. `.gitignore` excludes this file and common exports. Git ignore rules do not retroactively protect any file already committed: always inspect `git status` before pushing.

**Messaging safety:** confirm who will receive each message, the exact contents, and that the recipient agreed to this kind of outreach. Do not allow Instinct to message entire groups, make bookings, make purchases, or change reservations without your explicit approval. Avoid transmitting sensitive travel identifiers or full accommodation information.

## Open-source license

MIT — see [LICENSE](LICENSE). Contributions are welcome, but **never include real guest data in issues, screenshots, pull requests, or test fixtures**.
