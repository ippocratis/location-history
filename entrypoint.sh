#!/bin/sh
echo "Running preprocess.py script"
python preprocess.py
echo "Starting Flask application"
python app.py
