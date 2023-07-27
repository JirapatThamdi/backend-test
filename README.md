## How to run service
```
# Create Python environment
python3 -m venv venv
source venv/bin/active

# Install required packages
pip install -r requirements.txt

# Start the service
python3 main.py

# API doc
# http://0.0.0.0:8000/docs#/
```

## How to test with client
```
# Do the same thing as server but run
python3 client/face-client.py

# the result image will saved in output/result.jpg
```