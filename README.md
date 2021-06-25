# Instructions for the Rollbar Prometheus Exporter

## Background
This prometheus exporter takes Rollbar item and occurrence data that is available from the Rollbar API and converts it into a format that can be consumed by Prometheus  
  
Once the metrics data is in Prometheus it can be used in dashboarding tools, for example Grafana   

## Requirements
virtualenv  
python 3.x (This exporter been tested with Python 3.8.5)  '

It is a requirement that the Rollbar projects that you are getting metrics, for has the following parameters set: 

environment  
code_version  

### Setting up an environment for the exporter
Download this source code repository  

Open an command window and change directory (cd) to the root directory of this source code repository  

#### 1. Create the environment

Creating the environment involves the following steps:  

1. Give the ./create_environment.sh shell script execute permissions   
2. Execute ./create_environment.sh to create the environment  

See the commands below  

chmod +x ./create_environment.sh  
  
./create_environment.sh  

You should now have a virtual environment that has installed the required dependencies from ./requirements.txt  

#### 2. Confirm the version of python

Confirm the version of python in yoru virtual environment

source venv/bin/activate  
python3 --version  

The version of python3 should be version 3.7 or higher  


#### 3. Add read access tokens to projects.json for the Projects that you want metrics for
cd ./metrics  


Open projects.json and add your Rollbar project_names (also called project_slugs) and read_access_tokens as shown below  
  
{  
    "project_name_1": "PROJECT_ACCESS_TOKEN_WITH_READ_SCOPE",  
    "project_name_2": "PROJECT_ACCESS_TOKEN_WITH_READ_SCOPE"  


#### 4. Create a Rollbar project to accept errors from this prometheus_exporter application  

Set it up so that this prometheus exporter application sends error data to Rollbar if errors occur


Create a Rollbar project called Prometheus Exporter
Get a project access token with post_server_item scope
  
cd ./metrics   
Add the Rollbar read_access_token and environment information to config.ini

[rollbar]  
access_token=PROJECT_ACCESS_TOKEN_WITH_POST_SERVER_SCOPE  
environment=production  
code_version=0.0001  
  
Save config.ini

When this prometheus exporter application is running, check Rollbar from time to time for errors  
Configure notifications and other workflows as needed in Rollbar  

  
### Running the application as a flask web application  

#### Change the port if needed
The default port is 8083 (see port settings in metrics/app.py). 
You can override this by setting an EXPORTER_PORT environment variable with a different port

#### Run the flask application
From the root folder of the repository run the folloiwng commands  
  
source venv/bin/activate    
cd ./metrics    
python3 app.py  
  
The runs the file app.py as a web application (by default on port 8083)  
  
app.py has a /metrics endpoint that prometheus can query  
  
Generate some errors in the projects referenced in projects.json above  

From a browser open http(s)://localhost:8083/metrics  

You should see a list of the metrics 


#### To stop the flask application

From the command window where the flask application is running type Control-C  
  
  
## Prometheus Configuration  
From the root folder of this source code repository 

Copy the contents of ./util/prometheus.yml file into the prometheus.yml file for your prometheus installation

Restart prometheus
  
Prometheus will now go out and pull metrics from http(s)://your_host_name:8083/metrics every 15 seconds    


### Debugging this prometheus exporter application from a command line  

To check once for metrics from Rollbar, or to debug the application you can run this prometheus exporter application directly from a command line  

From the root folder of the repository do the following  

source venv/bin/activate  
cd ./metrics  

../venv/bin/python3 process_metrics.py  

  
This will allow you to check for metrics once    
It will print the metrics back to the screen   
  
This is also an easy way to debug the application 


  



