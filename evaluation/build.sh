#!/bin/bash

cd svm_proprank
make

cd ../lib/pyrankagg
python3 setup.py install

cd ../../
pip install -r requirements.txt