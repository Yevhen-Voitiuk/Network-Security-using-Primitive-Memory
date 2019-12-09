import csv

data_position = 4 # Pre-determined column of the csv file with data to process

# Set the name conventions
csv_file_path = '/Users/yevhenvoitiuk/Desktop/Capstone/Wireshark Captures/'
csv_name = 'training data.csv'

# Open the output file
with open(csv_file_path + "PROCESSED " + csv_name, mode="w") as output_csv:
    output_file = csv.writer(output_csv)

    # Open the input file
    with open(csv_file_path + csv_name) as input_csv:
        input_file = csv.reader(input_csv)

        # Modify the first row to have the custom Attack column
        first_row = next(input_file)
        #output_file.writerow(['Attack?'] + first_row) # SageMaker doesn't like header rows
        # Process other rows
        for row in input_file:
            tempRow = row
            if tempRow[data_position].startswith('5', 5): # Goal is to change this substring to '3030' for machine training purposes
                changedData = tempRow[data_position][0:5] + '0' + tempRow[data_position][6:len(tempRow[data_position])]
                print(tempRow[data_position] + "__->__" + changedData)
                tempRow[data_position] = changedData
                tempRow[data_position] = int(tempRow[data_position], 16)
                output_file.writerow([1] + tempRow)
            else:
                if tempRow[data_position] == '':
                    tempRow[data_position] = 0
                else:
                    tempRow[data_position] = int(tempRow[data_position], 16)
                output_file.writerow([0] + tempRow)