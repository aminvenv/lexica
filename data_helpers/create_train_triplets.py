import pandas as pd
import numpy as np
import argparse
import os
from tqdm import tqdm
import re


def main(task_name, addr):
    task_test_qrel = pd.read_csv(addr+task_name+'/test.qrel',
                names=['qid', 'zero', 'docno', 'relevance'],
                sep=' ')
    task_val_qrel = pd.read_csv(addr+task_name+'/val.qrel',
                names=['qid', 'zero', 'docno', 'relevance'],
                sep=' ')

    prefix = '../data/'+task_name+'_data'

    temp_lst = list(set(task_val_qrel['qid'].values))
    picked_qid = np.random.choice(temp_lst, size=int(np.around(0.15*len(temp_lst))), replace=False, p=None)
    assert set(task_val_qrel[task_val_qrel['qid'].isin(picked_qid)]['qid'].values) == set(picked_qid), 'err'

    new_train_qrel = task_val_qrel[~task_val_qrel['qid'].isin(picked_qid)].copy()
    new_validation_run = task_val_qrel[task_val_qrel['qid'].isin(picked_qid)].copy()

    new_validation_run['Q0'] = len(new_validation_run) * ['Q0']
    new_validation_run['num'] = len(new_validation_run) * [-10]
    new_validation_run['run'] = len(new_validation_run) * ['validation']
    
    print("number of train samples for task: {}".format(len(new_train_qrel)))
    print("number of valid samples for task: {}".format(len(new_validation_run)))
    
    task_test_qrel.to_csv(prefix+'/test.qrel',
                          index=False, header=False, sep=' ')
    
    new_train_qrel.to_csv(prefix+'/train.qrel',
                          index=False, 
                          header=False,
                          sep=' ')
    new_train_qrel[['qid', 'docno']].to_csv(prefix+'/train_pairs.csv',
                                            index=False,
                                            header=False,
                                            sep='\t')

    new_validation_run[['qid','Q0', 'docno', 'num', 'relevance', 'run']].to_csv(prefix+'/valid.run',
                                                                                index=False,
                                                                                header=False,
                                                                                sep='\t')

    papers_meta_view_cite_read = pd.read_csv(addr+'meta_papers.csv',
                                             sep='\t')
    qid_list = []
    pos_list = []
    neg_list = []

    query_text_list = []
    pos_doc_text_list = [] 
    neg_doc_text_list = []

    for qid in tqdm(set(new_train_qrel['qid'].values)):
        pos_docids = new_train_qrel[(new_train_qrel['qid']==qid) & (new_train_qrel['relevance']==1)]['docno'].values
        neg_docids = new_train_qrel[(new_train_qrel['qid']==qid) & (new_train_qrel['relevance']==0)]['docno'].values

        list_of_neglists = np.random.choice(neg_docids, size=(len(pos_docids),2), replace=False)
        list_count = 0
        for pos_docid in pos_docids: 
            for neg_docid in list_of_neglists[list_count]:

                if qid not in papers_meta_view_cite_read['paper_id'].values:
                    continue
                else:
                    tmp = papers_meta_view_cite_read[papers_meta_view_cite_read['paper_id']==qid]
                    tmp_query_text = re.sub(r'[^\w]', ' ', str(tmp.abstract.values[0]) + str(tmp.title.values[0]))

                if pos_docid not in papers_meta_view_cite_read['paper_id'].values:
                    continue
                else:
                    tmp = papers_meta_view_cite_read[papers_meta_view_cite_read['paper_id']==pos_docid]
                    tmp_pos_text = re.sub(r'[^\w]', ' ', str(tmp.abstract.values[0]) + str(tmp.title.values[0]))

                if neg_docid not in papers_meta_view_cite_read['paper_id'].values:
                    continue
                else:
                    tmp = papers_meta_view_cite_read[papers_meta_view_cite_read['paper_id']==neg_docid]
                    tmp_neg_text = re.sub(r'[^\w]', ' ', str(tmp.abstract.values[0]) + str(tmp.title.values[0]))

                query_text_list.append(tmp_query_text)
                pos_doc_text_list.append(tmp_pos_text)
                neg_doc_text_list.append(tmp_neg_text)
                qid_list.append(qid)
                pos_list.append(pos_docid)
                neg_list.append(neg_docid)

            list_count += 1

    qid_posid_negid = pd.DataFrame(columns=['qid','query','pos_docno', 'pos', 'neg_docno', 'neg'])
    qid_posid_negid['qid'] = qid_list
    qid_posid_negid['query'] = query_text_list
    qid_posid_negid['pos_docno'] = pos_list
    qid_posid_negid['pos'] = pos_doc_text_list
    qid_posid_negid['neg_docno'] = neg_list
    qid_posid_negid['neg'] = neg_doc_text_list

    qid_posid_negid.to_csv(prefix+'/train_triples.csv',
                           index=False,
                           header=False,
                           sep='\t')

    print('pre-processing for task {} finished'.format(task_name))


if __name__=="__main__":
    parser = argparse.ArgumentParser('Create train validation run for Scidocs')
    parser.add_argument('--path')
    args = parser.parse_args()
   
    tasks = ['coview', 'coread', 'cocite', 'cite']
    
    for tsk in tasks:
        main(tsk,  args.path)
