import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from app.model import g, Trial
from scipy import stats
from scipy.stats import lognorm

##### Visualising lognormal distributions - visualising a particular distribution
# Given mean and std in real space
# mean = 215
# std = 374.1

# # Convert to shape (s), location (loc), and scale parameters
# phi = np.sqrt(std**2 + mean**2)
# sigma = np.sqrt(np.log((phi**2) / (mean**2)))
# mu = np.log(mean**2 / phi)

# # Generate x values
# x = np.linspace(1, mean + 4*std, 500)
# pdf = lognorm.pdf(x, s=sigma, scale=np.exp(mu))

# # Plot
# fig = go.Figure()
# fig.add_trace(go.Scatter(x=x, y=pdf, mode='lines', name='Lognormal PDF'))
# fig.update_layout(template='plotly_white', title='Lognormal Distribution')
# fig.show()

#### Visualising a loop of distributions - Reducing mean and standard deviation together in proportion
# Given mean and std in real space
mean_list = list(range(160, 250, 10))
std_list = [x * 1.74 for x in mean_list]


# Define a common x-axis range
x_min = 1
x_max = 800 #max(mean_list) + 4 * max(std_list)
x = np.linspace(x_min, x_max, 500)

fig = go.Figure()

for i in range(len(mean_list)):

# Convert to shape (s), location (loc), and scale parameters
    phi = np.sqrt(std_list[i]**2 + mean_list[i]**2)
    sigma = np.sqrt(np.log((phi**2) / (mean_list[i]**2)))
    mu = np.log(mean_list[i]**2 / phi)

    median = np.exp(mu)
    mode = np.exp(mu - sigma**2)
    print(f'Distribution {i}: Mean={mean_list[i]}, Median={median:.2f},' 
          f'Mode={mode:.2f}, Sigma={sigma:.2f}')

    # Generate x values
    #x = np.linspace(1, mean_list[i] + 4*std_list[i], 500)
    pdf = lognorm.pdf(x, s=sigma, scale=np.exp(mu))

    # Plot
    fig.add_trace(go.Scatter(x=x, y=pdf, mode='lines', name=f'Mean {mean_list[i]}, STD {std_list[i]:.1f}'))
    
    
fig.update_layout(template='plotly_white', 
                  title='Overlay of Lognormal Distributions reducing mean and standard dev together',
                  xaxis_title='x',
                  yaxis_title='Probability Density',
                  xaxis=dict(dtick=100))

fig.show()

#### Visualising a loop of distributions - Reducing mean, standard dev staying the same
# Given mean and std in real space
mean_list = list(range(160, 250, 10))
std_list = [355] * len(mean_list)

# Define a common x-axis range
x_min = 1
x_max = 800 #max(mean_list) + 4 * max(std_list)
x = np.linspace(x_min, x_max, 500)

fig = go.Figure()

for i in range(len(mean_list)):

# Convert to shape (s), location (loc), and scale parameters
    phi = np.sqrt(std_list[i]**2 + mean_list[i]**2)
    sigma = np.sqrt(np.log((phi**2) / (mean_list[i]**2)))
    mu = np.log(mean_list[i]**2 / phi)

    median = np.exp(mu)
    mode = np.exp(mu - sigma**2)
    print(f'Distribution {i}: Mean={mean_list[i]}, Median={median:.2f},' 
          f'Mode={mode:.2f}, Sigma={sigma:.2f}')

    # Generate x values
    #x = np.linspace(1, mean_list[i] + 4*std_list[i], 500)
    pdf = lognorm.pdf(x, s=sigma, scale=np.exp(mu))

    # Plot
    fig.add_trace(go.Scatter(x=x, y=pdf, mode='lines', name=f'Mean {mean_list[i]}, STD {std_list[i]:.1f}'))
    
    
fig.update_layout(template='plotly_white', 
                  title='Overlay of Lognormal Distributions Changing mean, STD constant',
                  xaxis_title='x',
                  yaxis_title='Probability Density',
                  xaxis=dict(dtick=100))

fig.show()

#### Visualising a loop of distributions - Reducing std, mean staying the same
# Given mean and std in real space
std_list = list(range(240, 480, 20))
mean_list = [204] * len(mean_list)

# Define a common x-axis range
x_min = 1
x_max = 800 #max(mean_list) + 4 * max(std_list)
x = np.linspace(x_min, x_max, 500)

fig = go.Figure()

for i in range(len(mean_list)):

# Convert to shape (s), location (loc), and scale parameters
    phi = np.sqrt(std_list[i]**2 + mean_list[i]**2)
    sigma = np.sqrt(np.log((phi**2) / (mean_list[i]**2)))
    mu = np.log(mean_list[i]**2 / phi)

    median = np.exp(mu)
    mode = np.exp(mu - sigma**2)
    print(f'Distribution {i}: Mean={mean_list[i]}, Median={median:.2f},' 
          f'Mode={mode:.2f}, Sigma={sigma:.2f}')

    # Generate x values
    #x = np.linspace(1, mean_list[i] + 4*std_list[i], 500)
    pdf = lognorm.pdf(x, s=sigma, scale=np.exp(mu))

    # Plot
    fig.add_trace(go.Scatter(x=x, y=pdf, mode='lines', name=f'Mean {mean_list[i]}, STD {std_list[i]:.1f}'))
    
    
fig.update_layout(template='plotly_white', 
                  title='Overlay of Lognormal Distributions Changing STD, Mean constant',
                  xaxis_title='x',
                  yaxis_title='Probability Density',
                  xaxis=dict(dtick=100))

fig.show()

# Get values of sigma out of examples above
######## Try fixing mode -- need to just plug in values of sigma and calculate SD afterwards
# Fixed target mode
mode_target = 25 # example

# Try different sigma values (smaller sigma → thinner tails)
sigma_list = np.linspace(0.9, 1.4, 12)  # Adjust as you want

# x range
x_min = 1
x_max = 800
x = np.linspace(x_min, x_max, 500)

fig = go.Figure()

for i, sigma in enumerate(sigma_list):
    # Adjust mu to keep mode constant
    mu = np.log(mode_target) + sigma**2

    # Calculate mean and std (in real space) if needed
    mean = np.exp(mu + 0.5 * sigma**2)
    std = np.sqrt((np.exp(sigma**2) - 1) * np.exp(2*mu + sigma**2))

    median = np.exp(mu)
    mode = np.exp(mu - sigma**2)  # Should exactly equal mode_target

    print(f'Distribution {i}: Sigma={sigma:.3f}, Mean={mean:.2f}, Median={median:.2f},'
           f'Mode={mode:.2f}, STD={std:.2f}')

    pdf = lognorm.pdf(x, s=sigma, scale=np.exp(mu))

    fig.add_trace(go.Scatter(x=x, y=pdf, mode='lines',
                             name=f'Sigma {sigma:.2f}'))

fig.update_layout(template='plotly_white',
                  title=f'Overlay of Lognormal Distributions (Fixed Mode {mode_target})',
                  xaxis_title='x',
                  yaxis_title='Probability Density',
                  xaxis=dict(dtick=100))

fig.show()