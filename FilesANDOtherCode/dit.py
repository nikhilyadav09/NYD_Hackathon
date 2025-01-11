import logging
import pandas as pd

# Initialize logging
logging.basicConfig(level=logging.INFO)

class TranslationPipeline:
    def __init__(self):
        pass

    def clean_translation(self, text: str) -> str:
        try:
            # Find the first colon and retain everything after it
            parts = text.split(":", 1)
            if len(parts) > 1:
                return parts[1].strip()
            return text.strip()
        except Exception as e:
            logging.error(f"Error during cleaning: {e}")
            return text

    def process_file(self, input_file: str, output_file: str):
        try:
            # Load the CSV file
            data = pd.read_csv(input_file)

            # Check if the necessary column exists
            if 'Translation (English)' not in data.columns:
                raise ValueError("The input file must have a 'Translation (English)' column.")

            # Clean each entry in the 'Translation (English)' column
            cleaned_translations = []
            for idx, text in enumerate(data['Translation (English)']):
                if isinstance(text, str):
                    cleaned = self.clean_translation(text)
                    logging.info(f"Original: {text[:100]}... | Cleaned: {cleaned[:100]}...")
                    cleaned_translations.append(cleaned)
                else:
                    cleaned_translations.append("No text provided")

            # Add the cleaned translations to a new DataFrame
            result = pd.DataFrame({
                'Chapter': data['Chapter'],
                'Verse': data['Verse'],
                'Cleaned Translation (English)': cleaned_translations
            })

            # Save the new DataFrame to a new file
            result.to_csv(output_file, index=False)
            logging.info(f"Cleaned translations saved to {output_file}")

        except Exception as e:
            logging.error(f"Error processing file: {e}")

if __name__ == "__main__":
    # File paths
    input_csv = "patanjali_translations_english2.csv"  # Replace with your input file path
    output_csv = "patanjali_translations_cleaned1.csv"  # Replace with your output file path

    # Run the pipeline
    pipeline = TranslationPipeline()
    pipeline.process_file(input_file=input_csv, output_file=output_csv)
