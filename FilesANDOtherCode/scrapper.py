import requests
from bs4 import BeautifulSoup
import csv

# Output CSV file
output_file = "patanjali_translations_hindi.csv"

# Initialize CSV file with headers
with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Chapter", "Verse", "Translation (Hindi)"])  # Headers

# Function to extract content from a specific URL using BeautifulSoup
def extract_translation(url, chapter, verse):
    try:
        print(f"Fetching URL: {url}")
        # Define headers to mimic a browser
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Connection": "keep-alive",
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to fetch URL: {url} (Status Code: {response.status_code})")
            return None

        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Locate the Hindi tab content
        hindi_tab_content = soup.find("div", class_="tabs-cont-box active")
        if hindi_tab_content:
            content = hindi_tab_content.get_text(strip=True)
            print(f"Translation extracted: {content[:50]}... (truncated for display)")
            return content
        else:
            print("Hindi content not found.")
            return None

    except Exception as e:
        print(f"Error extracting data for Chapter {chapter}, Verse {verse}: {e}")
        return None

# Main script to scrape translations in Hindi
def scrape_patanjali_translations_hindi():
    print("Starting the scraping process for Hindi translations.")

    chapter = 1
    lst=["samadhipada1","sadhana-pada-2","vibhooti-pada-3","kaivalya-pada-4"]
    for chapters in lst:  # Loop through chapters
        verse = 1
        while True:  # Loop through verses in a chapter
            url = f"https://patanjaliyogasutra.in/{chapters}-{verse}/"
            print(f"Processing Chapter {chapter}, Verse {verse}.")

            # Extract translation
            translation = extract_translation(url, chapter, verse)
            if translation is None or translation.strip() == "":
                print(f"No data found for Chapter {chapter}, Verse {verse}. Moving to the next chapter.")
                break  # Move to the next chapter

            # Append data to the CSV file
            with open(output_file, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([chapter, verse, translation])

            print(f"Saved Chapter {chapter}, Verse {verse} to CSV.")

            # Increment verse
            verse += 1

        print(f"Finished Chapter {chapter}. Moving to the next chapter.")
        # Increment chapter
        chapter += 1

    print("Scraping completed.")

# Run the script
if __name__ == "__main__":
    scrape_patanjali_translations_hindi()
