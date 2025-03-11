import streamlit as st

st.set_page_config(
     layout="wide"
 )

st.title("Non-Elective Flow Virtual Hospital")
st.header("(work in progress)")

st.markdown("""
Welcome to the Non-Elective Flow Virtual Hospital. The Virtual Hospital is being
developed by the Data & Analytics (D&A) team at the Countess of Chester Hospital. 
The Virtual Hospital is intended to help understand the effect of different 
management strategies on ED admission delays (DTA waits) using a computer 
simulation. Please note that this is work in progress and please contact the D&A
 team with any questions or feedback.
""")

st.markdown("""
            
##### Example questions the Virtual Hospital can help with:
            
The Virtual Hospital can help with questions related to the flow and pathway of 
**admitted**, **non-elective**, **adult** patients.

* Given x beds, how far does admitted length of stay have to reduce to meet 
particular waiting time targets for those queuing in ED? (Evidence based target)
* If we open 15 beds but keep admitted length of stay the same, what is the 
impact on ED waiting times and the various targets? (Evidence for a particular 
management strategy)
* What is the optimum number of people to stream from ED to SDEC to minimise ED
waits for admission? (Evidence for a particular management strategy)
* How does increase demand impact ED waiting times if the bed base stays static? 
(Evidence for planning)
            
For some worked examples see the Examples page (under construction)

""")

st.markdown("""
##### How does the Virtual Hospital work?

Patients flow through the system as illustrated in the diagram below. 

*  Patients
enter the system when it is decided that they require admission (Decision To Admit).
This can be via the Emergency Department (ED), the Same Day Emergency
Care Department (SDEC) or via another route. Admission demand can be altered for each
of the 3 routes.
* Patients wait in ED, SDEC or other until there is a bed available. 
The <span style='color:#FF1493; font-weight:bold'> pink arrow </span>
represents the queue we are most interested in - these are the patients 
waiting in ED who are admitted.
* If a patient is waiting in ED for longer than the amount of time they were 
expected to stay in hospital (thereby receiving their treatment in ED) they are discharged from ED.
* When admitted to a bed a patient remains in that bed and the bed is unavailable
until they are discharged.
* The timepoints associated with each simulated patient (Decision To Admit,
Admission, Discharge) are logged and used to calculate waiting time metrics.
            
For more detail on how the model works see the 'More Information' page
""", unsafe_allow_html=True)

st.image("https://raw.githubusercontent.com/Countess-of-Chester-Hospital-NHS-FT/Non-Elective-Flow-Simulation/refs/heads/main/app/img/model_diagram.png")

st.markdown("""
##### How is the Virtual Hospital different to a real hospital?
            
*"All models are wrong, some are useful" George Box*

The Virtual Hospital is a simplified version of a real hospital, although some more
complexity may be built in in the future. It may differ 
from a real hospital in the following important ways. In the Virtual Hospital:

* There is no daily or weekly trend in when patients arrive.
* ED, SDEC and other routes are assumed to be open at all times.
* Patients can be discharged at any time of day/week.
* Any patient can occupy any bed.
* Beds are ready instantly for the next patient.
* The overall number of beds stays constant through the simulation.
            
This means that flow in the Virtual Hospital will always be **better** than flow in
the real system (queue times in ED will be worse in the real system than in the 
Virtual Hospital). 

However, the Virtual Hospital can therefore be used to provide a
best case scenario - if x beds, x demand and x los leads to 10 DTA breaches per day in the Virtual Hospital,
you would expect **at least** this many DTA breaches per day in the  real system with the
same parameters. And it can
still be used to help understand the relationships between beds, demand and los.
            
For more detail on model assumptions see the 'More Information' page
""", unsafe_allow_html=True)

