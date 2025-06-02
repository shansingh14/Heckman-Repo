#This code generate data when base ranker is SVM-rank, the process is as follows:
#Base ranker learn o 1% of data, and generates a prediction score for the remaining 99% of data
#The 99% of data will be ranked according to the prediction score
#clicks will be generated from this ranked data with multiple sampling times (multiple pass) to augment data
# The final generated data will be written to be fed into naive svm and others


import random,operator,numpy as np
from copy import deepcopy
import sys, math

EPSILON = 0

class searchItem:

    def __init__(self , r , t, a, score):
        self.true_rel=t
        self.ranking=r
        self.attributes=a
        self.score=score


class searchResult:

    def __init__(self):
        self.result = []
        self.clicked = {}

    def sortByRank(self):
        self.result.sort(key = operator.attrgetter('ranking'), reverse = True)
        for i in range(len(self.result)):
            self.result[i].ranking = i

    def doPrint(self):
        print("searchResult")
        for r in self.result:
            print("ranking=" + str(r.ranking) + ", true_rel=" + str(r.true_rel) + ", att=" + str(r.attributes))
        print("============")

    def getRankOfClicked(self, clicks):
        counter = 0
        r=[]
        # assert len(clicks) == len(self.result)
        for c in clicks:
            assert c==0 or c==1
            if c==1:
                r.append(self.result[counter].ranking)

            counter = counter+1

        return r

    def setPropencityScores(self, clicks, eta):
        counter = 0
        r=[]
        # assert len(clicks) == len(self.result)
        for c in clicks:
            assert c==0 or c==1
            if c==1:
                p = 1/((1/(1+float(self.result[counter].ranking)))**eta)
                self.clicked[counter] = p
            counter = counter+1

    def gen_clicks(self, eta):

        # assert len(self.ranking) == len(self.true_rel)
        count = len(self.result)
        '''
            count       = number of documents in search result (for a single query)
            ranking     = ranking of the documents in search result
            relevance   = true relevance of the documents provided in data
            eta         = presentation bias factor
        '''

        exam_prob = np.zeros(count)  # examination probability
        click_prob = np.zeros(count)  # click probability
        clicks = np.zeros(count, dtype=np.int64)  # actual clicks

        for i in range(count):
            doc_i = self.result[i].ranking
            exam_prob[doc_i] = (1.0 / (i + 1)) ** eta
            relevance_probability = EPSILON + (1 - EPSILON) * \
                                    (((math.pow(2, self.result[doc_i].true_rel)) - 1) / ((math.pow(2, 4)) - 1))
            click_prob[doc_i] = exam_prob[doc_i] * relevance_probability

        if np.sum(
                click_prob) <= 0:                                         # if no probability of clicks (possibly because of no relevance), return empty clicks,
            return np.array([])

        for i in range(min(count,observe_num+1)):                                  #from initiall, not generate clicks for bellow cut-off#
            doc_i = self.result[i].ranking
            clicks[doc_i] = np.random.binomial(n=1, p=click_prob[doc_i])  # generate the click
            assert i==doc_i

        if np.sum(clicks) <= 0:  # if no clicks generated, return empty
            return np.array([])

        self.setPropencityScores(clicks , eta)
        return clicks

input_file_name = sys.argv[1]           #99% of train data; not really 100%
prediction= sys.argv[2]                 #prediction file that contains base ranker scores for 99% of train data#
valid_file_name = sys.argv[3]           #valid file name
# prediction_valid= sys.argv[4]           #prediction file that contains base ranker scores for valid data
input_file_name_test = sys.argv[4]      #test data file#
output_file_name_naive= sys.argv[5]     #output file that we write data that will be fed to naive-svm#
output_file_name_heckman= sys.argv[6]   #output file where we write data that will be fed to heckman#
sampling_times= int(sys.argv[7])        #number of passes (5)#
observe_num = int(sys.argv[8])          #cut off (1-30)#
eta= float(sys.argv[9])                 #eta=position bias severity#
run_num= int(sys.argv[10])              #this indicates the random number generation for clicks
# valid_click_as_nsvm = int(sys.argv[12]) #1 means generate validation click data in naive svm format # removing for now
number_of_interactions= int(sys.argv[11]) #total number of interactions
documents_to_consider=int(sys.argv[12]) # documents to consider for each ranked list, similar to observe no,
                                        # but might have different meaning at later times, so keeping it separate

file_test = open(input_file_name_test, "r")
D_test={}
for f1 in file_test:
    qid=f1[f1.find(":")+1:f1.find(" ",f1.find(":"))]
    attributes=""
    if f1[-1]== "\n":
        attributes=f1[f1.find(" ", f1.find(":"))+1:-1]
    else:
        attributes = f1[f1.find(" ", f1.find(":"))+1:]
    trueR = float(f1[:f1.find(" ")])
    # print(trueR)
    if qid not in D_test:
        # D[qid]=[]
        D_test[qid] = searchResult()
    newSearchItem = searchItem (1, trueR, attributes, 1)
    D_test[qid].result.append(newSearchItem)

