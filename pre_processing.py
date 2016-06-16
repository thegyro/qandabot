from nltk.corpus import stopwords
from bs4 import BeautifulSoup
import sys
import xlrd

# 6th field is the post id in answers
# 4th field is the post id in posts
# 1st field is the post id in questions

data = {}

def func(text, post_id):

	questions = []
	stop = stopwords.words('english')

	
	x = (text.lower()).split(' ')

	soup = BeautifulSoup(text)
	text = soup.getText()

	for each_word in text.split():
		s = ''
		if each_word not in stop:
			s = s + each_word + ' '

	data[post_id].append(text) 

def main():

	# python pre_processing.py data/sample_questions_from_AXC.xls data/sample_answer_from_AXC.xls data/sample_posts_upvotes_downvotes.xls > out.csv
	
	# questions
	xl_workbook = xlrd.open_workbook(sys.argv[1])
	xl_sheet = xl_workbook.sheet_by_index(0)

	for i in range(0, xl_sheet.nrows):

		post_id = xl_sheet.cell(i,0).value
		question = xl_sheet.cell(i,3).value

		if len(question) == 0:
			continue

		#print post_id, question

		if post_id not in data:
			data[post_id] = []

		func(question, post_id)

	# answers
	xl_workbook = xlrd.open_workbook(sys.argv[2])
	xl_sheet = xl_workbook.sheet_by_index(0)
	#print xl_sheet

	for i in range(0, xl_sheet.nrows):
		post_id = xl_sheet.cell(i,5).value
		answer = xl_sheet.cell(i,1).value
		
		if post_id not in data:
			continue
			#data[post_id] = []

		func(answer, post_id)


	# votes
	xl_workbook = xlrd.open_workbook(sys.argv[3])
	xl_sheet = xl_workbook.sheet_by_index(0)
	#print xl_sheet

	for i in range(0, xl_sheet.nrows):
		post_id = xl_sheet.cell(i,3).value
		uvote = xl_sheet.cell(i,0).value
		dvote = xl_sheet.cell(i,1).value
		
		if post_id not in data:
			continue
			#data[post_id] = []

		data[post_id].append(uvote)
		data[post_id].append(dvote)

	for key in data:
		print key, ",",
		
	 	for v in data[key]:
	 		try:
	 			print v, ",",
	 		except:
	 			print v.encode('utf-8'), ",",
	 	print


if __name__ == '__main__':
	main()
