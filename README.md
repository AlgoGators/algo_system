# AlgoGators System
## Building and Launching Docker Containers
### Environment file:
Make sure a .env file exists in this directory with the following parameters:
```
IBKR_USERNAME=
IBKR_PASSWORD=
API_PORT=
SOCAT_PORT=
TRADING_MODE=
READ_ONLY_API=
IB_GATEWAY_VERSION=
```
For example:
IBKR_USERNAME=john.doe
IBKR_PASSWORD=password1234
API_PORT=4002
SOCAT_PORT=4004
TRADING_MODE=paper
READ_ONLY_API=no
IB_GATEWAY_VERSION=1019

See [ib-gateway](https://github.com/AlgoGators/ib-gateway) repo for more information on parameters

To build and run (from parent directory):
```
docker-compose up -d
```

### IBC:


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

## Updating a submodule
```
git submodule update --remote <moduleName>
git add <moduleName>
git commit -m "your message"
git push
(follow the login instructions)
```
OR
```
git submodule update --remote <moduleName>
(and use the Desktop GUI to commit as normal)
```

## Adding Environment Variables
There are API keys and login credentials that for obvious reasons should be stored privately and separately of the codebase.

Create a .env file with the variables you wish to define; for example:
```
USERNAME=JOHN.D
PASSWORD=1234
```
Then to access these variables from Python:
```
import os
from dotenv import load_dotenv
from pathlib import Path
# loads the environment variables
load_dotenv(Path('path/to/.env'))
# retrieves the variable
print(os.getenv('USERNAME')) 
```

NOTE: An advantage of doing it this way, is that environment variables can be accessed by any function/file on the computer without having to reload the .env file.

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

### Carry
The carry signal requires the following inputs:
- List of Instrument objects
- dictionary of historical prices as a pandas dataframe
- capital
- risk target
- multipliers of instruments 
- list of spans for Carry   
