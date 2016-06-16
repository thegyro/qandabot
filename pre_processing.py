from nltk.corpus import stopwords
from bs4 import BeautifulSoup
import sys

# 6th field is the post id in answers
# 4th field is the post id in posts
# 1st field is the post id in questions

data = {}


def func_v(pid_col, u_col, d_col, fp):

	for each_line in fp:
		if pid_col in data:
			data[pid_col].append(u_col)
			data[pid_col].append(d_col)

def func(pid_col, text_col, fp):

	questions = []
	stop = stopwords.words('english')

	for each_line in fp:
		x = (each_line.lower()).split(",")
		post_id, text = x[pid_col], x[text_col]

		#print post_id, text

		if len(text.strip()) == 0:
			return

		if post_id not in data:
			data[post_id] = []

		soup = BeautifulSoup(text)
		text = soup.getText()

		for each_word in text.split():
			s = ''
			if each_word not in stop:
				s = s + each_word + ' '

		data[post_id].append(text) 

def main():
	fp_q = open(sys.argv[1]).readlines()
	fp_a = open(sys.argv[2]).readlines()
	fp_v = open(sys.argv[3]).readlines()

	# func(pid_col, text_col, fp)
	func(0, 3, fp_q) # questions
	func(5, 1, fp_a) # answers

	func_v(2, 0, 1, fp_v)	# vote(pid, upvote, downvote, file)

	for key in data:
		print key, ",",
		
		for v in data[key]:
			try:
				print v, ",",
			except:
				print v.encode('utf-8'), ",",
		print
		#for v in data[key]:
			#print v, ",",
		#print

if __name__ == '__main__':
	main()
