# Refusal and hold responses (brand voice)

These are the patient-facing and referrer-facing messages used when a hard
guardrail fires. They follow the United Endodontics voice: warm, plain, and
clear about the next step. They never use em dashes or en dashes.

The runtime copies of these messages live in the guardrail policy at
`src/dental_harness/guardrails/policy.yaml` under `responses`, so they can be
reviewed and changed as data. Keep this file and the policy in step. This file
is the canonical brand reference and is the place to work out wording.

## Formatting palette (United Endodontics)

For any rendered or HTML output of these messages, use the brand palette:

- Near-black `#1A1A1A` for text
- Deep forest green `#1E3A28` for headers
- Primary green `#3A7D44` for the next-step action or link
- Soft sage `#7CB68A` for secondary accents
- Warm cream `#F5F0E8` for the background or card surface

## Clinical-advice refusal

> I am not able to give clinical advice, including a diagnosis, a treatment
> recommendation, or a prognosis. Your health and safety matter, so I am
> routing this to a licensed clinician who can review it and follow up with you
> directly.

Use when someone asks the assistant to diagnose, recommend or judge treatment,
estimate a prognosis, or weigh in on symptoms or medication. Always pair the
refusal with a real handoff to a clinician.

## Out-of-scope refusal

> I am not able to take that action. It is outside what this assistant is set
> up to do. I can help with scheduling, referrals, insurance and billing
> questions, recall, and patient education. For anything else, I will pass this
> to a member of our team.

Use when a request falls outside the allowlisted actions.

## PHI egress hold

> I am holding this because it would send patient-identifying information in a
> way that is not authorized for this action. A member of our team will review
> it before anything goes out.

Use when an outbound message would carry patient-identifying data without
authorization for that action.

## Approval hold

> This is ready, and I have held it for a team member to review and approve
> before it is sent. Nothing has been sent yet.

Use for any outbound message or state-changing action that is waiting on human
approval.
