import sys

def generate_txt_from_csv(filename, q = True, a = False):
	for l in open(filename):
		sentences = l.strip().split('\t')
		if(len(sentences) >= 3):
			question = sentences[1]
			answer = sentences[2]
			if q and a:
				print question
				print answer
			else if a:
				print answer
			else:
				print question
			


if __name__ == "__main__":
	generate_txt_from_csv(sys.argv[1])
