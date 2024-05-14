import csv
# We are define an function to read csv file and turn into dictionary
def read_csv_to_dict(csv_file):
    # create a empty dictionary to store
    mandarin_cantonese_dict = {}
    # we are open the csv file
    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        # We are using DictReader method
        reader = csv.DictReader(file)
        # We are taking care of each row
        for row in reader:
            mandarin = row['Mandarin']
            cantonese = row['Cantonese']
            mandarin_cantonese_dict[mandarin] = cantonese
        return mandarin_cantonese_dict
    
# We are creating a function to turn text into strings
def read_txt_to_string(txt_file):
    # We first need an empty string
    articles = ""
    with open(txt_file, 'r', encoding='utf-8') as file:
        # We are read each line in file
        for line in file:
            articles += line
    # We are Return the concatenated string containing the contents of the file
    return articles
# We are creating another function to replace words in the article
def replace_names(articles, mandarin_cantonese_dict):
    for original, new in mandarin_cantonese_dict.items():
        articles = articles.replace(original,new)
    return articles
        
# We are define the main method
def main():
    # We are defining the csv_file path
    csv_file = 'Mandarin to Cantonese - Sheet1.csv'
    mandarin_cantonese_dict = read_csv_to_dict(csv_file)
    text_file = 'article.txt'
    article = read_txt_to_string(text_file)
    modified_article = replace_names(article,mandarin_cantonese_dict)
    # We are printing out to check the result
    print(mandarin_cantonese_dict)
    print(article)
    print(modified_article)
    
    
# We are define the entrypoint of the function
if __name__ == "__main__":
    main()