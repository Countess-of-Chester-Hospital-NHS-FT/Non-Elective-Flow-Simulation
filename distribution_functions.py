import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from app.model import g, Trial
from scipy import stats
from scipy.stats import lognorm
from sim_tools.distributions import (Exponential, Lognormal, Uniform)

# Make list of theoretical distributions, constant mean but changing tail thickness
def make_lognormal_lists(mode_target, len):
    sigma_list = np.linspace(1.0, 1.5, len)

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

# Get co-ordinates for drawing each probability distribution
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

# visualise single or multiple traces (probability distributions)
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

#mean_list, std_list = make_lognormal_lists(18, 5)
#visualise_lognormal(mean_list, std_list)

## Compare theoretical distributions with each other as histograms
def visualise_lognormal_hist_list(mean_list, std_list, samples):
    if isinstance(mean_list, (int, float)):
        mean_list = [mean_list]
    if isinstance(std_list, (int, float)):
        std_list = [std_list]
    #fig = go.Figure()
    for i in range(len(mean_list)):
        fig = go.Figure()

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
#visualise_lognormal_hist_list(250, 374.1, 70000)



### Compare real distribution with a list of theoretical distributions
def hist_compare_real_model(filepath, mean_list, std_list):
    if isinstance(mean_list, (int, float)):
        mean_list = [mean_list]
    if isinstance(std_list, (int, float)):
        std_list = [std_list]
    csv = pd.read_csv(filepath)
    samples = csv.shape[0]
    fig = go.Figure()
    fig_list=[]
    for i in range(len(mean_list)):
        #print(f'Distribution {i}: Mean={mean_list[i]}, STD={std_list[i]}') 
        dist = Lognormal(mean_list[i], std_list[i], random_seed = 5)
        sample_list=[]
        for j in range(samples):
            sample = dist.sample()
            sample_list.append(sample)

        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=csv['LoSHrs'],
            name='Real',
            opacity=0.3
        ))
        #fig.update_traces(xbins=dict(start=0, end=2000, size=5))
        fig.add_trace(go.Histogram(
            x=sample_list,
            name = f'Modelled',
                    opacity=0.3
        ))
        fig.update_traces(xbins=dict(start=0, end=2000, size=24))
        fig.update_xaxes(range=[0, 2000])
        fig.update_layout(title = f'Real vs Modelled Dist {i}')
        #fig.show()
        fig_list.append(fig)

    return fig_list

#mean_list, std_list = make_lognormal_lists(16, 20)
#hist_compare_real_model("data/los_fy2425.csv", 201.85, 353.05)
#fig_list[12].show()
#fig_list = hist_compare_real_model("data/los_fy2425.csv", mean_list, std_list)
#fig_list[12].show()
#for i in range(len(fig_list)):
    #fig_list[i].show()

### mode function
def calc_mode(df, column, bin_size, min_bin_edge):
    vmax = df[f'{column}'].max()
    bins = np.arange(min_bin_edge, vmax + bin_size, bin_size)
    labels = [f"{int(b)}–{int(b + bin_size)}" for b in bins[:-1]]
    df['binned']= pd.cut(df[f'{column}'], bins=bins, labels=labels)
    mode_bin = df['binned'].mode()[0]
    #print(f"Mode of bins: {mode_bin}")
    return mode_bin

#csv=pd.read_csv("data/los_fy2425.csv")
#calc_mode(csv,'LoSHrs', 1, 0)
# dist = Lognormal(215, 355, random_seed = 5)
# sample_list=[]
# for j in range(70000):
#     sample = dist.sample()
#     sample_list.append(sample)




