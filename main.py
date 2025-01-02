import csv  # CSV library
import xml.etree.ElementTree as ET  # Element Tree library


# takes XML element and returns it as text if element does nto return false
def extract_text(element):
    return element.text if element is not None else ''


# takes CDATA element and returns it as text if CDATA does nto return false
def extract_cdata_text(element):
    return element.text if element is not None else ''


def convert_xml_to_csv(xml_file, csv_file):
    tree = ET.parse(xml_file)  # parses the XML file into an element tree and obtains root element
    root = tree.getroot()

    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:  # opens the csv file in write mode
        csvwriter = csv.writer(csvfile)  # csv writer is created for writing data into the cxv file
        header = [
            'anonymizedclientID/questionID', 'Category (manually assigned)', 'Initial Question',
            'Transcript (student)', 'transcript(librarian)', 'Timestamp chat started', 'timestamp chat finished',
            'Message Count', 'referer', 'wait time', 'duration', 'Resolution'
        ]
        csvwriter.writerow(header)  # writes the first header row

        for record in root.findall('Record'):  # iterates for each record in the XML file
            last_date = None  # creates last_date for later use

            # Find all Date elements within the Transcript
            date_elements = record.findall('.//Date')
            if date_elements:
                last_date = date_elements[-1].text  # Get the text of the last Date element

                # extracts and records data for each category
            record_data = {
                'anonymizedclientID/questionID': extract_text(record.find('QuestionId')),
                'Category (manually assigned)': '',
                'Initial Question': extract_text(record.find('Transcript/PatronQuestion/Text')),
                'Transcript (student)': '',
                'transcript(librarian)': '',
                'Timestamp chat started': extract_text(record.find('Transcript/PatronQuestion/Date')),
                'timestamp chat finished': last_date if last_date else '',  # Use last_date as 'Timestamp chat ended'
                'Message Count': extract_text(record.find('Header/QuestionFormField/Data')),
                'referer': extract_text(record.find('Header/QuestionFormField/Data')),
                'wait time': extract_text(record.find('Header/WaitTime')),
                'duration': extract_text(record.find('Header/SessionTime')),
                'Resolution': extract_text(record.find('Header/Resolution'))
            }
            # creates student_transcript and librarian_transcript for more in depth conversion
            student_transcript = ''
            librarian_transcript = ''
            message_count = 0

            # finds the transcript element and record both Patron and Library incidents within two separate
            # categories while also incrementing message count
            for elem in record.find('Transcript'):
                if elem.tag == 'PatronIncident':
                    student_transcript += f"{elem.find('Text').text}\n"
                    message_count += 1
                elif elem.tag == 'LibraryIncident':
                    librarian_transcript += f"{elem.find('Text').text}\n"
                    message_count += 1

            # records student_transcript elements adn librarian transcripts as well as message count
            record_data['Transcript (student)'] = student_transcript.strip()
            record_data['transcript(librarian)'] = librarian_transcript.strip()
            record_data['Message Count'] = message_count

            # finds referer element and records element if it exists
            referer = record.find('Header/QuestionFormField[Label="Referer"]/Data')
            if referer is not None:
                record_data['referer'] = extract_text(referer)

            # finds category element and records element if it exists
            category = record.find('Header/QuestionFormField[Label="Category"]/Data')
            if referer is not None:
                record_data['category'] = extract_text(category)

            # Write record data to CSV
            csvwriter.writerow([record_data[field] for field in header])


if __name__ == "__main__":
    xml_file_path = "2019.xml"
    csv_file_path = "output.csv"
    convert_xml_to_csv(xml_file_path, csv_file_path)
