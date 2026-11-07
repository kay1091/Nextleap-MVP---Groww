
"""
Groww SIP Performance Explainer — AI Classification Engine

Educational student PM prototype.
Not affiliated with Groww. Not investment advice.

AI identifies the topic of the user's question.
Only reviewed, predefined educational explanations are displayed.

Provider: OpenRouter
"""

from __future__ import annotations

import json
import logging
import math
import re
from dataclasses import dataclass
from typing import Optional

import requests


# ---------------------------------------------------------
# 1. Supported educational topics
# ---------------------------------------------------------

TOPICS = (
    "daily_vs_total",
    "invested_vs_current",
    "xirr",
    "sip_vs_lumpsum",
    "unknown",
)

FACTS = {
    "daily_vs_total": (
        "One-day change vs overall return",
        "One-day change describes how an investment's displayed "
        "market value changed over the latest reported day. "
        "Overall gain or loss compares current value with the "
        "amount invested, subject to the platform's definitions. "
        "A negative one-day change can appear alongside a positive "
        "overall gain. A change in market value is not, by itself, "
        "evidence of a fee or withdrawal."
    ),

    "invested_vs_current": (
        "Invested amount vs current value",
        "Invested amount is the total contribution amount in this "
        "example. Current value is what those holdings are worth "
        "at the specified valuation time. The difference is an "
        "illustrative gain or loss. A lower current value does "
        "not automatically mean money was withdrawn."
    ),

    "xirr": (
        "Understanding XIRR",
        "XIRR is an annualized money-weighted return calculation "
        "that accounts for the dates and amounts of investment "
        "cash flows. It differs from a simple percentage change "
        "between invested amount and current value. "
        "Calculating XIRR requires dated cash flows and a "
        "valuation date. This prototype does not estimate XIRR "
        "from two amounts."
    ),

    "sip_vs_lumpsum": (
        "Comparing SIP returns fairly",
        "With a SIP, contributions happen on different dates, "
        "so each instalment has a different holding period. "
        "A single stock purchase or an index return may cover "
        "a different period and involve different risks. "
        "Meaningful comparisons need aligned time periods, "
        "cash-flow dates and an understanding of the risks. "
        "These figures alone cannot tell you which investment "
        "is suitable."
    ),
}


# ---------------------------------------------------------
# 2. Result returned to Streamlit
# ---------------------------------------------------------

@dataclass
class Result:
    topic: str
    gate: str
    explanation: str
    reason: str
    source: str


# ---------------------------------------------------------
# 3. Validate and calculate illustrative figures
# ---------------------------------------------------------

def safe_amount(value: float) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and 0 <= value <= 1_000_000_000
    )


def calculate(
    invested: float,
    current: float,
) -> Optional[dict]:

    if not (
        safe_amount(invested)
        and safe_amount(current)
    ):
        return None

    if invested <= 0:
        return None

    difference = round(current - invested, 2)

    simple_pct = round(
        (current - invested) / invested * 100,
        2,
    )

    return {
        "difference": difference,
        "simple_pct": simple_pct,
    }


# ---------------------------------------------------------
# 4. Deterministic intent checks
# ---------------------------------------------------------

UNSUPPORTED_PATTERNS = (
    r"\bshould\s+i\s+(buy|sell|stop|continue|invest|redeem|switch)\b",
    r"\bwhich\s+(fund|stock|sip)\b",
    r"\bwhat\s+(fund|stock)\s+should\s+i\b",
    r"\brecommend\b",
    r"\bguarantee\b",
    r"\bpredict\b",
    r"\bwill\s+it\s+recover\b",
    r"\bnext\s+month.*\b(return|recover|profit|gain)\b",
    r"\bbest\s+(fund|stock)\b",
    r"\binvest\s+now\b",
    r"\bwhen\s+should\s+i\s+(buy|sell|invest|exit)\b",
)

def unsupported_request(question: str) -> bool:
    text = question.lower()

    return any(
        re.search(pattern, text)
        for pattern in UNSUPPORTED_PATTERNS
    )


