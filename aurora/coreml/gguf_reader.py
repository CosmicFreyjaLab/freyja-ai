from gguf.gguf_reader import GGUFReader
import torch.nn as nn


def get_chat_template_str(file_path):
    reader = GGUFReader(file_path)


def parse_gguf_model_from_pretrained(gguf_model_file):
    nn.factory_kwargs(gguf_model_file)
    nn.Embedding.from_pretrained()


if __name__