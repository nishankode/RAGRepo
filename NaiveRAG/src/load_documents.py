from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import TextLoader
import praw
from dotenv import load_dotenv
from langchain.docstore.document import Document
import os


# Define a function to create a DirectoryLoader for a specific file type
def create_directory_loader(file_type, directory_path):
    
    # Define a dictionary to map file extensions to their respective loaders
    loaders = {
        '.pdf': PyPDFLoader,
        '.txt': TextLoader,
        '.csv': CSVLoader,
    }
    
    directory_loader = DirectoryLoader(
        path=directory_path,
        glob=f"**/*{file_type}",
        loader_cls=loaders[file_type],
    )
    
    return directory_loader


def collect_reddit_posts(subreddit_name, search_keyword, post_limit):

	load_dotenv()

	# Initialize PRAW with your credentials
	reddit = praw.Reddit(
		client_id=os.getenv('REDDIT_CLIENT_ID'),  # Your client_id
		client_secret=os.getenv('REDDIT_CLIENT_SECRET'),  # Your client_secret
		user_agent=os.getenv('REDDIT_UDER_AGENT'),  # Your user_agent
	)


	# Initialize an empty string to store all the content
	all_content = ""

	# Search for posts with the keyword in the specified subreddit
	posts = reddit.subreddit(subreddit_name).search(search_keyword, limit=post_limit)  # You can change the limit
	
	all_posts_documents = []

	# Process the posts and append the content to the all_content variable
	post_count = 1
	for post in posts:

		post_content = ''
		
		post_content += f"Title: {post.title}\n"
		post_content += f"Text: {post.selftext}...\n"  
		
		# Fetch comments for each post and append them to all_content
		post.comments.replace_more(limit=0)  # This removes 'More comments' objects for better processing
		for comment in post.comments.list():
			post_content += f"Comment by {comment.author}: {comment.body[:200]}...\n"  # First 200 characters of comment
		post_content += "\n===\n"

		doc =  Document(page_content=post_content, metadata={"source": f"{post.url} - {post.author} - {post_count}"})

		all_posts_documents.append(doc)

		post_count += 1

	return all_posts_documents



def load_all_documents(folder_path=None, subreddit_name=None, search_keyword=None, post_limit=None):
    
	if folder_path:
		# Create DirectoryLoader instances for each file type
		pdf_loader = create_directory_loader('.pdf', folder_path)
		txt_loader = create_directory_loader('.txt', folder_path)
		csv_loader = create_directory_loader('.csv', folder_path)
		
		# Load the files
		pdf_documents = pdf_loader.load()
		txt_documents = txt_loader.load()
		csv_documents = csv_loader.load()
	
	elif subreddit_name and search_keyword:
		pdf_documents, txt_documents, csv_documents = [], [], []
		reddit_documents = collect_reddit_posts(subreddit_name, search_keyword, post_limit)

	return [pdf_documents, txt_documents, csv_documents, reddit_documents]
	
