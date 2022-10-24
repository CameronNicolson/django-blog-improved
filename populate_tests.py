"""Populate Tests 

posts_fixtures - is a Path object with 
file path of testing data for post models.
e.g. ("/home/user/django/blog/fixtures)

The `insert_dummy_text_to_file` puts placeholder text inside files with
matching keywords. The keyword is lorem(<num-of-paragraphs>).
Examples:
* lorem(1) - adds 1 paragraph of placeholder text
* lorem(5) - add 5 paragraphs of placeholder text 
"""

from django.utils.lorem_ipsum import paragraphs

from pathlib import Path
import re

post_fixtures = Path.cwd() / "blog" / "fixtures" / "posts.yaml"

def insert_dummy_text_to_file(path):

    if not path.is_file():
        raise ValueError("file not found")
        return None
    
    with open(path) as file_contents:
        replacement = ""
        for line in file_contents:
            match = re.search("content: lorem\((\d{1})\)$" , line)
            if match:
                num_of_paragraphs = int(match.group(1))
                paragraph_list = paragraphs(num_of_paragraphs)
                dummy_str = ''.join(f"{line}" for line in paragraph_list)
                line = re.sub("lorem\(\d\)", dummy_str, line)
                replacement = replacement + line
                continue
            replacement = replacement + line
    file_contents.close()
    # opening the file in write mode
    fout = open(post_fixtures, "w")
    fout.write(replacement)
    fout.close()

def main():
    insert_dummy_text_to_file(post_fixtures)
    print("Populated test data successful!")

if __name__ == "__main__":
    main()