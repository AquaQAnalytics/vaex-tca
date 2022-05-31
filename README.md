# Vaex-TCA
Code for a simple TCA app using Vaex and FastAPI. Vaex is a data library similar to Pandas, built to handle data which cannot fit in memory. More information is available on the Vaex website:

https://vaex.io/docs/index.html

FastAPI is a Python library used to set up APIs with minimal effort. More information on FastAPI is available here:

https://fastapi.tiangolo.com/

Use pip to install the required libraries for this project:

pip install numpy  
pip install pandas  
pip install vaex  
pip install fastapi "uvicorn[standard]"

To run the application, use one of the uvicorn commands below:

uvicorn main:app --reload  
uvicorn main:app --host "*" --port 1234

The reload flag will automatically refresh the webpage when there are any changes to the code - use for testing only. Data used for the project is NYSE TAQ data. Sample data can be accessed here:

https://ftp.nyse.com/Historical%20Data%20Samples/
