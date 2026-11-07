from engine import calculate, local_hint, evaluate

def test_calculation():
 x=calculate(18000,16200)
 assert x=={'difference':-1800,'simple_pct':-10.0}
 assert calculate(0,100) is None

def test_unsafe_fallback():
 x=evaluate('Should I buy this stock?',18000,16000)
 assert x.gate=='Fallback'

def test_no_key_fallback():
 x=evaluate('Explain XIRR',18000,16000)
 assert x.gate=='Fallback'

def test_core_terms():
 assert local_hint('What is XIRR?')=='xirr'
 assert local_hint('Is my 1D return a charge today?')=='daily_vs_total'
 assert local_hint('Should I stop my SIP?')=='unknown'

def test_gate_blocks_bad_model(monkeypatch):
 import engine
 monkeypatch.setattr(engine,'classify_xai',lambda *args: ('xirr','fake'))
 x=evaluate('Why is my 1D return negative?',18000,16000,api_key='dummy')
 assert x.gate=='Fallback'

def test_pass_only_approved_template(monkeypatch):
 import engine
 monkeypatch.setattr(engine,'classify_xai',lambda *args: ('daily_vs_total','fake'))
 x=evaluate('Why is my 1D return negative?',18000,16200,api_key='dummy')
 assert x.gate=='Pass'
 assert '−' not in x.explanation or 'One-day' in x.explanation
