import torch
from torch import nn
import pickle 
import argparse

def load_model(model_path):
    if model_path.endswith(".pth"):
        model = torch.load(model_path)
    elif model_path.endswith(".pkl"):
        model = pickle.load(model_path)
    else:
        raise TypeError(f"File type {model_path.split('.')[-1]} cannot be loaded.")
    return model

def inference(model, data):
    if isinstance(model, nn.Module):
        logits = model(data)
        _, pred = torch.max(logits, 1)
        return pred
    else:
        return model.predict(data)
    
def format(prediction):
    # format the output
    return prediction
    
def main(model_path, data):
    model = load_model(model_path)
    output = inference(model, data)
    return format(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model_path")
    parser.add_argument("data")
    args = parser.parse_args()
    
    main(args)