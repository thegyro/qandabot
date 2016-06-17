import random
import numpy as np
from keras.models import Sequential
from keras.layers.recurrent import LSTM
from keras.layers.core import Dense, Activation, Dropout

class RNNGenerator:
	def __init__(self, model_name, text):
		self.text = text
		chars = list(set(text))
		max_len = 20
		self.max_len = max_len
		self.chars = chars
		model = Sequential()
		model.add(LSTM(512, return_sequences=True, input_shape=(max_len, len(chars))))
		model.add(Dropout(0.2))
		model.add(LSTM(512, return_sequences=False))
		model.add(Dropout(0.2))
		model.add(Dense(len(chars)))
		model.add(Activation('softmax'))
		model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

		model.load_weights(model_name)

		self.model = model
		self.char_labels = {ch:i for i, ch in enumerate(chars)}
		self.labels_char = {i:ch for i, ch in enumerate(chars)}

	def generate(self, temperature=0.35, seed=None, predicate=lambda x: len(x) < 100):
	    if seed is not None and len(seed) < max_len:
	        raise Exception('Seed text must be at least {} chars long'.format(self.max_len))

	    # if no seed text is specified, randomly select a chunk of text
	    else:
	        start_idx = random.randint(0, len(self.text) - self.max_len - 1)
	        seed = self.text[start_idx:start_idx + self.max_len]

	    sentence = seed
	    generated = sentence

	    while predicate(generated):
	        # generate the input tensor
	        # from the last max_len characters generated so far
	        x = np.zeros((1, self.max_len, len(self.chars)))
	        for t, char in enumerate(sentence):
	            x[0, t, self.char_labels[char]] = 1.

	        # this produces a probability distribution over characters
	        probs = self.model.predict(x, verbose=0)[0]

	        # sample the character to use based on the predicted probabilities
	        next_idx = self.sample(probs, temperature)
	        next_char = self.labels_char[next_idx]

	        generated += next_char
	        sentence = sentence[1:] + next_char

	    return generated


	def sample(self, probs, temperature):
	    """samples an index from a vector of probabilities"""
	    a = np.log(probs)/temperature
	    a = np.exp(a)/np.sum(np.exp(a))
	    return np.argmax(np.random.multinomial(1, a, 1))


if __name__ == "__main__":
	rnn = RNNGenerator("intuit_weights.h5", open('../data/intuit_data.txt').read())
	print rnn.generate()