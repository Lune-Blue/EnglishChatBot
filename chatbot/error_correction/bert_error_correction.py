import torch
import torch.optim as optim
from transformers import EncoderDecoderModel, BertTokenizer, AutoTokenizer


model = EncoderDecoderModel.from_pretrained('/home/intern/seungjun/error_model/bert2bert4').to('cuda')
tokenizer = AutoTokenizer.from_pretrained("google/roberta2roberta_L-24_discofuse")

def ErrorSolution_bert2bert(input_string):
    input_ids = tokenizer("grammar: " + input_string, add_special_tokens=False, return_tensors="pt").input_ids.to('cuda')
    summary_ids = model.generate(input_ids, num_beams = 32, max_length = input_ids.size()[1]+10)

    result_arr =[]
    result = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in summary_ids]
    result_arr.extend(result)

    return result_arr

def main():
    print("this is Bert encoder decoder error correction model. if you want to quit, enter quit")
    while True:
        print("Enter message: ", end=' ')
        get_input = input()
        if(get_input =="quit"):
            break
        else:
            print(ErrorSolution_bert2bert(get_input))

if __name__ == "__main__":
    main()