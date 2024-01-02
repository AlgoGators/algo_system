
# AlgoGators System
## Installation
Begin installation of the total system by running:
```
git clone https://github.com/AlgoGators/algo_system.git --recurse
```
OR
```
git clone https://github.com/AlgoGators/algo_system.git
cd algo_system
git submodule update --init --recurse
```

Incorporating the dynamic optimization with trend and carry signals to generate position sizes
## Design

### Dynamic Optimization
The dynamic optimization requires the following inputs:
- Summed returns of the trend and carry signals

### Trend
The trend signal requires the following inputs:
- List of Instrument objects
- dictionary of historical prices as a pandas dataframe
- capital
- risk target
- multipliers of instruments 
- list of spans for the EWMA   
