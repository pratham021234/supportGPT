import re

class TextCleaner:
    @staticmethod
    def clean(text: str) -> str:
        if not text:
            return ""
        
        # 1. Normalize unicode spaces (e.g. non-breaking spaces)
        text = text.replace('\xa0', ' ')
        
        # 2. Remove invisible characters (zero-width spaces, etc.)
        text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)
        
        # 3. Collapse multiple spaces into a single space
        text = re.sub(r'[ \t]+', ' ', text)
        
        # 4. Collapse multiple newlines into a maximum of two newlines (to preserve paragraphs)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 5. Strip leading and trailing whitespace
        return text.strip()
