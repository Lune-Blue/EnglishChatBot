from happytransformer import HappyTextToText, TTSettings
def ErrorSolutionT5(input_string):
    beam_settings = TTSettings(num_beams=5, min_length=1, max_length =len(input_string))
    error_t5 = HappyTextToText(load_path = "/home/intern/seungjun/error_model/t5")
    result = error_t5.generate_text("grammar: "+input_string, args=beam_settings)
    return result.text

def main():
    print("this is Bart error correction model. if you want to quit, enter quit")
    while True:
        print("Enter message: ", end=' ')
        get_input = input()
        if(get_input =="quit"):
            break
        else:
            print(ErrorSolutionT5(get_input))

if __name__ == "__main__":
    main()