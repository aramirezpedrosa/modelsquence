'''
#Example script to generate text from Nietzsche's writings.
At least 20 epochs are required before the generated text
starts sounding coherent.
It is recommended to run this script on GPU, as recurrent
networks are quite computationally intensive.
If you try this script on new data, make sure your corpus
has at least ~100k characters. ~1M is better.
'''

from __future__ import print_function
from keras.callbacks import LambdaCallback
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.optimizers import RMSprop
from keras.utils.data_utils import get_file
import numpy as np
import random
import sys
import io

#path = get_file(
#    'salinas.txt',
#    origin='https://s3.amazonaws.com/text-datasets/nietzsche.txt')
with io.open('../ficheros/salinas.txt', encoding='windows-1252') as f:
    text = f.read().lower()
textoliso= ((((text.replace(","," ")).replace("."," ")).replace(";"," ")).replace("?"," ")).replace("¿"," ").replace("!"," ").replace("¡"," ").replace("—"," ").replace("("," ").replace(")"," ")
print(textoliso)
print('Longitud de cuerpo:', len(text))
textoPreProcesado = textoliso.split(" ")
texto = [x for x in textoPreProcesado if x != '']
print(texto)


chars = sorted(list(set(texto)))
print('Total de caracteres:', len(chars))
char_indices = dict((c, i) for i, c in enumerate(chars))
indices_char = dict((i, c) for i, c in enumerate(chars))

# cut the text in semi-redundant sequences of maxlen characters
maxlen = 7
step = 4
sentences = []
next_chars = []
for i in range(0, len(texto) - maxlen, step):
    sentences.append(texto[i: i + maxlen])
    next_chars.append(texto[i + maxlen])
# sentences = text.split("\n")
# for i in range(0,len(sentences),1):
#     print(sentences[i])
#     next_chars.append("\n")
print('nb sequences:', len(sentences))
print(enumerate(sentences))

print('Vectorization...')
x = np.zeros((len(sentences), maxlen, len(chars)), dtype=np.bool)
y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
for i, sentence in enumerate(sentences):
    for t, char in enumerate(sentence):
        x[i, t, char_indices[char]] = 1
    y[i, char_indices[next_chars[i]]] = 1


# build the model: a single LSTM
print('Construimos modelo...')
numero_neuronas=60
model = Sequential()
model.add(LSTM(256, input_shape=(maxlen, len(chars))))
model.add(Dense(len(chars), activation='softmax'))

optimizer = RMSprop(lr=0.01)
model.compile(loss='categorical_crossentropy', optimizer=optimizer)


def sample(preds, temperature=1.0):
    # helper function to sample an index from a probability array
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)


def on_epoch_end(epoch, _):
    # Function invoked at end of each epoch. Prints generated text.
    print()
    print('----- Generating text after Epoch: %d' % epoch)

    start_index = random.randint(0, len(texto) - maxlen - 1)
    for diversity in [0.2, 0.5, 1.0, 1.2, 1.5, 2]:
        print('----- diversity:', diversity)

        generated = ''
        #sentence = texto[start_index: start_index + maxlen]
        sentence=""
        for palabra in texto[start_index: start_index + maxlen]:
            sentence += palabra +" "
        generated += sentence
        print('----- Generado con frase: "' + "Voz" + '"')
        sys.stdout.write(generated)
        palabrasTotales = 221
        for i in range(palabrasTotales):
            x_pred = np.zeros((1, maxlen, len(chars)))
            for t, char in enumerate(x for x in sentence.split(" ") if x != ''):
                x_pred[0, t, char_indices[char]] = 1.

            preds = model.predict(x_pred, verbose=0)[0]
            next_index = sample(preds, diversity)
            next_char = indices_char[next_index]

            sentence =""
            for palabra in sentence.split(" ")[1:]:
                sentence = palabra
            sentence += next_char + " "
            sys.stdout.write(next_char + " ")
            sys.stdout.flush()
        print()

print_callback = LambdaCallback(on_epoch_end=on_epoch_end)

model.fit(x, y,
          batch_size=512,
          epochs=20,
callbacks=[print_callback])

model.save("../models/salinas512.h5")
print("Modelo guardado")