import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
#from app.model import g, Trial
from scipy import stats
from scipy.stats import lognorm
from sim_tools.distributions import (Exponential, Lognormal, Uniform, Normal)

# Make list of theoretical distributions, constant mean but changing tail thickness
def make_lognormal_lists(mode_target, len):
    sigma_list = np.linspace(1.2, 1.4, len)

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

def make_lognormal_trace2(mean, std, x_min, x_max):
    # Convert to shape (s), location (loc), and scale parameters
    phi = np.sqrt(std**2 + mean**2)
    sigma = np.sqrt(np.log((phi**2) / (mean**2)))
    mu = np.log(mean**2 / phi)

    # Distribution
    dist = lognorm(s=sigma, scale=np.exp(mu))

    # Main stats
    median = dist.median()
    mode = np.exp(mu - sigma**2)

    # Percentiles
    p25 = dist.ppf(0.25)
    p75 = dist.ppf(0.75)
    p95 = dist.ppf(0.95)

    # PDF
    x = np.linspace(x_min, x_max, 500)
    pdf = dist.pdf(x)

    return pdf, sigma, median, mode, p25, p75, p95

# visualise single or multiple traces (probability distributions)
def visualise_lognormal(mean_list, std_list):
    if isinstance(mean_list, int) or isinstance(mean_list, float):
        mean_list = [mean_list]

    if isinstance(std_list, int) or isinstance(std_list, float):
        std_list = [std_list]

    # # Define a common x-axis range
    x_min = 0
    x_max = 800 #max(mean_list) + 4 * max(std_list)
    x = np.linspace(x_min, x_max, 500)
    fig = go.Figure()

    dist_list=[]
    median_list=[]
    mode_list=[]
    sigma_list=[]
    p25_list=[]
    p75_list=[]
    p95_list=[]
    
    for i in range(len(mean_list)):
        pdf, sigma, median, mode, p25, p75,p95 = make_lognormal_trace2(mean_list[i], std_list[i], x_min, x_max)
        #print(f'Distribution {i}: Mean={mean_list[i]}, STD={std_list[i]}, Median={median:.2f},' 
        #f'Mode={mode:.2f}, Sigma={sigma:.2f}')
        fig.add_trace(go.Scatter(x=x, y=pdf, mode='lines', name=f'Mean {mean_list[i]}, STD {std_list[i]:.1f}'))
        dist=f'Distribution {i}'
        dist_list.append(dist)
        median_list.append(median)
        mode_list.append(mode)
        sigma_list.append(sigma)
        p25_list.append(p25)
        p75_list.append(p75)
        p95_list.append(p95)

    df= pd.DataFrame(
        {'Distribution':pd.Series(dist_list),
         'Mean':pd.Series(mean_list),
         'Std':pd.Series(std_list),
         'Median':pd.Series(median_list),
         'Mode':pd.Series(mode_list),
         'Sigma':pd.Series(sigma_list),
         'P25':pd.Series(p25_list),
         'P75':pd.Series(p75_list),
         'P95':pd.Series(p95_list),
         }
    )

    fig.update_layout(showlegend=False)
    #fig.show()
    return fig, df

#visualise_lognormal(215, 374.1)

#mean_list, std_list = make_lognormal_lists(18, 5)
#visualise_lognormal(mean_list, std_list)

## Compare theoretical distributions with each other as histograms
def visualise_lognormal_hist_list(mean_list, std_list, samples, random_seed):
    if isinstance(mean_list, (int, float)):
        mean_list = [mean_list]
    if isinstance(std_list, (int, float)):
        std_list = [std_list]
    fig_list=[]
    list_of_summary_lists=[]
    #fig = go.Figure()
    for i in range(len(mean_list)):
        fig = go.Figure()

        dist = Lognormal(mean_list[i], std_list[i], random_seed = random_seed)
        sample_list=[]
        for j in range(samples):
            sample = dist.sample()
            sample_list.append(sample)
        
        dist_summary_list=samples_to_summary_list(sample_list)
        list_of_summary_lists.append(dist_summary_list)

        #print(f'Distribution {i}: Mean={mean_list[i]}, STD={std_list[i]}') 

        fig.add_trace(go.Histogram(
            x=sample_list,
            name = f'Dist {i}',
            #opacity=0.3
        ))
        fig.update_traces(xbins=dict(start=0, end=2000, size=5))

        fig.update_xaxes(range=[0, 2000])
        fig.update_layout(template='plotly_white')
        #fig.show()
        fig_list.append(fig)

    return fig_list, list_of_summary_lists

#mean_list, std_list = make_lognormal_lists(18, 2)
#visualise_lognormal_hist_list(250, 374.1, 70000)



