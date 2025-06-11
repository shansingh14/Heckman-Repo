#!/bin/bash

cd svm_proprank
make

cd ../lib/pyrankagg
# python3 setup.py install

cd ../../../

cd generation/svm_rank
make clean
make
echo "make file installed..."

cd ../../
pip install -r requirements.txt