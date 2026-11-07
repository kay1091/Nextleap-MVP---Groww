import os
import streamlit as st
from engine import evaluate, calculate, FACTS
st.set_page_config(page_title='SIP Performance Explainer',page_icon='📖',layout='centered')
st.title('SIP Performance Explainer')
st.caption('A student PM prototype · Not affiliated with Groww · For education, not investment advice')
st.write('Confused by the returns on your SIP? Try a hypothetical example. No login, portfolio upload or personal information needed.')
with st.expander('What this prototype can and cannot do'):
 st.write('It can explain one-day change, invested/current values, XIRR and fair comparisons of SIP vs lump-sum returns. It cannot access your account, check charges, recommend funds, predict returns, or decide whether you should continue investing.')
with st.form('question'):
 q=st.text_area('What would you like to understand?',value='My 1D return is -₹450 but my total return is positive. Was ₹450 deducted as a charge?',height=110)
 c1,c2=st.columns(2)
 with c1: invested=st.number_input('Example amount invested (₹)',min_value=0.0,value=18000.0,step=500.0)
 with c2: current=st.number_input('Example current value (₹)',min_value=0.0,value=16200.0,step=500.0)
 go=st.form_submit_button('Explain these numbers',type='primary',use_container_width=True)
if go:
 key=os.environ.get('OPENROUTER_API_KEY')
 try: key=st.secrets.get('OPENROUTER_API_KEY',key)
 except Exception: pass
 model=os.environ.get('XAI_MODEL','grok-4-1-fast-reasoning')
 with st.spinner('Checking the explanation...'):
  r=evaluate(q,invested,current,key,model)
 if r.gate=='Pass':st.success('Quality gate: PASS — classified intent, verified topic and template, checked arithmetic')
 else:st.warning('Quality gate: FALLBACK — the AI explanation was not released')
 st.write(r.explanation)
 with st.expander('Why did the quality gate make this decision?'):
  st.write(f'Check: {r.reason}  |  Source: {r.source}  |  Topic: {r.topic}')
st.subheader('Non-AI comparison: metric glossary')
st.write('These explanations are available even when AI is offline. Compare which experience actually helps you more.')
for title,body in FACTS.values():
 with st.expander(title):st.write(body)
st.divider()
st.caption('Calculations use hypothetical values only. A change in market value does not by itself establish a cash withdrawal or charge. Validate account-specific figures with the official platform. Your question is sent to xAI for intent classification only when configured; do not enter identifying data.')
