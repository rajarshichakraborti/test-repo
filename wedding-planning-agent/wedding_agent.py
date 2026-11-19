#!/usr/bin/env python3
"""Local-first wedding planner. No automatic messaging or third-party dependencies."""
import argparse
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
from urllib.parse import quote
from urllib.request import Request, urlopen
import webbrowser

ROOT = Path(__file__).resolve().parent
KINDS = ("rsvp", "travel", "accommodation")
CIRCLES_API = "https://app.usecircles.app/api/v1/agent"


def load_data():
    path = ROOT / "data.json"
    if not path.exists():
        path = ROOT / "data.example.json"
        print("Using fictional example records. Copy data.example.json to data.json to customize.")
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or not isinstance(data.get("guests", []), list):
        raise ValueError("Expected JSON object with guests list.")
    return data


def guest_by_id(data, guest_id):
    for guest in data.get("guests", []):
        if guest.get("id") == guest_id:
            return guest
    raise ValueError("Guest not found: " + str(guest_id))


def draft(data, guest_id, kind="rsvp"):
    if kind not in KINDS:
        raise ValueError("Unknown message type.")
    guest = guest_by_id(data, guest_id)
    name = guest.get("name", "there")
    title = data.get("wedding", {}).get("title", "our wedding")
    if kind == "rsvp":
        if guest.get("rsvp") == "confirmed":
            return f"Hi {name}, we're looking forward to celebrating {title} with you! Let us know if your plans change."
        return f"Hi {name}, we'd love to celebrate {title} with you! Could you confirm if you're able to attend?"
    if kind == "travel":
        return f"Hi {name}, could you share your arrival and departure timing for {title}, when available? Please don't send sensitive booking references in group chats."
    return f"Hi {name}, we're coordinating accommodation for {title}. Could you confirm your stay dates and whether you need a room?"


def sanitize_phone(phone):
    number = re.sub(r"[\s().+-]", "", str(phone))
    if not re.fullmatch(r"[1-9][0-9]{6,14}", number):
        raise ValueError("Phone must be in international format, e.g. +12025550123")
    return number


def whatsapp_url(phone, message):
    """Prefills WhatsApp. Never actually sends."""
    return "https://wa.me/" + sanitize_phone(phone) + "?text=" + quote(message, safe="")


def instinct_message(data, guest_id, kind="rsvp"):
    guest = guest_by_id(data, guest_id)
    recipient = guest.get("name", "Unknown")
    number = guest.get("phone", "").strip()
    if number:
        recipient += " (" + number + ")"
    return (
        "Wedding Planning Agent request\n"
        "Prepare this WhatsApp message; DO NOT SEND until I approve the recipient and exact text.\n"
        "Recipient: " + recipient + "\n"
        "Message:\n" + draft(data, guest_id, kind) + "\n"
        "Only use chats I explicitly authorized in Circles. Never share guest information "
        "in public or group chats. Do not retry a message after an uncertain delivery; "
        "check its status first."
    )


RULES = """Please apply these rules to my Wedding Planning Agent requests:
1. Ask me to approve the exact recipient and message before each send.
2. Never contact guests, vendors or groups autonomously.
3. Use only the WhatsApp chats I explicitly enable in Circles.
4. Do not reveal guest contact details, private bookings, travel references or finances in group chats.
5. If a send fails or its status is uncertain, report it and do not retry without my instruction.
6. Never make a booking, payment, cancellation or change without explicit approval.
7. Keep guest communications respectful and limited to the wedding.
8. Tell me what happened with each send; don't claim delivery without a receipt.
Please acknowledge these rules before I issue the first request.
"""


def open_instinct(data, message):
    number = data.get("settings", {}).get("instinct_whatsapp_number", "").strip()
    if number:
        url = whatsapp_url(number, message)
    else:
        # Instinct's number varies by account; let the user choose its chat.
        url = "https://wa.me/?text=" + quote(message, safe="")
    webbrowser.open(url)
    print("Opened a prefilled WhatsApp composer. Choose your Instinct chat if prompted.")
    print("Review the recipient and text, then tap Send yourself.")


def show_summary(data):
    guests = data.get("guests", [])
    tasks = data.get("tasks", [])
    print("Wedding:", data.get("wedding", {}).get("title", "Wedding"))
    print("Guests:", len(guests), "| Confirmed:", sum(g.get("rsvp") == "confirmed" for g in guests))
    print("Events:", len(data.get("events", [])))
    print("Open tasks:", sum(t.get("status") != "done" for t in tasks))
    for t in tasks:
        if t.get("status") != "done":
            print(" -", t.get("title", "Task"), "| due", t.get("due", "TBD"))


