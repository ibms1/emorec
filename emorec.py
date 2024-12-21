import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from transformers import pipeline
import io
import textwrap

class SentimentEmojiImageCreator:
    def __init__(self):
        # Initialize sentiment analyzer
        try:
            self.sentiment_analyzer = pipeline("sentiment-analysis", 
                                            model="nlptown/bert-base-multilingual-uncased-sentiment")
        except Exception as e:
            st.error(f"Error loading sentiment analyzer: {str(e)}")
            self.sentiment_analyzer = None
        
        # Simplified emotion dictionary for better reliability
        self.emotion_to_emoji = {
            'POSITIVE': '😊',
            'VERY_POSITIVE': '🤗',
            'NEUTRAL': '😐',
            'NEGATIVE': '😔',
            'VERY_NEGATIVE': '😢'
        }

    def analyze_text(self, text):
        """Analyze text and return sentiment results"""
        try:
            # Split text into sentences
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            results = []
            
            for sentence in sentences:
                if self.sentiment_analyzer:
                    # Get sentiment prediction
                    sentiment = self.sentiment_analyzer(sentence)[0]
                    score = float(sentiment['score'])
                    
                    # Map score to emotion
                    if score >= 0.75:
                        emotion = 'VERY_POSITIVE'
                    elif score >= 0.55:
                        emotion = 'POSITIVE'
                    elif score >= 0.45:
                        emotion = 'NEUTRAL'
                    elif score >= 0.25:
                        emotion = 'NEGATIVE'
                    else:
                        emotion = 'VERY_NEGATIVE'
                    
                    # Calculate duration based on sentence length (in milliseconds)
                    duration = max(2000, min(5000, len(sentence.split()) * 500))
                    
                    results.append({
                        'sentence': sentence,
                        'emotion': emotion,
                        'emoji': self.emotion_to_emoji[emotion],
                        'duration': duration
                    })
            
            return results
        except Exception as e:
            st.error(f"Error in text analysis: {str(e)}")
            return []

    def create_frame(self, text, emoji, emotion, size=(500, 300), bg_color='white'):
        """Create a single frame with emoji and text"""
        try:
            # Create new image with white background
            image = Image.new('RGB', size, bg_color)
            draw = ImageDraw.Draw(image)
            
            # Try to use a system font that supports emoji
            try:
                # For emoji
                emoji_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
                # For text
                text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            except:
                # Fallback to default font
                emoji_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
            
            # Draw emoji at the center-top
            emoji_bbox = draw.textbbox((0, 0), emoji, font=emoji_font)
            emoji_width = emoji_bbox[2] - emoji_bbox[0]
            draw.text((size[0]/2 - emoji_width/2, 50), emoji, font=emoji_font, fill='black')
            
            # Draw emotion label
            emotion_text = f"Emotion: {emotion.title()}"
            draw.text((size[0]/2, 140), emotion_text, font=text_font, fill='black', anchor='mm')
            
            # Wrap and draw the sentence text
            wrapper = textwrap.TextWrapper(width=40)
            wrapped_text = wrapper.fill(text)
            draw.text((size[0]/2, 200), wrapped_text, font=text_font, fill='black', anchor='mm', align='center')
            
            return image
        except Exception as e:
            st.error(f"Error creating frame: {str(e)}")
            # Return a blank frame in case of error
            return Image.new('RGB', size, bg_color)

    def create_animation(self, text):
        """Create animated GIF from text analysis"""
        try:
            # Analyze text
            analysis_results = self.analyze_text(text)
            
            if not analysis_results:
                return None, []
            
            frames = []
            durations = []
            
            # Create frames
            for result in analysis_results:
                frame = self.create_frame(
                    result['sentence'],
                    result['emoji'],
                    result['emotion']
                )
                frames.append(frame)
                durations.append(result['duration'])
            
            # Generate GIF
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
            
            return None, analysis_results
            
        except Exception as e:
            st.error(f"Error creating animation: {str(e)}")
            return None, []

def main():
    st.set_page_config(page_title="Emotion Analysis", page_icon="🎭")
    
    st.title("🎭 Text Emotion Analyzer")
    st.write("""
    Analyze the emotions in your text and see them as animated emojis!
    Enter your text below to begin.
    """)
    
    # Initialize creator
    creator = SentimentEmojiImageCreator()
    
    # Get user input
    text_input = st.text_area(
        "Enter your text here:",
        height=150,
        placeholder="Type or paste your text here..."
    )
    
    if st.button("Analyze Emotions"):
        if text_input.strip():
            with st.spinner("Analyzing emotions..."):
                try:
                    gif_bytes, analysis_results = creator.create_animation(text_input)
                    
                    if gif_bytes and analysis_results:
                        # Display results
                        st.subheader("Analysis Results:")
                        for result in analysis_results:
                            st.write(f"""
                            **Text:** {result['sentence']}
                            **Emotion:** {result['emotion'].title()} {result['emoji']}
                            ---
                            """)
                        
                        # Display animation
                        st.subheader("Emotion Animation:")
                        st.image(gif_bytes, caption="Emotion Analysis Animation")
                    else:
                        st.warning("Could not generate animation. Please try different text.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter some text to analyze.")

if __name__ == "__main__":
    main()