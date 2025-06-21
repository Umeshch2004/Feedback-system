import json
import os
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_feedback_sentiment(strengths_text, areas_text):
    """Analyze sentiment of feedback using AI"""
    try:
        combined_text = f"Strengths: {strengths_text}\nAreas to improve: {areas_text}"
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a sentiment analysis expert. Analyze the following feedback and determine if it's positive, neutral, or negative. Consider both strengths and improvement areas. Respond with JSON format: {'sentiment': 'positive'|'neutral'|'negative', 'confidence': 0.0-1.0, 'reasoning': 'brief explanation'}"
                },
                {"role": "user", "content": combined_text}
            ],
            response_format={"type": "json_object"},
            max_tokens=200
        )
        
        result = json.loads(response.choices[0].message.content)
        return result['sentiment'], result.get('confidence', 0.8), result.get('reasoning', '')
    except Exception as e:
        print(f"AI sentiment analysis failed: {e}")
        return 'neutral', 0.5, 'AI analysis unavailable'

def generate_feedback_suggestions(employee_role, performance_area):
    """Generate AI-powered feedback suggestions"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an HR expert. Generate constructive feedback suggestions for an employee. Provide both strengths to highlight and areas for improvement. Be specific, actionable, and professional."
                },
                {
                    "role": "user", 
                    "content": f"Generate feedback suggestions for a {employee_role} focusing on {performance_area}. Provide 3 strength points and 3 improvement areas."
                }
            ],
            max_tokens=400
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI feedback generation failed: {e}")
        return "Unable to generate AI suggestions at this time."

def extract_smart_tags(feedback_text):
    """Extract relevant tags from feedback using AI"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Extract relevant professional tags from this feedback. Focus on skills, competencies, and performance areas. Return as JSON array of strings, maximum 5 tags."
                },
                {"role": "user", "content": feedback_text}
            ],
            response_format={"type": "json_object"},
            max_tokens=150
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get('tags', [])
    except Exception as e:
        print(f"AI tag extraction failed: {e}")
        return []

def generate_performance_insights(feedback_history):
    """Generate AI insights from feedback history"""
    try:
        feedback_summary = "\n".join([
            f"Date: {fb['date']}, Sentiment: {fb['sentiment']}, Strengths: {fb['strengths'][:100]}..., Areas: {fb['areas'][:100]}..."
            for fb in feedback_history[-10:]  # Last 10 feedback items
        ])
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Analyze this employee's feedback history and provide actionable insights about their performance trends, growth areas, and recommendations. Be constructive and specific."
                },
                {"role": "user", "content": feedback_summary}
            ],
            max_tokens=300
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI insights generation failed: {e}")
        return "Unable to generate insights at this time."

def improve_feedback_writing(original_feedback):
    """Suggest improvements to feedback writing"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in writing constructive feedback. Improve the following feedback to be more specific, actionable, and professional while maintaining the original intent."
                },
                {"role": "user", "content": original_feedback}
            ],
            max_tokens=300
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI feedback improvement failed: {e}")
        return original_feedback