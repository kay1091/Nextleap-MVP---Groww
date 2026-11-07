# SIP Performance Explainer — first PM project MVP

This is a small educational experiment, not a Groww feature. It uses xAI/Grok only to interpret a user's question into one of four approved educational topics. **Grok does not generate financial advice or final answers.** The server enforces a schema/confidence check, independent keyword mismatch check, validates example arithmetic, and renders a pre-reviewed explanation. When checks fail or no API key is configured, it shows a visible fallback and a non-AI glossary.

## Run locally

```bash
pip install -r requirements.txt pytest
streamlit run app.py
pytest -q
```

Set `XAI_API_KEY` in your environment or in Streamlit Cloud secrets. Optionally set `XAI_MODEL` (default `grok-4-1-fast-reasoning`; verify model availability and billing in your xAI account). Do **not** commit keys. A key is mandatory for the live AI path; without one only the glossary and fallback work. User questions are sent to xAI for classification when configured; do not enter personal or account data.

## Deploy

1. Create a private or public GitHub repo with these files (not the secret key).
2. Deploy `app.py` on Streamlit Community Cloud.
3. Add `XAI_API_KEY="..."` in the Streamlit deployment's Secrets panel. Check that the configured model is available.
4. Open the public URL in a private/incognito browser and test one passing case and one unsupported question.
5. Record the URL and an execution screenshot in your assignment only after verification.

No public deployment or live xAI API call was executed in the creation environment.

## Evaluation and research limitations

`golden_set_review.csv` contains 20 **draft scenario cases**, NOT independently human-labelled gold data. A human researcher must fill `human_expected_topic`, run them through the deployed AI application, enter `ai_topic`, `gate`, and `reviewer_note`, calculate agreement, and document at least 2–3 corrections. Keep the Discovery Engine review-classification evaluation separate from this investor-facing intent evaluation. No scores are claimed until executed.

Three tests with actual participants should use the same comprehension scenario (before/after explanation), record whether they can correctly distinguish 1D/total returns, ask how they would independently verify confusing numbers, then compare against the non-AI glossary. No test participants or outcomes are claimed yet.

Research basis: corrected V3 log has three directly matching debriefs I01, I04, I06. Others are adjacent; the selected-segment five-interview requirement is not substantiated by those three alone. The live prototype measures educational comprehension, not 12-month retention. Do not interpret it as an investment recommendation.