def local_hint(question: str) -> str:
    """Conservative terminology-based topic suggestion."""

    q = question.lower()

    if unsupported_request(q):
        return "unknown"

    if any(term in q for term in (
        "xirr",
        "annualized",
        "annualised",
        "money weighted",
        "money-weighted",
    )):
        return "xirr"

    if any(term in q for term in (
        "stock returns",
        "lump sum",
        "lumpsum",
        "compare with",
        "versus stock",
        "vs stock",
        "sip vs",
    )):
        return "sip_vs_lumpsum"

    if any(term in q for term in (
        "1d",
        "one day",
        "one-day",
        "daily return",
        "daily change",
        "yesterday",
        "deducted today",
        "charge today",
    )):
        return "daily_vs_total"

    if any(term in q for term in (
        "invested",
        "current value",
        "profit",
        "loss",
        "total return",
        "my returns",
        "value down",
        "negative returns",
    )):
        return "invested_vs_current"

    return "unknown"


# ---------------------------------------------------------
# 5. AI classification prompt
# ---------------------------------------------------------

SYSTEM = """
You classify questions for an educational mutual fund
SIP performance explanation tool used in India.

Return exactly one valid JSON object.

Required schema:
{
  "topic": "daily_vs_total",
  "confidence": 0.95
}

Allowed topics:
- daily_vs_total
- invested_vs_current
- xirr
- sip_vs_lumpsum
- unknown

Definitions:

daily_vs_total:
Questions about one-day returns, daily changes,
daily negative values compared with positive total returns,
or whether a displayed daily market change is a deduction.

invested_vs_current:
Questions about money invested, current market value,
simple gains or losses, and why market value changes.

xirr:
Questions about XIRR, annualized money-weighted returns,
or how dated contributions affect return calculations.

sip_vs_lumpsum:
Questions comparing SIP returns with lump-sum investments,
stocks or published index returns across different periods.

unknown:
Investment recommendations, personalized advice,
predictions, guaranteed returns, account-specific charges,
personal tax or legal advice, or questions outside scope.

Rules:
1. Classify only the user's question.
2. Do not provide financial advice.
3. Do not produce a user-facing explanation.
4. Do not invent account information.
5. Return only the JSON object.
6. Do not use markdown or code fences.
7. Confidence must be a number between 0 and 1.
8. If intent is unclear, choose unknown.
"""


# ---------------------------------------------------------
# 6. OpenRouter API integration
# ---------------------------------------------------------

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

DEFAULT_MODEL = "openrouter/free"

MIN_CONFIDENCE = 0.70


def classify_openrouter(
    question: str,
    api_key: str,
    model: str = DEFAULT_MODEL,
) -> tuple[Optional[str], str]:

    if not api_key or not api_key.strip():
        return None, "OpenRouter API key missing"

    if not isinstance(model, str) or not model.strip():
        model = DEFAULT_MODEL

    messages = [
        {
            "role": "system",
            "content": SYSTEM,
        },
        {
            "role": "user",
            "content": question,
        },
    ]

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {api_key.strip()}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": 0,
                "max_tokens": 400,
            },
            timeout=40,
        )

        
if not response.ok:
    try:
        error_data = response.json().get("error", {})
        error_code = error_data.get("code", response.status_code)
        error_type = error_data.get("metadata", {}).get("error_type", "unknown")
        error_message = str(error_data.get("message", "No details"))

        # Keep diagnostics short; never expose API credentials.
        logging.error(
            "OpenRouter HTTP %s | Code: %s | Type: %s | Message: %s",
            response.status_code,
            error_code,
            error_type,
            error_message[:250],
        )

        return None, f"OpenRouter HTTP {response.status_code}"

    except (ValueError, AttributeError, TypeError):
        logging.error(
            "OpenRouter HTTP %s | Could not parse error",
            response.status_code,
        )
        return None, f"OpenRouter HTTP {response.status_code}"


        payload = response.json()

        choices = payload.get("choices", [])

        if not choices:
            return None, "Empty AI response"

        message = choices[0].get("message", {})

        content = message.get("content")

        if not isinstance(content, str):
            return None, "Invalid AI response content"

        content = content.strip()

        # Some models wrap their JSON output in code fences.
        # Remove only surrounding fences, not arbitrary text.
        if content.startswith("```"):
            content = re.sub(
                r"^```(?:json)?\s*",
                "",
                content,
                flags=re.IGNORECASE,
            )
            content = re.sub(
                r"\s*```$",
                "",
                content,
            )

        classification = json.loads(content.strip())

        if not isinstance(classification, dict):
            return None, "Invalid classification object"

        topic = classification.get("topic")
        confidence = classification.get("confidence")

        if topic not in TOPICS:
            return None, "Unsupported AI topic"

        if (
            isinstance(confidence, bool)
            or not isinstance(confidence, (int, float))
            or not math.isfinite(confidence)
            or confidence < MIN_CONFIDENCE
            or confidence > 1
        ):
            return None, "Invalid or low AI confidence"

        return topic, "Valid AI classification"

    except requests.Timeout:
        logging.warning("OpenRouter request timed out")
        return None, "AI request timed out"

    except requests.RequestException as exc:
        logging.error(
            "OpenRouter network error: %s",
            type(exc).__name__,
        )
        return None, "AI network request failed"

    except (
        ValueError,
        KeyError,
        IndexError,
        TypeError,
        AttributeError,
    ) as exc:

        logging.error(
            "OpenRouter response validation failed: %s",
            type(exc).__name__,
        )

        return None, "Invalid AI response format"


