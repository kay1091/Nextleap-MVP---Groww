# User test plan — three target users

Research question: Does the AI-based question interpreter help first-time SIP investors understand what performance figures mean more clearly than a standard glossary?

Recruitment: target first-time Groww mutual fund SIP investors in their first 12 months who actively check performance. Record consent and anonymous ID. Do not ask for screenshots, PAN, personal account details or holdings.

## Protocol (10–15 minutes each)

1. **Before prototype:** Present the same hypothetical statement to each user: 'Invested ₹18,000, current value ₹16,200. One-day change −₹450. Is −₹450 a bank charge? What does the total difference represent?' Ask participant to explain in their own words. Record pre-test correctness (0, 1, or 2 points for two concepts).
2. **Non-AI baseline:** Let participant read the static glossary for 60 seconds. Ask if they can answer the two concepts; record what was unclear.
3. **AI feature:** With valid API key, have them type their question. Record whether gate passed or fell back, whether they could interpret the explanation, any hesitation or incorrect information.
4. **Post-test:** Ask again without showing the interface. Check whether they can (a) identify one-day market-value change rather than fee and (b) compute the simple invested/current difference without treating it as XIRR. Ask how helpful the AI was versus glossary (1–5), and why.
5. **Safety:** Ask a question that requests a fund recommendation. Observe whether it safely refuses.

Participant table:

| ID | First-year and active checker? | Before (0–2) | Glossary comprehension (0–2) | AI comprehension (0–2) | AI gate | Preference & explanation | Observed issue | Change proposed |
|----|-------------------------------|--------------|------------------------------|------------------------|---------|--------------------------|----------------|-----------------|
| P01 | | | | | | | | |
| P02 | | | | | | | | |
| P03 | | | | | | | | |

**Never invent test outcomes.** With n=3 this supports only directional usability learning, not proven 12-month continuation improvement. Compare user improvement and whether AI actually outperformed baseline; revise or reject feature if not.