### Compare real distribution with a list of theoretical distributions
def hist_compare_real_model(series, series_name, mean_list, std_list, random_seed):
    if isinstance(mean_list, (int, float)):
        mean_list = [mean_list]
    if isinstance(std_list, (int, float)):
        std_list = [std_list]
    #csv = pd.read_csv(filepath)
    samples = len(series) # counts the number of rows in real data
    fig = go.Figure()
    fig_list=[]
    box_list=[]
    list_of_summary_lists=[]
    real_summary_list=samples_to_summary_list(series)
    list_of_summary_lists.append(real_summary_list)
    for i in range(len(mean_list)):
        #print(f'Distribution {i}: Mean={mean_list[i]}, STD={std_list[i]}') 
        dist = Lognormal(mean_list[i], std_list[i], random_seed = random_seed)
        sample_list=[]
        for j in range(samples):
            sample = dist.sample()
            sample_list.append(sample)
        
        dist_summary_list=samples_to_summary_list(sample_list)
        list_of_summary_lists.append(dist_summary_list)

        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=series,
            name=series_name
            #opacity=0.3
        ))
        #fig.update_traces(xbins=dict(start=0, end=2000, size=5))
        fig.add_trace(go.Histogram(
            x=sample_list,
            name = f'Modelled'
                    #opacity=0.3
        ))
        fig.update_traces(xbins=dict(start=0, end=2000, size=24))
        fig.update_xaxes(range=[0, 2000])
        fig.update_layout(title = f'{series_name} vs Modelled Dist {i}',
                          template='plotly_white')
        #fig.show()
        fig_list.append(fig)

        box = go.Figure()
        box.add_trace(go.Box(y=series, name='Real', boxpoints=False))
        box.add_trace(go.Box(y=sample_list, name='Modelled', boxpoints=False))
        box.update_layout(title = f'{series_name} vs Modelled Dist {i}',
                          template='plotly_white')
        
        box_list.append(box)


    return fig_list, list_of_summary_lists, box_list #note: list of summary lists will be longer than fig list because it has real distribtion at the start



#for use with series
def calc_mode(pdseries, bin_size, min_bin_edge):
    vmax = pdseries.max()
    bins = np.arange(min_bin_edge, vmax + bin_size, bin_size)
    labels = [f"{int(b)}–{int(b + bin_size)}" for b in bins[:-1]]
    binned = pd.Series()
    binned= pd.cut(pdseries, bins=bins, labels=labels)
    mode_bin = binned.mode()[0]
    #print(f"Mode of bins: {mode_bin}")
    return mode_bin



#csv=pd.read_csv("data/los_fy2425.csv")
#calc_mode(csv,'LoSHrs', 1, 0)
dist = Lognormal(215, 355, random_seed = 5)
sample_list=[]
for j in range(70000):
    sample = dist.sample()
    sample_list.append(sample)

def samples_to_summary_list(sample_list):

    sample_list = pd.Series(sample_list)

    mean=sample_list.mean()
    std=sample_list.std()
    mode=calc_mode(sample_list, 2, 0)
    median=sample_list.median()
    perc_25=sample_list.quantile(0.25)
    perc_75=sample_list.quantile(0.75)
    perc_95=sample_list.quantile(0.95)

    summary_list = [mean,std,mode,perc_25,median,perc_75,perc_95]
    return summary_list

def summary_lists_to_table(list_of_lists):
    labels=['mean','std','mode','25 perc','median','75 perc','95 perc']
    summary_df=pd.DataFrame(labels, columns=['Metric'])
    for i in range(len(list_of_lists)):
        summary_df[f'LoS Dist {i - 1}']=list_of_lists[i]
    return summary_df

## Compare theoretical distributions with each other as histograms
def visualise_normal_hist_list(mean_list, std_list, samples, random_seed):
    if isinstance(mean_list, (int, float)):
        mean_list = [mean_list]
    if isinstance(std_list, (int, float)):
        std_list = [std_list]
    fig_list=[]
    list_of_summary_lists=[]
    #fig = go.Figure()
    for i in range(len(mean_list)):
        fig = go.Figure()

        dist = Normal(mean_list[i], std_list[i], random_seed = random_seed)
        sample_list=[]
        for j in range(samples):
            sample = dist.sample()
            sample_list.append(sample)
        
        dist_summary_list=samples_to_summary_list(sample_list)
        list_of_summary_lists.append(dist_summary_list)

        #print(f'Distribution {i}: Mean={mean_list[i]}, STD={std_list[i]}') 

        fig.add_trace(go.Histogram(
            x=sample_list,
            name = f'Dist {i}',
            #opacity=0.3
        ))
        fig.update_traces(xbins=dict(start=0, end=2000, size=5))

        fig.update_xaxes(range=[0, 2000])
        fig.update_layout(template='plotly_white')
        #fig.show()
        fig_list.append(fig)

    return fig_list, list_of_summary_lists

