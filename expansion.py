from argparse import ArgumentParser
from transformers import BertLMHeadModel, BertTokenizer, DataCollatorWithPadding
import torch
import json
import re
from nltk.corpus import stopwords
from tqdm import tqdm
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
import numpy as np
import os
import configparser


DEVICE = torch.device('cuda:1' if torch.cuda.is_available() else 'cpu')


config = configparser.ConfigParser()
config.read('./config.conf')
MODEL_TYPE = config.get('Train', 'MODEL_NAME')
MODEL_VOCAB_SIZE = config.getint('Train', 'MODEL_VOCAB_SIZE')
TOKENIZER = config.get('Train', 'TOKENIZER')


def clean_vacab(tokenizer, do_stopwords=True):
    if do_stopwords:
        stop_words = set(stopwords.words('english'))
        # keep some common words in ms marco questions
        # stop_words.difference_update(["where", "how", "what", "when", "which", "why", "who"])
        stop_words.add("definition")

    vocab = tokenizer.get_vocab()
    tokens = vocab.keys()

    good_ids = []
    bad_ids = []

    for stop_word in stop_words:
        ids = tokenizer(stop_word, add_special_tokens=False)["input_ids"]
        if len(ids) == 1:
            bad_ids.append(ids[0])

    for token in tokens:
        token_id = vocab[token]
        if token_id in bad_ids:
            continue

        if len(token) > 1:
            if token[0] == '#':
                good_ids.append(token_id)
        else:
            if not re.match("^[A-Za-z0-9_-]*$", token):
                bad_ids.append(token_id)
            else:
                good_ids.append(token_id)
    bad_ids.append(2015)  # add ##s to stopwords
    return good_ids, bad_ids


class MarcoEncodeDataset(Dataset):
    def __init__(self, path, tokenizer, p_max_len=512):
        self.tok = tokenizer
        self.p_max_len = p_max_len
        self.passages = []
        self.pids = []

        with open(path, 'rt') as fin:
            lines = fin.readlines()
            for line in tqdm(lines, desc="Loading collection"):
                pid, passage = line.split("\t")
                self.passages.append(passage)
                self.pids.append(pid)

    def __len__(self):
        return len(self.passages)

    def __getitem__(self, item):
        psg = self.passages[item]
        encoded_psg = self.tok.encode_plus(
            psg,
            max_length=self.p_max_len,
            truncation='only_first',
            return_attention_mask=False,
        )
        encoded_psg.input_ids[0] = 1  # TILDE use token id 1 as the indicator of passage input.
        return encoded_psg

    def get_pids(self):
        return self.pids


def main(args):
    model = BertLMHeadModel.from_pretrained(args.tilde_checkpoint, cache_dir='./cache')
    tokenizer = BertTokenizer.from_pretrained(args.tokenizer, use_fast=True, cache_dir='./cache')
#     model = BertLMHeadModel.from_pretrained("ielab/TILDE", cache_dir='./cache')
#     tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', use_fast=True, cache_dir='./cache')
    model.eval().to(DEVICE)
    with open(os.path.join(args.output_dir, f"collection-tilde-expanded-top{args.topk}.jsonl"), 'w+') as wf:
        _, bad_ids = clean_vacab(tokenizer)

        encode_dataset = MarcoEncodeDataset(args.corpus_path, tokenizer)
        encode_loader = DataLoader(
            encode_dataset,
            batch_size=args.batch_size,
            collate_fn=DataCollatorWithPadding(
                tokenizer,
                max_length=512,
                padding='max_length'
            ),
            shuffle=False,  # important
            drop_last=False,  # important
            num_workers=args.num_workers,
        )

        pids = encode_dataset.get_pids()
        COUNTER = 0
        for batch in tqdm(encode_loader):
            passage_input_ids = batch.input_ids.numpy()
            batch.to(DEVICE)
            with torch.no_grad():
                logits = model(**batch, return_dict=True).logits[:, 0]
                batch_selected = torch.topk(logits, args.topk).indices.cpu().numpy()

            expansions = []
            for i, selected in enumerate(batch_selected):
                expand_term_ids = np.setdiff1d(np.setdiff1d(selected, passage_input_ids[i], assume_unique=True),
                                               bad_ids, assume_unique=True)
                expansions.append(expand_term_ids)

            for ind, passage_input_id in enumerate(passage_input_ids):
                passage_input_id = passage_input_id[passage_input_id != 0][1:]  # skip the first special token
                

                excess_cond = 512-len(passage_input_id)
                    
                if excess_cond > 0:
                    expanded_passage = np.append(passage_input_id, expansions[ind][0:excess_cond]).tolist()
                else:
                    expanded_passage = passage_input_id.tolist()
#                 expanded_passage = np.append(passage_input_id, expansions[ind]).tolist()

                if args.store_raw:
                    expanded_passage = tokenizer.decode(expanded_passage)

                temp = {
                    "pid": pids[COUNTER],
                    "psg": expanded_passage
                }
                COUNTER += 1
                wf.write(f'{json.dumps(temp)}\n')


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--corpus_path', required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument('--topk', default=200, type=int, help='k tokens with highest likelihood to be expanded to the original document. '
                                                              'NOTE: this is the number before filtering out expanded tokens that already in the original document')
    parser.add_argument('--batch_size', default=64, type=int)
    parser.add_argument('--num_workers', default=8, type=int)
    parser.add_argument('--store_raw', action='store_true', help="True if you want to store expanded raw text. False if you want to expanded store token ids.")
    parser.add_argument('--tilde_checkpoint', required=True)
    parser.add_argument('--tokenizer', required=True)
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    main(args)
