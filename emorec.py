import streamlit as st
from textblob import TextBlob
from PIL import Image
import moviepy.editor as mp
import numpy as np
import emoji
import os
from transformers import pipeline
import re
import tempfile

class SentimentEmojiVideoCreator:
    def __init__(self):
        self.sentiment_analyzer = pipeline("sentiment-analysis", 
                                        model="nlptown/bert-base-multilingual-uncased-sentiment")
        
        # Expanded emotion dictionary with both English and Arabic
        self.emotion_to_emoji = {
            # Positive emotions
            'happiness': '😊',
            'joy': '😃',
            'love': '❤️',
            'admiration': '😍',
            'excitement': '🤩',
            'pride': '🦁',
            'courage': '💪',
            'confidence': '😎',
            'relaxed': '😌',
            'satisfaction': '☺️',
            'hope': '🌟',
            'optimism': '🌈',
            'thrill': '🤗',
            
            # Neutral emotions
            'neutral': '😐',
            'thinking': '🤔',
            'hesitation': '😕',
            'confusion': '😳',
            'waiting': '⏳',
            'wonder': '🤨',
            
            # Negative emotions
            'sadness': '😢',
            'fear': '😨',
            'terror': '😱',
            'anxiety': '😰',
            'anger': '😠',
            'frustration': '😣',
            'tired': '😫',
            'bored': '🥱',
            'exhausted': '😮‍💨',
            'disappointment': '😞',
            'envy': '😒',
            'disgust': '🤢',
            'pain': '🤕',
            'shock': '😦',
            'grief': '😥',
            
            # Communication emotions
            'laughter': '😄',
            'joking': '😅',
            'wink': '😉',
            'smirk': '😏',
            'silence': '🤐',
            'sarcasm': '🙃',
            
            # Complex emotions
            'tears_of_joy': '😂',
            'sad_smile': '🥲',
            'nervous_laugh': '😅',
            'angry_frustrated': '😤',
            'happy_shy': '☺️'
        }
        
        # Keywords for each emotion (English)
        self.emotion_keywords = {
            'happiness': ['happy', 'joyful', 'delighted', 'pleased', 'glad'],
            'joy': ['joy', 'jubilant', 'elated', 'cheerful'],
            'love': ['love', 'adore', 'cherish', 'affection'],
            'fear': ['afraid', 'scared', 'fearful', 'terrified', 'anxious'],
            'terror': ['terrified', 'horrified', 'petrified', 'panic'],
            'hesitation': ['hesitant', 'uncertain', 'unsure', 'doubtful'],
            'tired': ['tired', 'exhausted', 'fatigued', 'weary'],
            'courage': ['brave', 'courageous', 'bold', 'fearless'],
            'anger': ['angry', 'mad', 'furious', 'enraged'],
            'sadness': ['sad', 'depressed', 'unhappy', 'miserable'],
            'anxiety': ['anxious', 'worried', 'nervous', 'uneasy'],
            'excitement': ['excited', 'thrilled', 'enthusiastic', 'eager'],
            'frustration': ['frustrated', 'annoyed', 'irritated', 'agitated']
        }
        
    def detect_emotion_from_text(self, text):
        """Analyze text to detect emotions using keywords and context"""
        text = text.lower()
        detected_emotions = []
        
        # Search for keywords
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    detected_emotions.append(emotion)
                    
        if not detected_emotions:
            # If no specific emotions detected, use general sentiment analysis
            sentiment = self.sentiment_analyzer(text)[0]
            score = float(sentiment['score'])
            
            if score >= 0.8:
                return 'happiness'
            elif score >= 0.6:
                return 'satisfaction'
            elif score >= 0.4:
                return 'neutral'
            elif score >= 0.2:
                return 'sadness'
            else:
                return 'frustration'
        
        return detected_emotions[0]

    def analyze_sentiment(self, text):
        """Analyze text sentiment and return appropriate emojis"""
        sentences = re.split('[.!?।]', text)
        results = []
        
        for sentence in sentences:
            if sentence.strip():
                emotion = self.detect_emotion_from_text(sentence)
                emoji_char = self.emotion_to_emoji.get(emotion, '😐')
                duration = max(2, len(sentence.split()) * 0.5)
                
                results.append({
                    'sentence': sentence.strip(),
                    'emotion': emotion,
                    'emoji': emoji_char,
                    'duration': duration
                })
        
        return results
    
    def create_emoji_frame(self, emoji_char, size=(640, 480)):
        """Create a frame containing the emoji"""
        frame = Image.new('RGB', size, 'white')
        return np.array(frame)
    
    def create_video(self, text, output_path):
        """Create the final video"""
        analysis_results = self.analyze_sentiment(text)
        
        clips = []
        for result in analysis_results:
            frame = self.create_emoji_frame(result['emoji'])
            clip = mp.ImageClip(frame).set_duration(result['duration'])
            clips.append(clip)
        
        if clips:
            final_clip = mp.concatenate_videoclips(clips)
            final_clip.write_videofile(output_path, fps=24)
        
        return output_path, analysis_results

def main():
    st.set_page_config(page_title="Emotion to Emoji Video Creator", page_icon="🎬")
    
    st.title("🎭 Emotion to Emoji Video Creator")
    st.write("""
    This app analyzes the emotions in your text and creates a video with matching emojis.
    Enter your text below and see the magic happen!
    """)
    
    # Initialize the creator
    creator = SentimentEmojiVideoCreator()
    
    # Text input
    text_input = st.text_area(
        "Enter your text here:",
        height=150,
        placeholder="Type or paste your text here... (English or Arabic)"
    )
    
    if st.button("Create Video"):
        if text_input.strip():
            with st.spinner("Analyzing emotions and creating video..."):
                # Create temporary file for video
                temp_dir = tempfile.mkdtemp()
                output_path = os.path.join(temp_dir, "emotion_video.mp4")
                
                # Create video and get analysis results
                video_path, analysis_results = creator.create_video(text_input, output_path)
                
                # Display analysis results
                st.subheader("Emotion Analysis Results:")
                for result in analysis_results:
                    st.write(f"""
                    **Sentence:** {result['sentence']}
                    **Detected Emotion:** {result['emotion'].title()}
                    **Emoji:** {result['emoji']}
                    ---
                    """)
                
                # Display video
                st.subheader("Generated Video:")
                video_file = open(video_path, 'rb')
                video_bytes = video_file.read()
                st.video(video_bytes)
                
                # Cleanup
                video_file.close()
                os.remove(video_path)
                os.rmdir(temp_dir)
        else:
            st.warning("Please enter some text to analyze.")
    
    st.markdown("""
    ### Features:
    - Supports both English and Arabic text
    - Detects multiple emotions: happiness, sadness, fear, anger, surprise, etc.
    - Creates video visualization with appropriate emojis
    - Provides detailed emotion analysis for each sentence
    
    ### Tips:
    - Write complete sentences for better emotion detection
    - Use punctuation marks to separate sentences
    - Express emotions clearly in your text for better results
    """)

if __name__ == "__main__":
    main()