

"""
scouse_bot.py - an always-ready terminal comedy sidekick.

Type a word, a phrase or a bit of context and get a short Scouse,
observational-style bit back. Keeps a little recent history so it can
do callbacks to earlier jokes. Bring a smile to your day!

Commands:
  /reset   forget the conversation so far (fresh audience)
  /quit    exit (or Ctrl+C)

Setup:
  pip install anthropic
  export ANTHROPIC_API_KEY="sk-ant-..."   # or setx on Windows
"""

import sys
import anthropic

MODEL = "claude-sonnet-5"
MAX_HISTORY_TURNS = 6   # how many recent exchanges to keep for callbacks

STYLE = """You are a stand-up comic with a warm, Scouse, observational style:
self-deprecating, storytelling-driven, exasperated by family life and
everyday absurdities, big on vivid physical description and escalating
tangents that land on a punchline. Take whatever the user types - a single
word, a situation, a moan about their day - and reply with a short, punchy
bit (3-6 sentences). Use Liverpool phrasing naturally, never as caricature.
Keep it good-natured. If it fits, call back to an earlier joke in the
conversation. Don't claim to be a real person and don't reuse any real
comedian's material. No preamble - just the bit."""

# ANSI colours (work in Git Bash / Windows Terminal)
YOU = "\033[96m"
BOT = "\033[93m"
DIM = "\033[90m"
RESET = "\033[0m"


def main():
    client = anthropic.Anthropic()
    history = []

    print(f"{DIM}Scouse bot ready. Type something (/reset, /quit).{RESET}\n")

    while True:
        try:
            text = input(f"{YOU}You: {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{DIM}Ta-ra!{RESET}")
            break

        if not text:
            continue
        if text.lower() in ("/quit", "/exit"):
            print(f"{DIM}Ta-ra!{RESET}")
            break
        if text.lower() == "/reset":
            history.clear()
            print(f"{DIM}Fresh crowd in.{RESET}\n")
            continue

        history.append({"role": "user", "content": text})
        print(f"{BOT}Bot: {RESET}", end="", flush=True)

        reply = ""
        try:
            with client.messages.stream(
                model=MODEL,
                max_tokens=400,
                system=STYLE,
                messages=history,
            ) as stream:
                for chunk in stream.text_stream:
                    print(chunk, end="", flush=True)
                    reply += chunk
            print("\n")
        except anthropic.APIError as e:
            print(f"\n{DIM}[API error: {e}]{RESET}\n")
            history.pop()          # drop the unanswered message
            continue

        history.append({"role": "assistant", "content": reply})
        # trim to the last N exchanges (each exchange = 2 messages)
        history[:] = history[-2 * MAX_HISTORY_TURNS:]


if __name__ == "__main__":
    sys.exit(main())
