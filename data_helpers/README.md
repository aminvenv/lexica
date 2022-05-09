

#### For BM25/LM
To prepare the docs tokenized with BERT/SciBERT (for ranking with BM25 and LM), use tokenize_docs.ipynb.

#### For TILDE/TILDEv2
Run the following to create training and validation files for each tasks.

```
python create_train_triplets.py \
--path \path\to\scidocs\folder
```

"\path\to\scidocs\folder" should contain the csv of SciDocs papers "meta_papers.csv" which contains the following columns seperated by '\t:

```
paper_id abstract title
 ```

"\path\to\scidocs\folder" should also contain folders with the names: coview, coread, cocite, cite each of which contains val.qrel and test.qrel for each task.
The output is train/val qrels with raw train triplets in train_triplets.csv.

SciDocs paper id alphanumeric. In order to simply apply TILDE and TILDEv2, we re-index them and create a mapping from the old id to the new index in ‘data/docid2index.json’. Consequently, we need to transform all train/val/test files. To do so, you can use the transform.py

```python transform.py```


Finally, to build train data from train_triples.csv for each task, run the following :
```
python build_train_from_triplets.py   --tokenizer_name allenai/scibert_scivocab_uncased  --file ../data/[tsk]_data/train_triples.tsv  --truncate 512  --json_dir ../data/[tsk]_data/tknzd4scibert_train/
```

The credit of "build_train_from_triplets" goes to [COIL](https://github.com/luyug/COIL).

