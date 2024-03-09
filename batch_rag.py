import os
from local_rag import ChatPDF
import sys
from argparse import ArgumentParser

def main():
		parser = ArgumentParser("python batch_rag.py", description="Runs one question about a set of PDFs using an LLM")
		parser.add_argument("-d", "--directory", dest="directory", 
												help="directory containing pdfs to be interrogated", 
												required=True)
		parser.add_argument("-q", "--question", dest="question", 
												help="question to be sent to the LLM about the documents")
		parser.add_argument("-s", "--separately", dest="separately", action="store_true",
												help="process each pdf separately. Use this option if you want to ask the same question to each file.")
		# parser.add_argument("-h", "--help", dest="help", action="store_true",
		# 										help="print this help")

		args = parser.parse_args()

		# check directory
		if not os.path.exists(args.directory):
			sys.exit(f"Directory {args.directory} does not exist")
		if not os.path.isdir(args.directory):
			sys.exit(f"Path {args.directory} is not a directory")

		# check question
		if not args.question:
			sys.stdout.write("No question was provided. Please provide a one line question:")
			sys.stdout.flush()
			args.question = sys.stdin.readline()
		if not args.question:
				sys.exit("No question was provided. Exiting.")

		# manage chat
		chatPdf = ChatPDF()
		if args.separately:
			# process files one by one
			result = ""
			for file in os.listdir(args.directory):
				# process only pdf files
				if file.endswith(".pdf"):
					result += chatPdf.ingest(file).ask(args.question) + '\n'
					chatPdf.empty_database()
		else:	
			# process all files in directory
			result = chatPdf.ingest_directory(args.directory).ask(args.question)

		chatPdf.empty_database()

		print(result)


if __name__ == "__main__":
    main()
