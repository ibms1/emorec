import streamlit as st
from textblob import TextBlob
from PIL import Image, ImageDraw, ImageFont
import emoji
from transformers import pipeline
import re
import io
import tempfile

class SentimentEmojiImageCreator:
    def __init__(self):
        self.sentiment_analyzer = pipeline("sentiment-analysis", 
                                        model="nlptown/bert-base-multilingual-uncased-sentiment")
        
        # Emotion dictionary remains the same as before
        self.emotion_to_emoji = {
            'happiness': '😊', 'joy': '😃', 'love': '❤️', 'admiration': '😍',
            'excitement': '🤩', 'pride': '🦁', 'courage': '💪', 'confidence': '😎',
            # ... (rest of emotions remain the same)
        }
        
        self.emotion_keywords = {
            'happiness': ['happy', 'joyful', 'delighted', 'pleased', 'glad'],
            'joy': ['joy', 'jubilant', 'elated', 'cheerful'],
            # ... (rest of keywords remain the same)
        }

    def detect_emotion_from_text(self, text):
        """Same emotion detection logic as before"""
        # ... (previous emotion detection code)
        pass

    def analyze_sentiment(self, text):
        """Same sentiment analysis logic as before"""
        # ... (previous sentiment analysis code)
        pass

    def create_emoji_frame(self, emoji_char, text, size=(400, 300)):
        """Create a single frame with emoji and text"""
        # Create a new white image
        image = Image.new('RGB', size, 'white')
        draw = ImageDraw.Draw(image)
        
        # Draw emoji (as text) in the center
        draw.text((size[0]/2, size[1]/2-30), emoji_char, 
                 font=ImageFont.truetype("DejaVuSans.ttf", 60),
                 fill='black', anchor="mm")
        
        # Draw text below emoji
        draw.text((size[0]/2, size[1]/2+50), text,
                 font=ImageFont.truetype("DejaVuSans.ttf", 20),
                 fill='black', anchor="mm", align="center")
        
        return image

    def create_animated_gif(self, text):
        """Create animated GIF from text analysis"""
        analysis_results = self.analyze_sentiment(text)
        frames = []
        durations = []
        
        for result in analysis_results:
            if result['sentence'].strip():
                frame = self.create_emoji_frame(
                    result['emoji'],
                    f"{result['emotion']}: {result['sentence'][:50]}..."
                )
                frames.append(frame)
                # Duration in milliseconds (minimum 2000ms)
                duration = int(max(2000, len(result['sentence'].split()) * 500))
                durations.append(duration)
        
        # Save as animated GIF
        output = io.BytesIO()
        if frames:
            frames[0].save(
                output,
                format='GIF',
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=0
            )
            
        return output.getvalue(), analysis_results

def main():
    st.set_page_config(page_title="Emotion to Emoji Animation", page_icon="🎭")
    
    st.title("🎭 Emotion to Emoji Animation")
    st.write("""
    This app analyzes the emotions in your text and creates an animated GIF with matching emojis.
    Enter your text below and see the magic happen!
    """)
    
    creator = SentimentEmojiImageCreator()
    
    text_input = st.text_area(
        "Enter your text here:",
        height=150,
        placeholder="Type or paste your text here..."
    )
    
    if st.button("Create Animation"):
        if text_input.strip():
            with st.spinner("Analyzing emotions and creating animation..."):
                gif_bytes, analysis_results = creator.create_animated_gif(text_input)
                
                # Display analysis results
                st.subheader("Emotion Analysis Results:")
                for result in analysis_results:
                    st.write(f"""
                    **Sentence:** {result['sentence']}
                    **Detected Emotion:** {result['emotion'].title()}
                    **Emoji:** {result['emoji']}
                    ---
                    """)
                
                # Display GIF
                st.subheader("Generated Animation:")
                st.image(gif_bytes, caption="Emotion Animation")
        else:
            st.warning("Please enter some text to analyze.")
    
    st.markdown("""
    ### Features:
    - Creates animated GIF with emoji representations
    - Shows emotion analysis for each sentence
    - Adjusts display time based on sentence length
    """)

if __name__ == "__main__":
    main()