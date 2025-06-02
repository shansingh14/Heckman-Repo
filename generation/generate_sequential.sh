#./generate_sequential.sh 5 5 2 2 0

pass=$1
cutOff=$2
eta=$3
set=$4 # 1 for dataset 1, 2 for dataset 2
run_num=$5
k=$6

mkdir -p "../evaluation/generated_data/svm/naive/eta$eta/first_run/"
mkdir -p "../evaluation/generated_data/svm/propensity/eta$eta/first_run/"
mkdir -p "../evaluation/generated_data/heckman_svm/eta$eta/first_run/"
mkdir -p "../evaluation/nsvm_qid_c/svm_eta${eta}_first/"

if [ "$cutOff" -eq -1 ]; then
  file1="naive_svm.$pass""pass.see$k.eta$eta"
  file2="heckman_svm.$pass""pass.see$k.eta$eta"
  file3="prop_svm.$pass""pass.see$k.eta$eta"

  echo "Generating  for cut off : $k"
  python3 svm.py "ninety_nine_percent_set$set.train.txt" "prediction.txt" "set$set.test.txt" $file1 $file2 $pass $k $eta $run_num &
  wait

  mv "$file1.train" "../evaluation/generated_data/svm/naive/eta$eta/first_run/"
  mv "$file1.test" "../evaluation/generated_data/svm/naive/eta$eta/first_run/"
  mv "$file2.train" "../evaluation/generated_data/heckman_svm/eta$eta/first_run/"
  mv "$file2.test" "../evaluation/generated_data/heckman_svm/eta$eta/first_run/"

  mv "nsvm_qid_c_see$k.test" "../evaluation/nsvm_qid_c/svm_eta${eta}_first/"
else
  for ((i=0; i<=$cutOff; ++i))
  do
      file1="naive_svm.$pass""pass.see$i.eta$eta"
      file2="heckman_svm.$pass""pass.see$i.eta$eta"
      # file3="prop_svm.$pass""pass.see$i.eta$eta"

      # selection bias eta = 0, position bias eta = 1, if both eta = 1
      echo "Generating  for cut off : $i"
      # python2.7 svm.py "99_percent_set$set.binary.txt" "prediction.txt" $file1 $file3 $file2 $pass $i $eta &
      # python3 svm.py "99_percent_set$set.binary.txt" "prediction.txt" "set$set.valid.txt" "set$set.test.binary.txt" $file1 $file2 $pass $i $eta $run_num -1 0 &
      # this is for the temporary sampled dataset generation
      python3 svm.py "set$set.train_sampled.binary.txt" "prediction.txt" "set$set.valid.txt" "set$set.test.binary.txt" $file1 $file2 $pass $i $eta $run_num -1 0 &
      wait

      mv "$file1.train" "../evaluation/generated_data/svm/naive/eta$eta/first_run/"
      mv "$file1.test" "../evaluation/generated_data/svm/naive/eta$eta/first_run/"
      mv "$file2.train" "../evaluation/generated_data/heckman_svm/eta$eta/first_run/"
      mv "$file2.test" "../evaluation/generated_data/heckman_svm/eta$eta/first_run/"
      # mv "$file3.train" "../evaluation/generated_data/svm/propensity/eta$eta/first_run/"
      # mv "$file3.test" "../evaluation/generated_data/svm/propensity/eta$eta/first_run/"

      mv "nsvm_qid_c_see$i.test" "../evaluation/nsvm_qid_c/svm_eta${eta}_first/"
  done
fi