file_test.close()

#read train data, and prediction file#
file_train = open(input_file_name, "r")

file_prediction = open(prediction, "r")

D={}
for f1 in file_train:

    qid=f1[f1.find(":")+1:f1.find(" ",f1.find(":"))]
    attributes=""
    if f1[-1]== "\n":
        attributes=f1[f1.find(" ", f1.find(":"))+1:-1]
    else:
        attributes = f1[f1.find(" ", f1.find(":"))+1:]

    f2 = file_prediction.readline()
    ranking=float(f2[:-1])
    trueR = float(f1[:f1.find(" ")])
    if qid not in D:
        D[qid] = searchResult()

    newSearchItem = searchItem (ranking, trueR, attributes, ranking)

    D[qid].result.append(newSearchItem)

file_train.close()
file_prediction.close()

# read valid data, and prediction file
# file_valid = open(valid_file_name, "r")
# file_prediction_valid = open(prediction_valid, "r")
# D_valid = {}
# for f1 in file_valid:

#     qid = f1[f1.find(":") + 1:f1.find(" ", f1.find(":"))]
#     attributes = ""
#     if f1[-1] == "\n":
#         attributes = f1[f1.find(" ", f1.find(":")) + 1:-1]
#     else:
#         attributes = f1[f1.find(" ", f1.find(":")) + 1:]

#     f2 = file_prediction_valid.readline()
#     ranking = float(f2[:-1])
#     trueR = float(f1[:f1.find(" ")])
#     if qid not in D_valid:
#         D_valid[qid] = searchResult()

#     newSearchItem = searchItem(ranking, trueR, attributes, ranking)

#     D_valid[qid].result.append(newSearchItem)

# file_valid.close()
# file_prediction_valid.close()

#### Start Sampling #####
D_new={}
D_train=D

D={}

qids = list(D_train)
#print qids

if number_of_interactions == -1:
    for sampling in range(sampling_times):      # number of passes
        for r in range(len(qids)):
            # r = random.randint(0,len(qids)-1)    #choose a random number to sample#
            for i in range(1,len(qids)*100):      #assuming that irrespective of how many sampling we are doing, the lenghth of qid would not exceed 100 times its initial length#
                newQID = qids[r]+"_"+str(i)
                if newQID not in D_new:
                    D_new[newQID] = deepcopy(D_train[qids[r]])
                    break

    #### END Sampling #####

    D_train=D_new
    #### START CLICK GENERATION #####
    sampling_numbers = 1
    qid_counts_curr = 0
    qid_count = len(qids)
    np.random.seed(sampling_numbers * 4200000 + run_num * 1000)
    total_no_of_clicks = 0
    for k in D_train: # for each key, sort the corresponding value
        D_train[k].sortByRank()
        qid_counts_curr += 1
        if qid_counts_curr % qid_count == 0:
            sampling_numbers += 1
            np.random.seed(sampling_numbers * 4200000 + run_num * 1000)
        clicks= D_train[k].gen_clicks(eta)
        total_no_of_clicks += np.sum(clicks)

    print("Total number of clicks generated: " + str(total_no_of_clicks))
else:
    sampling_numbers = 1
    qid_counts_curr = 0
    qid_count = len(qids)
    np.random.seed(sampling_numbers * 4200000 + run_num * 1000)
    total_no_of_clicks = 0

    break_all = False
    # print qids
    for sampling in range(sampling_times):  # number of passes
        for r in range(len(qids)):
            # r = random.randint(0,len(qids)-1)    #choose a random number to sample#
            for i in range(1, len(qids) * 100):  # assuming that irrespective of how many sampling we are doing, the lenghth of qid would not exceed 100 times its initial length#
                newQID = qids[r] + "_" + str(i)
                if newQID not in D_new:
                    qid_counts_curr += 1
                    if qid_counts_curr % qid_count == 0:
                        sampling_numbers += 1
                        np.random.seed(sampling_numbers * 4200000 + run_num * 1000)
                    D_new[newQID] = deepcopy(D_train[qids[r]])
                    D_new[newQID].sortByRank()
                    clicks = D_new[newQID].gen_clicks(eta)
                    total_no_of_clicks += np.sum(clicks)
                    if total_no_of_clicks >= number_of_interactions:
                        break_all = True
                    break
            if break_all:
                break
        if break_all:
            break

    print("Total number of clicks generated: " + str(total_no_of_clicks))
    #### END Sampling #####

    D_train = D_new


