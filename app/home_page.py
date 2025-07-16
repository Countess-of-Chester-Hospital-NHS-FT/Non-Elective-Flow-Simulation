import streamlit as st

st.set_page_config(
     layout="wide"
 )

st.title("Non-Elective Flow Virtual Hospital")
st.header("(v0.0.0)")

st.markdown("""
Welcome to the Non-Elective Flow Virtual Hospital. The Virtual Hospital is being
developed by the Data & Analytics (D&A) team at the Countess of Chester Hospital. 
The Virtual Hospital is intended to help understand the effect of different 
management strategies on ED admission delays (DTA waits) using a computer 
simulation. Please note the limitations below and that this work is at an early stage. Please contact the D&A
team with any questions or feedback, or raise an issue via GitHub.
""")

st.markdown("""
            
##### Example questions the Virtual Hospital can help with:
            
The Virtual Hospital can help with questions related to the flow and pathway of 
**admitted**, **non-elective**, **adult** patients. This can help provide evidence for particular management strategies.

Given a starting scenario where x daily 12hr breaches are occurring, what happens to breach numbers:
* If we open x beds but keep admitted length of stay and demand the same?
* If we open x beds and reduce inpatient length of stay?
* If daily demand increases by x and beds and inpatient length of stay remain constant

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
* The longer a patient is waiting in ED, the more likely they are to be discharged from ED rather than admitted
(reneging).
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

The Virtual Hospital is a very simplified version of a real hospital, although some more
complexity may be built in in the future. It differs
from a real hospital in the following important ways. In the Virtual Hospital:

* Beds are the only constraint 
* There is no daily or weekly trend in when patients arrive.
* ED, SDEC and other routes are assumed to be open at all times.
* Patients can be discharged at any time of day/week.
* Any patient can occupy any bed.
* Beds are ready instantly for the next patient.
* The overall number of beds stays constant through the simulation.
            
This means that flow in the Virtual Hospital will always be **better** than flow in
the real system (queue times in ED will be worse in the real system than in the 
Virtual Hospital with the same inputs). 

However, the Virtual Hospital can therefore be used to provide a
best case scenario - if x beds, x demand and x los leads to 10 DTA breaches per day in the Virtual Hospital,
you would expect **at least** this many DTA breaches per day in the  real system with the
same parameters. It can also
be used to help understand the relationships between beds, demand and los and provide evidence about the 
required bedbase in the absence of other constraints.
            
For more detail on model assumptions see the 'More Information' page
""", unsafe_allow_html=True)

