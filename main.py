import csv

# We are define an function to read csv file and turn into dictionary
def read_csv_to_dict(csv_file):
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
# We are define the main method
def main():
    # We are defining the csv_file path
    csv_file = 'Mandarin to Cantonese - Sheet1.csv'
    mandarin_cantonese_dict = read_csv_to_dict(csv_file)
    # We are printing out to check the result
    print(mandarin_cantonese_dict)
    
    
# We are define the entrypoint of the function
if __name__ == "__main__":
    main()