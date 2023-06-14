import nltk
import random

def word_extraction(input_sentence):
    tokens = nltk.word_tokenize(input_sentence)
    tags = nltk.pos_tag(tokens)

    result_arr =[]
    for token in tags:
        if token[1].startswith('V') or token[1].startswith('N'):
            if len(token[0]) > 1:
                result_arr.append(token[0])

    word_ext = random.sample(result_arr,2)
    return word_ext


def main():
    print("this is word extraction model. if you want to quit, enter quit")
    while True:
        print("Enter message: ", end=' ')
        get_input = input()
        if(get_input =="quit"):
            break
        else:
            print(word_extraction(get_input))

if __name__ == "__main__":
    main()