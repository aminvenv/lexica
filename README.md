# lexica

This repository contains the code used for our work on contextualized term-based ranking.



SciDocs benchmark can be downloaded from [this](https://allenai.org/data/scidocs) link.
our focus is on 4 tasks: co-view, co-read, co-cite, and cite.


Follow the readme in data_helpers folder to prepare the data.


#### Contextualized Term-based ranking
TILDE and TILDEv2 implementations are based on [TILDE](https://github.com/ielab/TILDE) official repository 

##### TILDE
###### Training
```
python train_tilde.py \
--train_path ./data/[tsk]_data/train_pairs.csv \
--save_path ./data/[tsk]_data/v1_models/scibert
```
###### Indexing
```
python indexing.py \
--ckpt_path_or_name ./data/[tsk]_data/v1_models/scibert/TILDE_EPOCH[epoch_num]/ \
--collection_path ./data/docs.tsv \
--output_path ./data/[tsk]_data/v1_index/scibert/passage_embeddings.pkl \
--batch_size [batch-size] 
```
###### Inference
```
python inference.py \
--run_path ./data/[tsk]_data/raw.run \
--query_path ./data/queries.tsv \
--index_path ./data/[tsk]_data/v1_index/scibert/passage_embeddings.pkl \
--save_path ./data/[tsk]_data/v1_reranked/scibert.run
```
##### TILDEv2

###### Training
```
python train_tildev2.py   \
--output_dir ./data/[tsk]_data/v2_models/scibert/   \
--model_name allenai/scibert_scivocab_uncased   \
--save_steps 50000   \
--train_dir ./data/[tsk]_data/tknzd4scibert_train/   \
--q_max_len 512   \
--p_max_len 512   \
--fp16   \
--per_device_train_batch_size 2   \
--train_group_size 8   \
--warmup_ratio 0.1   \
--learning_rate 5e-6   \
--num_train_epochs 5   \
--overwrite_output_dir   \
--dataloader_num_workers 16   \
--cache_dir ./cache
```
###### Indexing

```
python indexingv2.py
--ckpt_path_or_name  ./data/[tsk]_data/v2_models/scibert/ \
--collection_path ./data/tknzd4scibert_docs_tsv/ \
--output_path ./data/[tsk]_data/v2_index/scibert
```

###### Inference
```
python inferencev2.py \
--index_path ./data/[tsk]_data/v2_index/scibert \
--query_path ./data/queries.tsv \
--run_path ./data/[tsk]_data/raw.run \
--save_path ./data/[tsk]_data/v2_reranked/scibert.run
```

##### EXPANDING for TILDEv2 with TILDE

```
python expansion.py \
--corpus_path ./data/docs.tsv \
--output_dir ./data/exp_tknzd4bert_docs_tsv/[tsk]/ \
--topk 200 \
--tilde_checkpoint ./data/[tsk]_data/v1_models/scibert/TILDE_EPOCH[epoch_num]/ \
--tokenizer allenai/scibert_scivocab_uncased
```

##### Config 

Depending on the encoder (BERT/SciBERT), set the correct setup for model, its tokenizer, and vocab size in the .conf file.

##### Traditional Term-based ranking:

###### BM25 and LM


we use Elasticsearch v7.15.1 for the implementation of bm25 and lm.

The preprocessing step for bm25 and lm are based on Elasticsearch features (token filter, and analyzer).
