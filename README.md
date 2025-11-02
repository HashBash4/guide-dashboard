# GUIDE Dashboard  
**Grid Use Insights for Decarbonisation and Engagement (GUIDE)**  

This dashboard provides real-time insights into the carbon intensity of the Australian electricity grid and recommends optimal times for electricity use to reduce emissions. It combines data from several public APIs (CSIRO, ElectricityMaps, and Open-Meteo) and visualises results in an interactive Dash web application.

---

## Setup Instructions

### 1. Create and activate a virtual environment  
```
# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 2. Install the required packages  
Depending on your operating system, install the corresponding dependencies file:

```
# For macOS:
pip install -r requirements-macos.txt

# For Windows/Linux:
pip install -r requirements_short.txt
```

### 3. Run the dashboard  
After installing the dependencies, start the application by running:
```
python app.py
```

Then open a web browser and navigate to the shown link!


---

### Notes
- An active internet connection is required to retrieve live data from the APIs.  
- If installation issues occur, upgrading pip may help:  
  ```
  pip install --upgrade pip
  ```
