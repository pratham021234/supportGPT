import re
import ftfy

class TextCleaner:
    @staticmethod
    def clean(text: str) -> str:
        if not text:
            return ""
            
        # 0. Fix broken UTF-8 encoding
        text = ftfy.fix_text(text)
        
        # 1. Normalize unicode spaces (e.g. non-breaking spaces)
        text = text.replace('\xa0', ' ')
        
        # 2. Remove invisible characters (zero-width spaces, etc.) and control characters
        text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        # 3. Strip basic HTML noise and scripts if leaked
        text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<style.*?>.*?</style>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<.*?>', '', text)
        
        # 4. Collapse multiple spaces into a single space
        text = re.sub(r'[ \t]+', ' ', text)
        
        # 5. Collapse multiple newlines into a maximum of two newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 6. Remove tracking links or excessive URLs (optional, based on requirement)
        # We can just leave them as is for semantic meaning, but remove query noise
        text = re.sub(r'(https?://[^\s]+)\?[^\s]+', r'\1', text)
        
        # 7. Strip leading and trailing whitespace
        return text.strip()