def circles_check():
    """Optional read-only connectivity check; no tokens written to disk."""
    token = os.environ.get("CIRCLES_KEY", "")
    if not token:
        raise ValueError("Set CIRCLES_KEY in your shell after connecting Circles. Never commit it.")
    req = Request(CIRCLES_API + "/allowed_chats", headers={"Authorization": "Bearer " + token})
    with urlopen(req, timeout=15) as resp:
        result = json.load(resp)
    for chat in result.get("chats", []):
        print(chat.get("name", "Unnamed"), "|", chat.get("access", "unknown"))
    print("Circles read-only check complete. No messages sent.")


def dashboard_html(data):
    rows = []
    for g in data.get("guests", []):
        ident, name = str(g.get("id", "")), escape(str(g.get("name", "Guest")))
        msg = draft(data, ident)
        phone = g.get("phone", "").strip()
        if phone:
            try:
                url = whatsapp_url(phone, msg)
                action = '<a target="_blank" rel="noopener noreferrer" href="' + escape(url, quote=True) + '">Open WhatsApp draft</a>'
            except ValueError:
                action = "Invalid phone"
        else:
            action = "Add phone locally to enable"
        rows.append("<tr><td>" + name + "</td><td>" + escape(str(g.get("rsvp", "pending"))) +
                    "</td><td>" + action + "</td></tr>")
    return (
        "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>Wedding Planning Agent</title><style>body{font:16px system-ui;max-width:850px;margin:40px auto;padding:0 20px}"
        "td,th{padding:12px;border-bottom:1px solid #ddd;text-align:left}table{width:100%;border-collapse:collapse}"
        "p{line-height:1.6}</style></head><body><h1>Wedding Planning Agent</h1>"
        "<p>Private, local-only dashboard. Links prefill WhatsApp; nothing is sent automatically.</p>"
        "<table><thead><tr><th>Guest</th><th>RSVP</th><th>Message</th></tr></thead><tbody>" +
        "".join(rows) + "</tbody></table><p>Review each message and recipient in WhatsApp before sending.</p></body></html>"
    )


def serve(data, port):
    html = dashboard_html(data).encode("utf-8")
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path not in ("/", "/index.html"):
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(html)
        def log_message(self, fmt, *args):
            pass
    url = "http://127.0.0.1:" + str(port)
    with ThreadingHTTPServer(("127.0.0.1", port), Handler) as server:
        print("Private dashboard:", url, "(Ctrl+C to stop)")
        webbrowser.open(url)
        server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Local-first, privacy-conscious wedding planner")
    parser.add_argument("command", choices=(
        "summary", "guests", "tasks", "draft", "whatsapp", "instinct",
        "instinct-rules", "dashboard", "circles-check"))
    parser.add_argument("guest_id", nargs="?")
    parser.add_argument("--kind", choices=KINDS, default="rsvp")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.command == "circles-check":
        circles_check()
        return
    data = load_data()
    if args.command == "summary":
        show_summary(data)
    elif args.command == "guests":
        for g in data.get("guests", []):
            print(g.get("id"), "|", g.get("name"), "| RSVP:", g.get("rsvp", "pending"),
                  "| travel:", g.get("travel_status", "unknown"))
    elif args.command == "tasks":
        for t in data.get("tasks", []):
            print(t.get("due", "TBD"), "|", t.get("status", "open"), "|",
                  t.get("title", "Task"), "|", t.get("owner", "Unassigned"))
    elif args.command == "instinct-rules":
        open_instinct(data, RULES)
    elif args.command == "dashboard":
        if not 1 <= args.port <= 65535:
            parser.error("Port must be 1–65535")
        serve(data, args.port)
    else:
        if not args.guest_id:
            parser.error("This command requires a guest_id")
        if args.command == "draft":
            print(draft(data, args.guest_id, args.kind))
        elif args.command == "whatsapp":
            g = guest_by_id(data, args.guest_id)
            webbrowser.open(whatsapp_url(g.get("phone", ""), draft(data, args.guest_id, args.kind)))
            print("Opened prefilled WhatsApp message. No message has been sent.")
        else:
            open_instinct(data, instinct_message(data, args.guest_id, args.kind))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        raise SystemExit("Error: " + str(error))
