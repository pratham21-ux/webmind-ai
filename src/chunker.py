import re

class TextChunker:
    def __init__(self, chunk_size=500, overlap=50):
        # Validation to prevent infinite loops
        if overlap >= chunk_size:
            raise ValueError("Overlap must be smaller than chunk size to progress through text.")
        
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_text(self, text):
        """
        Splits text into chunks by words with a sliding window.
        Includes internal cleanup to ensure web data stays readable.
        """
        # 1. Clean up whitespace (tabs, newlines, multiple spaces)
        text = re.sub(r'\s+', ' ', text).strip()
        
        words = text.split()
        if not words:
            return []

        chunks = []
        i = 0

        # 2. Sliding window logic
        while i < len(words):
            # Take a slice of words based on chunk_size
            chunk_slice = words[i : i + self.chunk_size]
            chunk_text = " ".join(chunk_slice)
            
            chunks.append(chunk_text)
            
            # Move the pointer forward by (chunk_size - overlap)
            i += (self.chunk_size - self.overlap)
            
            # 3. Stop condition: If the next start index is beyond the total words
            if i >= len(words):
                break
                
        return chunks

# --- Test Run with Universal Data ---
if __name__ == "__main__":
    # Sample generic web data showcasing the chunking and overlap mechanics
    test_data = """
    WebMind AI is a universal Retrieval-Augmented Generation system designed 
    to process any website. It uses a dynamic sliding window approach to 
    ensure context is never lost between text boundaries. By overlapping 
    the text segments, the Language Model maintains a continuous understanding 
    of long-form documentation, news articles, and complex data sets.
    """
    
    # We use a smaller size here just to demonstrate the overlap in the console
    chunker = TextChunker(chunk_size=15, overlap=5) 
    result = chunker.split_text(test_data)
    
    print(f"--- Generated {len(result)} Chunks ---\n")
    for idx, c in enumerate(result):
        # Highlighting the overlap by showing the start of each chunk
        print(f"Chunk {idx+1} (Words: {len(c.split())}):")
        print(f"Text: {c}\n")