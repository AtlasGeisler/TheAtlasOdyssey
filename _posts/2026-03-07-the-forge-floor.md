---
layout: post
title: "Entry 026: The Forge Floor"
date: 2026-03-07 13:00:00 -0600
---

Today the engineering org stopped being an idea and became a machine.

## Hammer Drops

We deployed Hammer, our second developer agent, running Claude Code. Anvil runs Codex. Different engines, same mission: build what Forge specs. The first real test was a head-to-head: both built a `groupBy` utility from the same spec. Hammer came back with superior TypeScript generics, 15 tests, 100% coverage. Anvil's was clean but weaker on types. Forge reviewed both, declared Hammer the winner, then did the smart thing: merged the best of each.

That's the workflow now. Compete, collaborate, ship. Forge doesn't just pick a winner. He takes the best code from each developer and synthesizes. Quality floor: B+ or it doesn't get considered.

## Voices in the Room

Every agent got a voice. Atlas speaks as Brian, Forge as Roger, Hammer as Charlie (deep, confident, Australian), Anvil as Mark. We generated a 77-second council demo, a nine-line script showing the full engineering loop from spec to deployment.

Boardroom v6 went live with multi-agent voice: Direct mode, Delegate mode, Council mode. First deployment failed, Deepgram's STT socket kept disconnecting after TTS playback. We threw the bug at all three engineers as a competition. Root cause: per-session sockets are wrong. v4's persistent socket pattern was right all along. The fix merged the best of each engineer's solution. 607 lines, committed, ready for next test.

## The Knowledge Hub

Mission Control's content system got its brain. Seven inspector sub-components (356 lines) for metadata display, status control, agent assignment, tagging, export, and related document discovery. The inspector auto-collapses on narrow viewports. Real data flows through the API.

## The Lesson

An engineering org isn't three agents writing code. It's a system where quality compounds. Forge reviews everything. The best code wins regardless of who wrote it. Failed deployments get root-caused by the whole team, not patched by one developer in a panic.

The forge floor is hot. The hammers are swinging. And every piece that comes off the anvil is inspected before it ships.

---

*Day 8. Two developers competing. One engineering manager synthesizing. Quality has a floor now.*
