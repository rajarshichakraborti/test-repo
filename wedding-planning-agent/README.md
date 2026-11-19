# Wedding Planning Agent

An open-source, privacy-first command-line wedding planning assistant. Organize guests, travel, accommodation, vendors, events, and message drafts without publishing anyone's private information.

## Quick start

Requires Python 3.10+; no third-party packages.

```bash
git clone https://github.com/rajarshichakraborti/test-repo.git
cd test-repo/wedding-planning-agent
cp data.example.json data.json
python3 wedding_agent.py summary
python3 wedding_agent.py guests
python3 wedding_agent.py tasks
python3 wedding_agent.py draft guest-001
python3 wedding_agent.py instinct guest-001
```

Edit `data.json` to enter your own wedding details. It is ignored by git; never commit real guest information.

## Commands

- `summary` — aggregate counts and upcoming tasks
- `guests` — show guest attendance/travel status
- `tasks` — list task ownership and due dates
- `draft GUEST_ID` — draft a personalized RSVP/travel coordination message, no sending
- `instinct GUEST_ID` — output a structured handoff for Instinct to review and send, subject to its available permissions
- `export-instinct` — print a privacy-minimized wedding status brief for use with Instinct

## Instinct support

Instinct is a third-party messaging agent. As of November 2026, a stable public developer API for direct messaging could not be verified. This project **does not claim direct Instinct sending**, does not collect Instinct passwords or tokens, and never automatically sends messages. Its current integration is a **human-approved copy/paste handoff**. Do not share the full guest database with Instinct; give it the minimum recipient details and draft required for one message.

1. Run `python3 wedding_agent.py instinct guest-001`.
2. Review and copy the generated instructions into your own Instinct chat.
3. Ask Instinct to confirm the recipient and final content **before** sending.
4. Verify delivery in your messaging app.
5. If Instinct later publishes a documented API or remote MCP capability, implement it separately with scoped credentials, explicit consent, and audit logs.

## Data model

`data.example.json` demonstrates events, guests, accommodation, flights, vendors and tasks. It deliberately contains fictional records, no credentials, and no real wedding details.

## Security

- `data.json`, `.env`, backups and exported messages are excluded from Git.
- Do not publish phone numbers, guest names, bookings, flight PNRs, addresses, or vendor contracts without consent.
- Inspect every message before sending; do not mass-message guests without their consent.
- This is a starter utility, not an autonomous sending service.

## Contributing

Open an issue or pull request. Add tests for new integrations and avoid dependencies on private accounts.

## License

MIT. See `LICENSE`.
