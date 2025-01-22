import csv
import xml.etree.ElementTree as ET

def get_element_text(element):
    """
    Safely extract the text from an XML element. 
    If the element is None, an empty string ('') is returned.
    
    :param element: An XML element (ElementTree object)
    :return: A string of the element's text content or an empty string
    """
    return element.text if element is not None else ''


def convert_xml_to_csv(xml_file, csv_file):
    """
    Convert an XML file to a CSV file based on predefined structure and fields.
    
    Process Overview:
    1. Parse the XML into an ElementTree structure.
    2. For each 'Record' in the XML:
       - Extract various fields (IDs, timestamps, text content, etc.).
       - Collate them into a dictionary 'record_data'.
       - Write them as a row into a CSV file.
    
    :param xml_file: Path to the input XML file (string)
    :param csv_file: Path to the output CSV file (string)
    """
    # 1. Parse the XML
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # 2. Open the output CSV file in write mode
    #    - newline='' to avoid extra blank lines in some environments
    #    - encoding='utf-8' for Unicode support
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        # Define the CSV header. You can modify these column names to suit your data model.
        header = [
            'RecordID',
            'Category',
            'Initial Inquiry',
            'Transcript (User)',
            'Transcript (Support)',
            'Timestamp Started',
            'Timestamp Finished',
            'Message Count',
            'Referer',
            'Wait Time',
            'Session Duration',
            'Resolution'
        ]
        
        # Write the header row into the CSV
        csvwriter.writerow(header)

        # 3. Iterate through each 'Record' in the XML
        for record in root.findall('Record'):
            # We may have multiple <Date> elements in the 'Transcript'. 
            # The last one is assumed to be the end of the conversation.
            date_elements = record.findall('.//Date')
            last_date = date_elements[-1].text if date_elements else ''

            # 4. Extract relevant data fields from the XML using XPath-like lookups
            record_data = {
                'RecordID': get_element_text(record.find('QuestionId')),
                'Category': '',  # Field to be manually assigned or parsed from the XML if needed
                'Initial Inquiry': get_element_text(record.find('Transcript/PatronQuestion/Text')),
                'Transcript (User)': '',
                'Transcript (Support)': '',
                'Timestamp Started': get_element_text(record.find('Transcript/PatronQuestion/Date')),
                'Timestamp Finished': last_date,
                'Message Count': '',  # Will be computed
                'Referer': get_element_text(record.find('Header/QuestionFormField/Data')),  
                # ^ Adjust the path if your 'Referer' is in a different place
                'Wait Time': get_element_text(record.find('Header/WaitTime')),
                'Session Duration': get_element_text(record.find('Header/SessionTime')),
                'Resolution': get_element_text(record.find('Header/Resolution'))
            }

            # If you have a specific field for 'Referer' or 'Category', 
            # you can refine the XPath to match your XML structure. 
            # For example:
            referer_element = record.find('Header/QuestionFormField[Label="Referer"]/Data')
            if referer_element is not None:
                record_data['Referer'] = get_element_text(referer_element)

            category_element = record.find('Header/QuestionFormField[Label="Category"]/Data')
            if category_element is not None:
                record_data['Category'] = get_element_text(category_element)

            # 5. Build user vs. support transcripts and count messages
            user_transcript = []
            support_transcript = []
            message_count = 0

            # Find the 'Transcript' element and iterate through child nodes 
            transcript_element = record.find('Transcript')
            if transcript_element is not None:
                for elem in transcript_element:
                    if elem.tag == 'PatronIncident':
                        # If a user message
                        text_content = get_element_text(elem.find('Text'))
                        user_transcript.append(text_content)
                        message_count += 1
                    elif elem.tag == 'LibraryIncident':
                        # If a support/agent message
                        text_content = get_element_text(elem.find('Text'))
                        support_transcript.append(text_content)
                        message_count += 1

            # Assign the joined transcripts to the record_data dictionary
            record_data['Transcript (User)'] = "\n".join(user_transcript).strip()
            record_data['Transcript (Support)'] = "\n".join(support_transcript).strip()
            record_data['Message Count'] = message_count

            # 6. Write the record data in the correct order to the CSV
            csvwriter.writerow([
                record_data['RecordID'],
                record_data['Category'],
                record_data['Initial Inquiry'],
                record_data['Transcript (User)'],
                record_data['Transcript (Support)'],
                record_data['Timestamp Started'],
                record_data['Timestamp Finished'],
                record_data['Message Count'],
                record_data['Referer'],
                record_data['Wait Time'],
                record_data['Session Duration'],
                record_data['Resolution']
            ])


if __name__ == "__main__":
    # Adjust these file paths as needed. 
    # For example: xml_file_path = "input_data.xml"
    #              csv_file_path = "output_data.csv"
    xml_file_path = "input_data.xml"
    csv_file_path = "output_data.csv"

    # Call the conversion function
    convert_xml_to_csv(xml_file_path, csv_file_path)
