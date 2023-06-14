from transformers import BartTokenizer, BartForConditionalGeneration, BartConfig
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
model = BartForConditionalGeneration.from_pretrained('/home/intern/seungjun/error_model/bartcond_4').to('cuda')

def ErrorSolution_bart(input_string):
    tokenized_input = tokenizer([input_string], return_tensors='pt').to('cuda')
    summary_ids = model.generate(tokenized_input['input_ids'], num_beams = 32, max_length = tokenized_input['input_ids'].size()[1]+10)

    result_arr =[]
    result = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in summary_ids]
    result_arr.extend(result)

    return result

def main():
    print("this is Bart error correction model. if you want to quit, enter quit")
    while True:
        print("Enter message: ", end=' ')
        get_input = input()
        if(get_input =="quit"):
            break
        else:
            print(ErrorSolution_bart(get_input))

if __name__ == "__main__":
    main()