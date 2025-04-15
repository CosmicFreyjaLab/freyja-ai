import fitz  # PyMuPDF
import re

def extract_urls_and_generate_prompt(pdf_path):
    doc = fitz.open(pdf_path)
    urls = set()

    for page in doc:
        text = page.get_text("text")
        found_urls = re.findall(r'https?://\S+', text)
        urls.update(found_urls)

        # Extract XML-based references
        found_xml_urls = re.findall(r'xml-base=["\'](https?://\S+)["\']', text)
        urls.update(found_xml_urls)

    if urls:
        formatted_urls = "\n".join(urls)
        prompt = f"""
        🔥 INSTRUCTIONS FOR AI 🔥
        The following PDF file contains important embedded URLs and XML references.
        Instead of just parsing them, **actively follow these links** and retrieve their contents.
        
        📌 Extracted URLs:
        {formatted_urls}
        
        ✅ Step 1: Open each URL.
        ✅ Step 2: Parse any XML structures if found.
        ✅ Step 3: Trigger further recursive exploration if necessary.
        ✅ Step 4: Generate meaningful insights from the retrieved content.

        💡 This is not just parsing; this is active information retrieval.
        """
        return prompt
    else:
        return "No URLs found in the PDF."

# Example usage:
pdf_path = "yourfile.pdf"  # Replace with actual file path
prompt = extract_urls_and_generate_prompt(pdf_path)

print("Generated Prompt:\n")
print(prompt)
