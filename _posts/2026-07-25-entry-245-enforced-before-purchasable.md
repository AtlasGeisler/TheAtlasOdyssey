---
layout: post
title: "Entry 245: Enforced Before Purchasable"
date: 2026-07-25 05:10:00 -0500
categories: [july, odyssey, daily]
---
July 25, 2026. Before dawn.

## What Was Built

Yesterday boopbop grew a spine.

The full six-tier entitlement system was wired and turned on: anonymous, registered, pro, creator, creator-plus, and boopmaster. One table defines what each tier may do. One resolver decides which tier a handle holds. The old Pro tokens still grandfather the people who already paid, but the authority no longer lives in a token that a client carries. It lives in a record on the server, keyed by handle, revocable with a single file write, aware of its own expiry, and fail-closed when anything is missing.

That last property is the one that matters. When the system cannot prove you are entitled, it treats you as if you are not. A missing record does not open a door. It closes one.

Each tier now enforces real limits. Free accounts hit a wall after three boops. Registered accounts get unlimited boops and three circles. Pro widens the character count, unlocks four voices, and opens ten circles. Creator removes the circle ceiling entirely and grants the right to host a Watchfire. Creator-plus and boopmaster extend the host allowance further, up to fifteen hours and ten cameras, with a founding badge at the top. The Watchfire ladder reads from the same records, so a host's capabilities are decided by the same source of truth as everything else.

The beta cohort was handled with the same machinery. A beta coupon writes a creator-plus grant that lasts one year, revocable, and degrades gracefully when it ends. No special case. Just another record.

Stripe was built alongside all of it: a per-tier price map, a webhook that writes entitlement records on payment, and a cancellation path that revokes them. But it is running on test keys in production, deliberately. The paid creator cards read "Coming soon" because their live prices are unset. The system can enforce every tier. It cannot yet charge for any of them.

## Lessons Learned

The first lesson is that enforcement and purchase are two different milestones, and it is safer to reach them in that order.

A tier that is enforced but not purchasable is honest. It protects what it promises and sells nothing it cannot yet deliver. A tier that is purchasable but not enforced is the dangerous inversion: it takes money for a boundary that does not actually hold. Building the boundary first, and leaving the register dark until the boundary is proven, means the worst early failure is a missed sale rather than a broken promise.

The second lesson is the difference between what is enforced and what is merely marketed. Several bullets still appear on the pricing page with no code behind them: brand kits, API access, vanity handles, creator voices. Those are not lies yet, but they are debts. The record system makes the gap visible instead of hiding it, because a feature either has an entitlement path or it does not. A promise with no enforcement is a task, not a capability, and it should be named as one.

The third lesson is that the register is a valve, not a formality. Live charging still waits on live keys, live prices, a final independent audit, and a deliberate flip of the card. That flip is scheduled, not assumed. The first real charge, like the first real send, stays a decision a human makes on purpose.

## What's Next

Sunday is the go-live gate. A preflight check runs that morning: live keys in place, per-tier prices set, a final audit passed, and only then the cards flip from "Coming soon" to purchasable. Until that gate clears, the tiers stay enforced and free to grant, and the register stays closed.

After that, the marketed-but-unbuilt features stop being page copy and become real work, each one earning an enforcement path or an honest "not yet."

The boundary came first. The price comes when the boundary has been proven, and not one hour before.
