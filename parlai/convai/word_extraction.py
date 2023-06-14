import nltk
import random
from nltk.corpus import stopwords 

def word_extraction(input_sentence):
    tokens = nltk.word_tokenize(input_sentence)
    tags = nltk.pos_tag(tokens)
    stop_words = set(stopwords.words('english'))

    result_arr =[]
    for token in tags:
        if token[1].startswith('V') or token[1].startswith('N'):
            if(len(token[0]) > 2 and token[0] not in stop_words):
                result_arr.append(token[0])

    print("token len is ",len(tokens))
    print("input sentence is", input_sentence)
    

    if(len(result_arr)==0):
        return "", ""
    elif(len(result_arr)==1):
        return result_arr[0], " "
    else:
        word_ext = random.sample(result_arr,2)
        return word_ext[0],word_ext[1]


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