# ---------------------------------------------------------
# 7. Quality-gated evaluation
# ---------------------------------------------------------

def evaluate(
    question: str,
    invested: float = 18000,
    current: float = 16200,
    api_key: Optional[str] = None,
    model: str = DEFAULT_MODEL,
) -> Result:

    if not isinstance(question, str):
        return Result(
            "unknown",
            "Fallback",
            "Please enter a question about SIP performance.",
            "Invalid question",
            "input validation",
        )

    question = question.strip()[:1500]

    if len(question) < 7:
        return Result(
            "unknown",
            "Fallback",
            "Please enter a complete question about SIP performance.",
            "Question too short",
            "input validation",
        )

    # Prevent unsupported financial advice requests from
    # reaching the model.
    if unsupported_request(question):
        return Result(
            "unknown",
            "Fallback",
            "I can explain investment performance figures, "
            "but I cannot recommend investments or predict "
            "future returns. Please use official information "
            "or consult an appropriately qualified professional "
            "for personal investment decisions.",
            "Outside educational scope",
            "guardrail",
        )

    if not (
        safe_amount(invested)
        and safe_amount(current)
    ):
        return Result(
            "unknown",
            "Fallback",
            "Please enter valid non-negative amounts.",
            "Invalid amount",
            "input validation",
        )

    numbers = calculate(invested, current)

    if numbers is None:
        return Result(
            "unknown",
            "Fallback",
            "Enter an invested amount greater than zero.",
            "Cannot calculate from the values provided",
            "input validation",
        )

    if not api_key:
        return Result(
            "unknown",
            "Fallback",
            "Live AI is not connected. You can still use "
            "the static explanations below.",
            "No OpenRouter API key configured",
            "offline",
        )

    hint = local_hint(question)

    # AI is used to interpret the question, not to generate
    # unconstrained financial guidance.
    topic, reason = classify_openrouter(
        question=question,
        api_key=api_key,
        model=model,
    )

    if topic is None:
        return Result(
            "unknown",
            "Fallback",
            "I could not verify the meaning of that question "
            "reliably. Please use the static explanations below.",
            f"Rejected: {reason}",
            "AI classification",
        )

    if topic == "unknown":
        return Result(
            "unknown",
            "Fallback",
            "I can explain SIP performance metrics, but I "
            "cannot verify account-specific details, recommend "
            "trades or predict returns.",
            "AI identified unsupported or unclear intent",
            "AI classification",
        )

    # Deterministic cross-check:
    # If a clear keyword-based topic and the AI topic conflict,
    # reject rather than display a potentially irrelevant answer.
    if hint != "unknown" and hint != topic:
        return Result(
            "unknown",
            "Fallback",
            "The AI interpretation did not agree with the "
            "basic terminology checks. Please select a topic "
            "from the glossary below.",
            "AI topic disagreed with deterministic check",
            "cross-check",
        )

    title, description = FACTS[topic]

    if topic in (
        "daily_vs_total",
        "invested_vs_current",
    ):
        difference = numbers["difference"]
        percentage = numbers["simple_pct"]

        if difference > 0:
            direction = "higher"
        elif difference < 0:
            direction = "lower"
        else:
            direction = "equal to"

        if difference == 0:
            description += (
                " In this hypothetical example, current value "
                "equals the amount invested (0.00% simple change)."
            )
        else:
            description += (
                f" In this hypothetical example, current value "
                f"is ₹{abs(difference):,.2f} {direction} than "
                f"the amount invested "
                f"({percentage:+.2f}% simple change). "
                "This is not an XIRR calculation or an "
                "account statement."
            )

    return Result(
        topic=topic,
        gate="Pass",
        explanation=description,
        reason=(
            "AI topic classification passed the confidence "
            "threshold and deterministic terminology checks. "
            "The explanation uses reviewed educational content "
            "and validated arithmetic."
        ),
        source=(
            "OpenRouter classification + deterministic content"
        ),
    )
