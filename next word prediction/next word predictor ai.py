#importing stuff
import random
import keras
import pandas as pd
import numpy as np
from nltk.tokenize  import RegexpTokenizer

#datasets for next word prediction
text_df = pd.read_csv("C:\python projects/nueral network/next word prediction/fake_or_real_news.csv")
text = list(text_df.text.values)
joined_text = " ".join(text)
partial_text = joined_text[:300000]
#tokenizer 
tokenizer = RegexpTokenizer(r"\w+")
tokens = tokenizer.tokenize(partial_text.lower())
unique_tokens = np.unique(tokens)
unique_token_index = {token: idx for idx,token in enumerate(unique_tokens)}

#input for next word
n_words = 10
input_words = []
next_word = []

for i in range(len(tokens) - n_words):
      input_words.append(tokens[i:i + n_words])
      next_word.append(tokens[i + n_words])

#creating x_train and x_test
x = np.zeros((len(input_words), n_words, len(unique_tokens)), dtype=bool)
y = np.zeros((len(next_word), len(unique_tokens)), dtype=bool)

for i, words in enumerate(input_words):
      for j, word in enumerate(words):
            x[i, j, unique_token_index[word]] = 1
      y[i, unique_token_index[next_word[i]]] = 1
      
#creating model
model = keras.Sequential()
model.add(keras.layers.LSTM(128, input_shape=(n_words, len(unique_tokens)), return_sequences=True))
model.add(keras.layers.LSTM(128))
model.add(keras.layers.Dense(len(unique_tokens)))
model.add(keras.layers.Activation("softmax"))

model.compile(loss="categorical_crossentropy", optimizer=keras.optimizers.RMSprop(learning_rate=0.01), metrics=["accuracy"])

#saver
model_checkpoint = "nueral network/next word prediction/nwp.model.weights.h5"
cp_callback = keras.callbacks.ModelCheckpoint(model_checkpoint,
                                              save_weights_only=True,
                                              verbose=1)

model.load_weights(model_checkpoint)
#model.fit(x, y, batch_size=128, epochs=40, callbacks= [cp_callback], shuffle=True)

#predicting next word def
def predict_next_word(input_text, n_best):
      input_text = input_text.lower()
      x = np.zeros((1, n_words, len(unique_tokens)))
      for i, word in enumerate(input_text.split()):
            x[0, i, unique_token_index[word]] = 1
                  
      prediction = model.predict(x)[0]
      return np.argpartition(prediction, -n_best)[-n_best:]

posible = predict_next_word("he will the election and ", 5)
print([unique_tokens[idx] for idx in posible])

#generating text
def generate_text(input_text, text_length, cretivity=1):
      word_sequence = input_text.split()
      current = 0
      
      for _ in range(text_length):
            sub_sequence = " ".join(tokenizer.tokenize(" ".join(word_sequence).lower())[current: current+n_words])
            
            try:
                  choice = unique_tokens[random.choice(predict_next_word(sub_sequence, cretivity))]       
            except:
                  choice = random.choice(unique_tokens)
            word_sequence.append(choice)
            current += 1
      return " ".join(word_sequence)

print(generate_text("he will have to look into this thing and he", 150, 3))