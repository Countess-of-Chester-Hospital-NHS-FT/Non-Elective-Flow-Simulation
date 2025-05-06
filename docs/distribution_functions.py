import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from app.model import g, Trial
from scipy import stats
from scipy.stats import lognorm
from sim_tools.distributions import (Exponential, Lognormal, Uniform)

##### Visualising lognormal distributions - visualising a particular distribution
def make_lognormal_lists(mode_target, len):
    sigma_list = np.linspace(1.1, 1.4, len)

    meanlos_list = []
    std_list = []

    for i, sigma in enumerate(sigma_list):
    # Adjust mu to keep mode constant
        mu = np.log(mode_target) + sigma**2

        # Calculate mean and std (in real space) if needed
        mean = np.exp(mu + 0.5 * sigma**2)
        std = np.sqrt((np.exp(sigma**2) - 1) * np.exp(2*mu + sigma**2))

        #add them to their list
        meanlos_list.append(mean)
        std_list.append(std)

        median = np.exp(mu)
        mode = np.exp(mu - sigma**2)  # Should exactly equal mode_target
        
    return meanlos_list, std_list

def make_lognormal_trace(mean, std, x_min, x_max):
    # # # Convert to shape (s), location (loc), and scale parameters
    phi = np.sqrt(std**2 + mean**2)
    sigma = np.sqrt(np.log((phi**2) / (mean**2)))
    mu = np.log(mean**2 / phi)

    median = np.exp(mu)
    mode = np.exp(mu - sigma**2)

    x = np.linspace(x_min, x_max, 500)
    pdf = lognorm.pdf(x, s=sigma, scale=np.exp(mu))
    return(pdf, sigma, median, mode)

# visualise single or multiple traces
def visualise_lognormal(mean_list, std_list):
    if isinstance(mean_list, int) or isinstance(mean_list, float):
        mean_list = [mean_list]

    if isinstance(std_list, int) or isinstance(std_list, float):
        std_list = [std_list]

    # # Define a common x-axis range
    x_min = 0
    x_max = 800 #max(mean_list) + 4 * max(std_list)

    fig = go.Figure()
    
    for i in range(len(mean_list)):
        pdf, sigma, median, mode = make_lognormal_trace(mean_list[i], std_list[i], x_min, x_max)
        print(f'Distribution {i}: Mean={mean_list[i]}, STD={std_list[i]}, Median={median:.2f},' 
        f'Mode={mode:.2f}, Sigma={sigma:.2f}')
        fig.add_trace(go.Scatter(x=x, y=pdf, mode='lines', name=f'Mean {mean_list[i]}, STD {std_list[i]:.1f}'))

    fig.update_layout(showlegend=False)
    fig.show()

#visualise_lognormal(215, 374.1)

mean_list, std_list = make_lognormal_lists(18, 5)
#visualise_lognormal(mean_list, std_list)

def visualise_lognormal_hist_list(mean_list, std_list, samples):
    if isinstance(mean_list, (int, float)):
        mean_list = [mean_list]
    if isinstance(std_list, (int, float)):
        std_list = [std_list]
    fig = go.Figure()
    for i in range(len(mean_list)):

        dist = Lognormal(mean_list[i], std_list[i], random_seed = 5)
        sample_list=[]
        for j in range(samples):
            sample = dist.sample()
            sample_list.append(sample)

        print(f'Distribution {i}: Mean={mean_list[i]}, STD={std_list[i]}') 

        fig.add_trace(go.Histogram(
            x=sample_list,
            name = f'Dist {i}',
            opacity=0.3
        ))
        fig.update_traces(xbins=dict(start=0, end=2000, size=5))

    fig.update_xaxes(range=[0, 2000])
    fig.show()

#mean_list, std_list = make_lognormal_lists(18, 2)
visualise_lognormal_hist_list(250, 374.1, 70000)

### comparison histograms of real distribution with a list of distributions




