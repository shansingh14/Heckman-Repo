#!/bin/bash

# ./final.sh 5 5 .5 2 1 10 -1

pass=$1 # no of passes for generating clicks
cutOff=$2 # selection bias severity
eta=$3 # position bias severity
set=$4 # 1 for dataset 1, 2 for dataset 2
run_num=$5 # instance of run number; will be integer, pass it 1 for now
p=$6 # position up to which we are interested to evaluate
k=$7 # if only a single selection bias cuf-off. Either use cutOff or k. Set any of them to -1.
# If you want to run with different selection bias cutoff set cufOff variable, else for
# a single selection bias cut off set k value. For now, set it to -1.

cd "evaluation"
#echo "Cleaning..."
#sh clean.sh
#wait

cd "../generation"

if [ -f "set$set.valid.temp.txt" ]; then
  mv "set$set.valid.temp.txt" "set$set.valid.txt"
  rm "set$set.valid.temp.txt"
fi

echo "Training 1% and predicting 99% data"
if [ "$set" -eq 2 ]; then
  ./svm_rank_gen.sh set2.train.txt set2.valid.txt prediction.txt prediction_valid.txt
  wait
else
  ./svm_rank_gen.sh set1.train.txt set1.valid.txt prediction.txt prediction_valid.txt
  wait
fi

./generate_sequential.sh $pass $cutOff $eta $set $run_num $k
wait

cd "../evaluation"
./run.sh $eta $pass $cutOff
wait

cd "../"
echo "Everything is done!"

