import csv

def split_csv(input_filename, output_filename, limit):
    with open(input_filename, 'r',encoding="utf-8") as input_file, open(output_filename, 'w', newline='',encoding="utf-8") as output_file:
        reader = csv.reader(input_file)
        writer = csv.writer(output_file)

        for i, row in enumerate(reader):
            if i >= limit:
                break
            writer.writerow(row)

input_filename = '../data/vector_database_wikipedia_articles_embedded.csv'
output_filename = '../data/very_small_vector_database_wikipedia_articles_embedded.csv'
limit = 100
split_csv(input_filename, output_filename, limit)
