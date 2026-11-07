# Slide 7 — proposed (replace with actual deployment URL)

**I built a small explainer to help new SIP investors understand confusing returns**

I chose performance comprehension because three directly relevant interview accounts described confusion about early returns (I01/I04/I06). The working prototype lets someone ask about one-day change, overall returns, XIRR and comparison with lump-sum investing using fictional figures. Grok interprets the question; the app checks the classification and uses fixed, vetted explanations instead of letting AI generate financial guidance. If a check fails, the app tells the user it cannot answer reliably and offers a glossary.

The non-AI alternative is that same glossary. I need to check whether interpreting the question adds enough value to justify AI. No personalized recommendations, predictions or real account access.

Evidence limitations: only three directly matching interviews are documented; quality evaluation and public deployment must be completed separately.

# Slide 8 — testing framework (replace with observed results)

**I will test whether the explanation improves understanding, not whether it persuades users to keep investing**

Three eligible target users: first interpret hypothetical numbers unaided, then with glossary and the AI explainer. Observe whether they can distinguish one-day changes from a charge, explain the invested/current gap and understand XIRR limitations. Record AI pass/fallback, user mistakes, and feedback. Evaluate ~20 hand-reviewed scenarios independently for correct intent classification and abstention. Report failures and what changed after testing. This small usability test cannot prove better 12-month SIP continuation.
