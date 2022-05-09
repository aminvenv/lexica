import pandas as pd
import json
from tqdm import tqdm
import re


def transform_runs(tsk, docid2index):
    run_df = pd.read_csv('./data/'+tsk+'_data/org_raw.run',
                         names=['qid', 'Q0', 'docno', 'rank', 'score', 'name'],
                         sep=' ',
                         dtype={'qid': str, 'docno': str})
    new_qid = []
    new_docno = []
    not_found = []

    for row in run_df.itertuples():
        new_qid.append(docid2index[row.qid])
        new_docno.append(docid2index[row.docno])

    new_run_df = pd.DataFrame(columns=['qid', 'Q0', 'docno', 'rank', 'score', 'name'])
    new_run_df['docno'] = new_docno
    new_run_df['qid'] = new_qid
    new_run_df['Q0'] = len(new_qid) * ['Q0']
    new_run_df['rank'] = len(new_qid) * [0]
    new_run_df['score'] = len(new_qid) * [0]
    new_run_df['name'] = len(new_qid) * ['scidocs']
    new_run_df.to_csv('./data/'+tsk+'_data/raw.run', sep=' ', index=False, header=False)


def transform_test_qrel(tsk, docid2index):
    test_qrels = pd.read_csv('./data/'+tsk+'_data/org_test.qrel',
                             sep=' ',
                             names=['qid', 'zeros', 'docno', 'label'],
                             dtype={'label': 'int64', 'qid': 'str', 'docno': 'str'})

    new_qid = []
    new_docno = []
    new_labels = []
    for row in test_qrels.itertuples():
        new_qid.append(docid2index[row.qid])
        new_docno.append(docid2index[row.docno])
        new_labels.append(row.label)

    new_test_qrel= pd.DataFrame(columns=['qid', 'zeros', 'docno', 'label'])
    new_test_qrel['docno'] = new_docno
    new_test_qrel['qid'] = new_qid
    new_test_qrel['label'] = new_labels
    new_test_qrel['zeros'] = len(new_qid) * [0]
    new_test_qrel.to_csv('./data/'+tsk+'_data/test.qrel', sep=' ', index=False, header=False)


def transform_train_qrel(tsk, docid2index):
    train_qrels = pd.read_csv('./data/'+tsk+'_data/org_train.qrel',
                              sep=' ',
                              names=['qid', 'zeros', 'docno', 'label'],
                              dtype={'label':'int64', 'qid':'str', 'docno':'str'})

    new_qid = []
    new_docno = []
    new_labels = []
    for row in train_qrels.itertuples():
        new_qid.append(docid2index[row.qid])
        new_docno.append(docid2index[row.docno])
        new_labels.append(row.label)

    new_train_qrel= pd.DataFrame(columns=['qid', 'zeros', 'docno', 'label'])
    new_train_qrel['docno'] = new_docno
    new_train_qrel['qid'] = new_qid
    new_train_qrel['label'] = new_labels
    new_train_qrel['zeros'] = len(new_qid) * [0]
    new_train_qrel.to_csv('./data/'+tsk+'_data/train.qrel', sep=' ', index=False, header=False)


def transform_val_qrel(tsk, docid2index):
    val_qrels = pd.read_csv('./data/'+tsk+'_data/org_val.qrel',
                sep=' ',
                names=['qid', 'zeros', 'docno', 'label'],
                dtype={'label':'int64', 'qid':'str', 'docno':'str'})

    new_qid = []
    new_docno = []
    new_labels = []
    for row in val_qrels.itertuples():
        new_qid.append(docid2index[row.qid])
        new_docno.append(docid2index[row.docno])
        new_labels.append(row.label)

    new_val_qrel= pd.DataFrame(columns=['qid', 'zeros', 'docno', 'label'])
    new_val_qrel['docno'] = new_docno
    new_val_qrel['qid'] = new_qid
    new_val_qrel['label'] = new_labels
    new_val_qrel['zeros'] = len(new_qid) * [0]
    new_val_qrel.to_csv('./data/'+tsk+'_data/val.qrel', sep=' ', index=False, header=False)


def transform_triples(tsk, docid2index):
    train_triples = pd.read_csv('./data/'+tsk+'_data/org_train_triples.tsv',
                                sep='\t',
                                names=['qid','query','pos_docno', 'pos', 'neg_docno', 'neg'])
    new_qid = []
    new_posdocno = []
    new_negdocno = []
    for each_triple in tqdm(train_triples.itertuples()):
        new_qid.append(docid2index[each_triple.qid])
        new_posdocno.append(docid2index[each_triple.pos_docno])
        new_negdocno.append(docid2index[each_triple.neg_docno])

    train_triples['qid'] = new_qid
    train_triples['pos_docno'] = new_posdocno
    train_triples['neg_docno'] = new_negdocno
    train_triples.to_csv('./data/'+tsk+'_data/train_triples.tsv', sep='\t', index=False, header=False)
    

if __name__ == "__main__":
    f = open('./data/docid2index.json')
    docid2index = json.load(f)
    f.close()

    task_names = ['coview', 'coread', 'cocite', 'cite']
    for tsk in task_names:
        transform_runs(tsk, docid2index)
        transform_test_qrel(tsk, docid2index)
        transform_train_qrel(tsk, docid2index)
        transform_val_qrel(tsk, docid2index)
        transform_triples(tsk, docid2index)
        print("Transformation for task {} done!".format(tsk))
