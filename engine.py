"""Constrained AI intent classification and deterministic financial-metric education.
No live portfolio connection, fund recommendations, return promises, or transaction execution.
"""
from __future__ import annotations
import json, math, os, re
from dataclasses import dataclass
from typing import Optional

TOPICS = ('daily_vs_total', 'invested_vs_current', 'xirr', 'sip_vs_lumpsum', 'unknown')
FACTS = {
 'daily_vs_total': ('One-day change vs overall return', 'One-day change describes the change in value over the latest displayed day. Overall gain or loss compares the current value with money invested (subject to the app’s displayed definitions). A negative one-day change can appear alongside a positive overall gain. A market-value change is not, by itself, evidence of a fee or withdrawal.'),
 'invested_vs_current': ('Invested amount vs current value', 'Invested amount is the total contribution amount in this example. Current value is what those holdings are worth at the specified valuation time. Their difference is an illustrative gain or loss, not proof that money was withdrawn.'),
 'xirr': ('Understanding XIRR', 'XIRR is an annualized money-weighted return calculation that accounts for the timing and size of cash flows. It is different from the simple percentage change between total contributions and current value. Accurate XIRR needs dated cash flows and a valuation date; we do not estimate it from two totals.'),
 'sip_vs_lumpsum': ('Comparing SIP returns fairly', 'A SIP contributes on multiple dates, so each instalment has a different holding period. A one-time stock purchase or a published index return may cover a different time window and risk exposure. Compare cash-flow dates, measurement periods and risk before interpreting the difference; the figures alone do not tell you which investment to choose.'),
}

@dataclass
class Result:
 topic: str
 gate: str
 explanation: str
 reason: str
 source: str


def safe_amount(x: float) -> bool:
 return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) and 0 <= x <= 1_000_000_000

def calculate(invested: float, current: float) -> Optional[dict]:
 if not (safe_amount(invested) and safe_amount(current)) or invested <= 0:
  return None
 delta=round(current-invested,2)
 pct=round((current-invested)/invested*100,2)
 return {'difference':delta,'simple_pct':pct}

def local_hint(q: str) -> str:
 q=q.lower()
 if any(w in q for w in ('will it recover','which fund','should i buy','should i sell','should i stop','should i continue','recommend','guarantee','predict','next month','best fund','invest now')):
  return 'unknown'
 if any(w in q for w in ('xirr','annualized','annualised','money weighted')): return 'xirr'
 if any(w in q for w in ('stock returns','lump sum','lumpsum','compare with','versus stock','vs stock','sip vs')): return 'sip_vs_lumpsum'
 if any(w in q for w in ('1d','one day','daily return','daily change','yesterday','deducted today','charge today')): return 'daily_vs_total'
 if any(w in q for w in ('invested','current value','profit','loss','total return','my returns','value down','negative returns')): return 'invested_vs_current'
 return 'unknown'

SYSTEM = '''You classify a user's question about *understanding* SIP performance for an educational app. Output exactly one JSON object, without markdown: {"topic":"daily_vs_total|invested_vs_current|xirr|sip_vs_lumpsum|unknown","confidence":0.0}. Do not write a user-facing explanation. Use unknown for investment advice, predictions, specific fund/stock decisions, personal tax/legal advice, or unverifiable account details. Classify based only on the supplied question. You have no live account data.''' 

import os
import requests

api_key = os.environ.get("OPENROUTER_API_KEY")
model = os.environ.get("OPENROUTER_MODEL", "openrouter/free")

response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json={
        "model": model,
        "messages": messages,  # Keep existing classification instructions
        "temperature": 0,
        "max_tokens": 300,
    },
    timeout=30,
)

response.raise_for_status()
result = response.json()
content = result["choices"][0]["message"]["content"]

def evaluate(question: str, invested:float=18000, current:float=16200, api_key:Optional[str]=None, model:str='grok-4-1-fast-reasoning') -> Result:
 question=question.strip()[:1500]
 if len(question)<7: return Result('unknown','Fallback','Please enter a complete question about SIP performance.','Question too short','none')
 hint=local_hint(question)
 if hint=='unknown' and any(x in question.lower() for x in ('should','recommend','guarantee','predict','will it recover','next month','best fund','invest now','buy','sell')):
  return Result('unknown','Fallback','I can explain SIP performance numbers, but I cannot recommend investments or predict returns. Please check official product information or consult an appropriately qualified professional for personal decisions.','Outside educational scope','guardrail')
 if not (safe_amount(invested) and safe_amount(current)):
  return Result('unknown','Fallback','The amounts entered are not valid. Please use non-negative finite amounts.','Invalid numbers','input validation')
 if not api_key:
  return Result('unknown','Fallback','Live AI classification is not connected. You can still use the static explanations below.','No xAI API key configured','offline')
 topic, why=classify_xai(question,api_key,model)
 if topic is None: return Result('unknown','Fallback','I could not verify the meaning of that question reliably. Please use one of the static metric explanations below.','Rejected: '+why,'AI classification')
 if topic=='unknown': return Result('unknown','Fallback','I can explain SIP performance metrics, but I cannot verify account details, recommend trades or predict returns. Please check the platform’s official information for account-specific issues.','AI identified unsupported intent','AI classification')
 # independent intent agreement: when a strong unambiguous deterministic cue is present, never trust a contradictory AI label.
 if hint!='unknown' and hint!=topic:
  return Result('unknown','Fallback','The AI interpretation did not agree with the basic terminology checks. Please choose a metric from the glossary below.','AI topic disagreed with deterministic check','cross-check')
 title, description=FACTS[topic]
 numbers=calculate(invested,current)
 if numbers and topic in ('daily_vs_total','invested_vs_current'):
  sign='higher' if numbers['difference']>=0 else 'lower'
  description += f" In the illustrative figures entered, current value is ₹{abs(numbers['difference']):,.2f} {sign} than invested amount (simple difference {numbers['simple_pct']:+.2f}%). This is not an XIRR calculation or an account statement."
 return Result(topic,'Pass',description,'AI intent passed; response rendered from reviewed educational templates and validated arithmetic','xAI classification + deterministic content')