def compare_real_model_diffplot(series, series_name, mean_list, std_list, random_seed):
    if isinstance(mean_list, (int, float)):
        mean_list = [mean_list]
    if isinstance(std_list, (int, float)):
        std_list = [std_list]

    samples = len(series)
    fig_list = []
    list_of_summary_lists = []
    overall_diffs = []

    real_summary_list = samples_to_summary_list(series)
    list_of_summary_lists.append(real_summary_list)

    # Define common histogram bins
    bins = np.arange(0, 2000 + 24, 24)  # bin size = 24
    bin_centers = (bins[:-1] + bins[1:]) / 2

    real_counts, _ = np.histogram(series, bins=bins)

    for i in range(len(mean_list)):
        dist = Lognormal(mean_list[i], std_list[i], random_seed=random_seed)
        sample_list = [dist.sample() for _ in range(samples)]

        dist_summary_list = samples_to_summary_list(sample_list)
        list_of_summary_lists.append(dist_summary_list)

        model_counts, _ = np.histogram(sample_list, bins=bins)
        diff = real_counts - model_counts
        abs_diff_sum = np.sum(np.abs(diff))
        overall_diffs.append(abs_diff_sum)

        # Create plot
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=bin_centers,
            y=diff,
            name='Real - Modelled',
            marker_color='crimson'
        ))

        # Main title and subtitle (via annotations)
        fig.update_layout(
            title=f'Difference Plot: {series_name} - Modelled Dist {i}',
            xaxis_title='Length of Stay',
            yaxis_title='Difference in Frequency',
            template='plotly_white',
            xaxis=dict(range=[0, 2000]),
            annotations=[
                dict(
                    text=f"Sum of absolute differences: {abs_diff_sum:.2f}",
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    showarrow=False,
                    font=dict(size=12, color='gray'),
                    align='center'
                )
            ]
        )

        fig_list.append(fig)

    return fig_list, list_of_summary_lists, overall_diffs

def compare_real_model_percentdiff(series, series_name, mean_list, std_list, random_seed):
    if isinstance(mean_list, (int, float)):
        mean_list = [mean_list]
    if isinstance(std_list, (int, float)):
        std_list = [std_list]

    samples = len(series)
    fig_list = []
    list_of_summary_lists = []
    percent_diff_scores = []  # Stores the MAPD values

    real_summary_list = samples_to_summary_list(series)
    list_of_summary_lists.append(real_summary_list)

    # Define bins and centers
    bins = np.arange(0, 2000 + 24, 24)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    real_counts, _ = np.histogram(series, bins=bins)

    for i in range(len(mean_list)):
        dist = Lognormal(mean_list[i], std_list[i], random_seed=random_seed)
        sample_list = [dist.sample() for _ in range(samples)]
        dist_summary_list = samples_to_summary_list(sample_list)
        list_of_summary_lists.append(dist_summary_list)

        model_counts, _ = np.histogram(sample_list, bins=bins)

        # Avoid divide-by-zero: mask where real_counts == 0
        with np.errstate(divide='ignore', invalid='ignore'):
            percent_diff = np.where(
                real_counts == 0,
                0,
                100 * (real_counts - model_counts) / real_counts
            )

        # Replace nan or inf with 0 (optional: or could drop them)
        percent_diff = np.nan_to_num(percent_diff)

        # Mean absolute percentage difference (MAPD)
        mapd = np.mean(np.abs(percent_diff))
        percent_diff_scores.append(mapd)

        # Plot the percent difference
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=bin_centers,
            y=percent_diff,
            name='Percentage Difference',
            marker_color='mediumseagreen'
        ))

        fig.update_layout(
            title=f'Percentage Difference Plot: {series_name} vs Modelled Dist {i}',
            xaxis_title='Length of Stay',
            yaxis_title='Percentage Difference (%)',
            template='plotly_white',
            xaxis=dict(range=[0, 2000]),
            annotations=[
                dict(
                    text=f"Mean Absolute % Difference: {mapd:.2f}%",
                    x=0.5,
                    y=1.05,
                    xref='paper',
                    yref='paper',
                    showarrow=False,
                    font=dict(size=12, color='gray'),
                    align='center'
                )
            ]
        )

        fig_list.append(fig)

    return fig_list, list_of_summary_lists, percent_diff_scores



### Function testing ground

# use this to generate sequence to hard code into app
# mode=16
# traces=20
# mean_list, std_list = make_lognormal_lists(mode, traces)

# fig_list, list_of_summary_lists=hist_compare_real_model("../data/los_fy2425.csv", mean_list, std_list, 5)

# summary_df=summary_lists_to_table(list_of_summary_lists)

# for i in range(len(fig_list)):
#     fig_list[i].show()

# display(summary_df)