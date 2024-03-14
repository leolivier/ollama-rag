import os
from local_rag import ChatPDF
import sys
from argparse import ArgumentParser
from pathlib import Path
import logging
import json

def get_args():
		parser = ArgumentParser("python batch_rag.py", description="Runs one question about a set of PDFs using an LLM")
		parser.add_argument("-d", "--directory", dest="directory", 
												help="directory containing pdfs to be interrogated", 
												required=True)
		parser.add_argument("-q", "--question", dest="question", 
												help="question to be sent to the LLM about the documents")
		parser.add_argument("-s", "--separately", dest="separately", action="store_true",
												help="process each pdf separately. Use this option if you want to ask the same question to each file.")
		parser.add_argument("-o", "--output", dest="output",	
											help="output file to be written with the results")
		parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
											help="increase output verbosity")
		parser.add_argument("-c", "--config", dest="config",
												help="path to config file")
		parser.add_argument("-l", "--log", dest="log",
											help="path to log file")
		parser.add_argument("-f", "--format", dest="format", default="none", choices=["json", "csv", "none"],
											help="format of the output file. Currently supported: json or csv or none if no particular format is desired (default).")
		return parser.parse_args()

def main():

		# parse args
		args = get_args()

		logging.basicConfig(encoding='utf-8', level=logging.DEBUG if args.verbose else logging.INFO, filename=args.log if args.log else None)

		# check directory
		if not os.path.exists(args.directory):
			sys.exit(f"Directory {args.directory} does not exist")
		if not os.path.isdir(args.directory):
			sys.exit(f"Path {args.directory} is not a directory")

		# check output
		if args.output:
			if os.path.exists(args.output):
				sys.exit(f"Output file {args.output} already exists")
			output_file = open(args.output, "w", newline='\n', encoding='utf-8')
		else:
			output_file = sys.stdout

		# check question
		if not args.question:
			sys.stdout.write("No question was provided. Please provide a question (^D to end):\n")
			sys.stdout.flush()
			args.question = ''
			for line in sys.stdin:
				args.question += line
		if not args.question or args.question == '':
				sys.exit("No question was provided. Exiting.")
		else:
			logging.info(f"Question is: {args.question}")
		# manage chat
		chatPdf = ChatPDF()
		if args.separately:
			# process files one by one
			if args.format == "json":
				output_file.write("[\n")
			for file in os.listdir(args.directory):
				# process only pdf files
				dir = Path(args.directory).resolve()
				if file.endswith(".pdf"):
					absolute_file = os.path.join(dir, file)
					result = chatPdf.ingest(absolute_file).ask(args.question, format=args.format)
					chatPdf.empty_database()
					if args.format == "json":
						try:
							result = json.loads(result)
						except json.decoder.JSONDecodeError:
							logging.info(f"JSON error occurred while processing file {file}:\n{result}\nFile skipped...")
							continue
						result["file"] = file
						out = json.dumps(result) + ','
					elif args.format == "csv":
						out = f'"{file}",{result}'
					else:
						out = f"result for file {file}: {result}"
					logging.info(out)
					output_file.write(f"{out}\n")
					output_file.flush()
			if args.format == "json":
				output_file.write("]\n")
		else:	
			# process all files in directory
			result = chatPdf.ingest_directory(args.directory).ask(args.question, format=args.format)
			if args.format == "json":
				output_file.write (json.dumps(result))
			else:
				output_file.write (result)

		chatPdf.empty_database()


if __name__ == "__main__":
    main()
