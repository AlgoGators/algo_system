
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
There are API keys and login credentials that for obvious reasons should be stored privately and separate of the codebase.

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
