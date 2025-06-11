---
library_name: peft
license: gemma
base_model: google/gemma-2b
tags:
- generated_from_trainer
model-index:
- name: GemmaCare0625-LoRA
  results: []
---

<!-- This model card has been generated automatically according to the information the Trainer had access to. You
should probably proofread and complete it, then remove this comment. -->

# GemmaCare0625-LoRA

This model is a fine-tuned version of [google/gemma-2b](https://huggingface.co/google/gemma-2b) on an unknown dataset.
It achieves the following results on the evaluation set:
- Loss: 3.9015

## Model description

More information needed

## Intended uses & limitations

More information needed

## Training and evaluation data

More information needed

## Training procedure

### Training hyperparameters

The following hyperparameters were used during training:
- learning_rate: 0.0002
- train_batch_size: 3
- eval_batch_size: 3
- seed: 42
- optimizer: Use paged_adamw_32bit with betas=(0.9,0.999) and epsilon=1e-08 and optimizer_args=No additional optimizer arguments
- lr_scheduler_type: linear
- num_epochs: 30
- mixed_precision_training: Native AMP

### Training results

| Training Loss | Epoch | Step | Validation Loss |
|:-------------:|:-----:|:----:|:---------------:|
| 4.3481        | 1.0   | 315  | 4.2860          |
| 4.1231        | 2.0   | 630  | 4.1076          |
| 4.0485        | 3.0   | 945  | 4.0318          |
| 4.0159        | 4.0   | 1260 | 4.0187          |
| 3.9967        | 5.0   | 1575 | 3.9902          |
| 3.9849        | 6.0   | 1890 | 3.9780          |
| 3.9692        | 7.0   | 2205 | 3.9754          |
| 3.9593        | 8.0   | 2520 | 3.9562          |
| 3.9467        | 9.0   | 2835 | 3.9586          |
| 3.9519        | 10.0  | 3150 | 3.9519          |
| 3.9362        | 11.0  | 3465 | 3.9368          |
| 3.9267        | 12.0  | 3780 | 3.9326          |
| 3.9249        | 13.0  | 4095 | 3.9310          |
| 3.9048        | 14.0  | 4410 | 3.9285          |
| 3.9167        | 15.0  | 4725 | 3.9259          |
| 3.9144        | 16.0  | 5040 | 3.9193          |
| 3.9154        | 17.0  | 5355 | 3.9191          |
| 3.9214        | 18.0  | 5670 | 3.9150          |
| 3.8995        | 19.0  | 5985 | 3.9151          |
| 3.9136        | 20.0  | 6300 | 3.9108          |
| 3.9091        | 21.0  | 6615 | 3.9103          |
| 3.9007        | 22.0  | 6930 | 3.9079          |
| 3.9027        | 23.0  | 7245 | 3.9079          |
| 3.8953        | 24.0  | 7560 | 3.9062          |
| 3.9039        | 25.0  | 7875 | 3.9069          |
| 3.9015        | 26.0  | 8190 | 3.9039          |
| 3.8897        | 27.0  | 8505 | 3.9041          |
| 3.8901        | 28.0  | 8820 | 3.9030          |
| 3.8848        | 29.0  | 9135 | 3.9020          |
| 3.8844        | 30.0  | 9450 | 3.9015          |


### Framework versions

- PEFT 0.15.2
- Transformers 4.52.4
- Pytorch 2.7.1+cu126
- Datasets 3.6.0
- Tokenizers 0.21.1