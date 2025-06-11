#!/bin/bash

# run command -> ./svm_rank_gen.sh set2.train.txt set2.test.txt prediction.txt

train=$1		# train file name
valid=$2	# valid file name
out=$3		# output file name
out_valid=$4		# output file name

mkdir -p temp

# create 1 and 99 percent train file
python3 create_prediction_train_file.py $train
wait

# train using one percent train file
echo "naive train "
svm_rank/svm_rank_learn -c 0.01 'one_percent_'$train 'temp/model' > /dev/null &
wait

# predict the 99% train file
echo "naive predict training 99% "
svm_rank/svm_rank_classify 'ninety_nine_percent_'$train 'temp/model' $out > /dev/null &
wait

# predict the valid file
echo "naive predict valid "
svm_rank/svm_rank_classify $valid 'temp/model' $out_valid > /dev/null &
wait

rm -r temp