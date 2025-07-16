# Non-Elective-Flow-Simulation

### Status
The first iteration of this project is complete and being maintained. This is a proof of concept model and may be developed further in future.

### About the project
#### Problem: 
Long waits for admission in ED are an issue at many acute trusts and can lead to poorer outcomes for patients. Lack of available beds are often a driver of long waiting times.
#### Management strategies: 
The strategies employed to tackle this problem are increasing the number of beds (by creation of escalation beds), trying to decrease discharge delays (reducing length of stay) or trying to reduce demand for admission. 
#### Key questions:
* Given x beds, how far does admitted length of stay have to reduce to meet particular waiting time targets for those queuing in ED? (Evidence based target)
* Given a starting scenario, if we open 15 beds but keep admitted length of stay the same, what is the impact on ED waiting times and the various targets? (Evidence for a particular management strategy)
* What is the maximum demand that can be sustained without queues occuring, given a fixed bed base and length of stay.
#### Outputs:
This repo contains a Discrete Event Simulation (DES) model (app/model.py), a user friendly streamlit app front-end (app) and a series of Quarto reports (docs). 

### References
* The app is published on [Streamlit Community Cloud](https://non-elective-flow-simulation-coch.streamlit.app/).
* This project was completed as part of the [HSMA Programme](https://hsma.co.uk/previous_projects/hsma_6/H6_6001_DES_modelling_non_elective_flow/index.html)

Note: Only simulated data are shared in this repository

### Project Structure

* **app**  This folder contains the code required to run the model as an app and deploy on Streamlit Community Cloud, run launch.py to run the app. **Model.py** contains the model code.
* **docs** This folder contains quarto documents which describe how the model handles length of stay and reneging behaviours, and also some quarto documents which describe model findings (results). Some of these documents use real system data so if running in an external organisation you will need to change the data source.
* **environment** This folder contains a .yml for recreating a conda environment and also requirements.in / requirements.txt files for using venv or other package managers. There is also another requirements.txt file in the app folder which is required for deployment on Streamlit Community cloud. For notes on use of environment files see [here](https://github.com/Countess-of-Chester-Hospital-NHS-FT/Python-Environment-Notes)

### Contributing
Contributions and identification of issues are welcomed. Feel free to raise an issue or post discussions.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/Feature`)
3. Commit your Changes (`git commit -m 'Add some Feature'`)
4. Push to the Branch (`git push origin feature/Feature`)
5. Open a Pull Request

### Acknowledgements
* This project was supported by the [HSMA programme](https://hsma.co.uk/)
* Particular thanks to [Sammi Rosser](https://github.com/Bergam0t) for developing the Vidigi animation package and help with resolving various issues.