#### START CLICK GENERATION for valid #####
# sampling_numbers = 1
# qid_counts_curr = 0
# qids_valid = list(D_valid)
# qid_count_valid = len(qids_valid)
# np.random.seed(sampling_numbers * 4200000 + run_num * 1000)
# for k in D_valid: # for each key, sort the corresponding value
#     D_valid[k].sortByRank()
#     qid_counts_curr += 1
#     if qid_counts_curr % qid_count_valid == 0:
#         sampling_numbers += 1
#         np.random.seed(sampling_numbers * 4200000 + run_num * 1000)
#     clicks_valid = D_valid[k].gen_clicks(eta)

#### START Writing Output (this data will be reranked by Heckman, niave svm and propensity svm)#####
# write naive svm#
train_out = open(output_file_name_naive+".train", "w")
test_out = open(output_file_name_naive+".test", "w")
# valid_out = open(valid_file_name.split('.txt')[0] + ".prediction.txt", "w")
test_qid_c = open("nsvm_qid_c_see" + str(observe_num) + ".test", "w")

counter=1
for k in D_train:
    for i in range(len(D_train[k].result)):
       if 0 < documents_to_consider <= i:
           break
       if i in D_train[k].clicked:
           train_out.write("1 qid:" + str(counter) + " " + D_train[k].result[i].attributes + "\n")
       else:
           train_out.write("0 qid:" + str(counter) + " " + D_train[k].result[i].attributes + "\n")
    counter = counter + 1

for k in D_test:
    for i in range(len(D_test[k].result)):
        true_rel = int(D_test[k].result[i].true_rel)
        test_out.write(str(int(true_rel)) + " qid:" + str(counter) + " " + D_test[k].result[i].attributes+"\n")
        test_qid_c.write(str(counter) + " " + str(int(true_rel)) + "\n")
    counter = counter + 1

# for k in D_valid:
#     for i in range(len(D_valid[k].result)):
#        if 0 < documents_to_consider <= i:
#            break
#        if i in D_valid[k].clicked:
#            # if valid_click_as_nsvm == 1:
#            valid_out.write("1 qid:" + str(counter) + " " + D_valid[k].result[i].attributes + "\n")
#            # else:
#            #     valid_out.write(str(counter) + " 1 " + D_valid[k].result[i].attributes + " " + str(
#            #         D_valid[k].result[i].ranking + 1) + " " + str(1)
#            #                 + " " + str(int(D_valid[k].result[i].true_rel))
#            #                 + " " + str(D_valid[k].result[i].score) + "\n")
#        else:
#            # if valid_click_as_nsvm == 1:
#            valid_out.write("0 qid:" + str(counter) + " " + D_valid[k].result[i].attributes + "\n")
#            # else:
#            #     valid_out.write(str(counter) + " 0 " + D_valid[k].result[i].attributes + " " + str(
#            #         D_valid[k].result[i].ranking + 1) + " " + str(1)
#            #                 + " " + str(int(D_valid[k].result[i].true_rel))
#            #                 + " " + str(D_valid[k].result[i].score) + "\n")
#     counter = counter + 1

train_out.close()
test_out.close()
# valid_out.close()
test_qid_c.close()

# write heckman
train_out = open(output_file_name_heckman+".train", "w")
test_out = open(output_file_name_heckman+".test", "w")

counter=1

for k in D_train:
    for i in range(len(D_train[k].result)):
        if 0 < documents_to_consider <= i:
            break
        if D_train[k].result[i].ranking <= observe_num:
            seen = 1
        else:
            seen = 0
        if i in D_train[k].clicked:
            train_out.write(str(counter) + " 1 " + D_train[k].result[i].attributes + " " + str(D_train[k].result[i].ranking + 1) + " " + str(seen)
                            + " " + str(int(D_train[k].result[i].true_rel))
                            + " " + str(D_train[k].result[i].score) + "\n")
        else:
            train_out.write(str(counter) + " 0 " + D_train[k].result[i].attributes + " " + str(D_train[k].result[i].ranking + 1) + " " + str(seen)
                            + " " + str(int(D_train[k].result[i].true_rel))
                            + " " + str(D_train[k].result[i].score) + "\n")
    counter = counter + 1

for k in D_test:
    for i in range(len(D_test[k].result)):
       true_rel = int(D_test[k].result[i].true_rel)
       seen=1
       test_out.write(str(counter) + " " + str(true_rel) + " " + D_test[k].result[i].attributes + " " + str(D_test[k].result[i].ranking) + " " + str(seen)
       + " " + str(int(D_test[k].result[i].true_rel)) + " 1" + "\n")
    counter = counter+1

#### End Writing Output #####
print("done\n")

train_out.close()
test_out.close()
