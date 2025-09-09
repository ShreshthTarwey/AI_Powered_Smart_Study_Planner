import google.generativeai as genai
import random
from datetime import datetime

class MotivationService:
    def __init__(self, api_key=None):
        """Initialize Gemini AI with API key"""
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
    
    def generate_personalized_motivation(self, user):
        """Generate personalized motivational message using Gemini API"""
        
        print(f"DEBUG: Model initialized: {bool(self.model)}")
        
        # If no API key or model available, return fallback
        if not self.model:
            print("DEBUG: Using fallback - no model available")
            return self._get_fallback_message(user)
        
        try:
            # Create context about the user
            user_context = self._build_user_context(user)
            print(f"DEBUG: User context: {user_context}")
            
            # Generate prompt for Gemini
            prompt = self._create_motivation_prompt(user_context)
            print(f"DEBUG: Generated prompt")
            
            # Get response from Gemini
            print("DEBUG: Calling Gemini API...")
            response = self.model.generate_content(prompt)
            print(f"DEBUG: AI Response: {response.text}")
            
            # Return the generated message
            return response.text.strip()
            
        except Exception as e:
            print(f"DEBUG: Error generating AI motivation: {e}")
            return self._get_fallback_message(user)
    
    def _build_user_context(self, user):
        """Build context about user for AI"""
        
        # Add some randomness to context
        coding_focus_areas = [
            "problem-solving", "debugging", "learning new frameworks", 
            "building projects", "algorithm practice", "code optimization",
            "skill development", "programming challenges", "web development",
            "software engineering", "data structures", "clean code practices"
        ]
        
        context = {
            'interests': user.interests or "general studies",
            'level': user.get_level(),
            'xp': user.xp,
            'streak': user.streak,
            'total_days': user.total_days_logged or 0,
            'time_of_day': self._get_time_of_day(),
            'focus_area': random.choice(coding_focus_areas),  # Add variety
            'session_number': random.randint(1, 100)  # Add uniqueness
        }
        
        # Determine user's motivation state
        if user.streak >= 14:
            context['state'] = 'streak_master'
        elif user.streak >= 7:
            context['state'] = 'consistent'
        elif user.streak >= 3:
            context['state'] = 'building_habit'
        elif user.get_level() >= 5:
            context['state'] = 'experienced'
        else:
            context['state'] = 'beginner'
            
        return context
    
    def _create_motivation_prompt(self, context):
        """Create AI prompt based on user context"""
        
        # Add random elements for variety
        message_styles = [
            "casual and friendly",
            "inspiring and motivational", 
            "encouraging and supportive",
            "energetic and enthusiastic",
            "wise and mentoring",
            "playful and fun",
            "confident and empowering"
        ]
        
        opening_styles = [
            "Start with an action word or emoji",
            "Begin with a statement about progress", 
            "Open with a coding-related metaphor",
            "Start with current time/situation reference",
            "Begin with an achievement acknowledgment",
            "Open with a future-focused statement",
            "Start with an inspiring coding fact or tip",
            "Begin with XP or level reference creatively",
            "Open with streak motivation uniquely",
            "Start with focus area encouragement"
        ]
        
        random_style = random.choice(message_styles)
        random_opening = random.choice(opening_styles)
        random_number = random.randint(1, 1000)  # Add uniqueness
        
        base_prompt = f"""
You are a supportive coding mentor and motivational coach. Create a unique motivational message for a {context['interests'].lower()} enthusiast (Request #{random_number}).

User Context:
- Interests: {context['interests']}
- Current Level: {context['level']}
- Experience Points: {context['xp']}
- Login Streak: {context['streak']} days
- Total Study Days: {context['total_days']}
- Time: {context['time_of_day']}
- Focus Area: {context['focus_area']}

IMPORTANT REQUIREMENTS:
1. {random_opening}
2. Make it {random_style} in tone
3. Reference their {context['xp']} XP and Level {context['level']} naturally
4. Keep it 1-2 sentences (maximum 140 characters)
5. Use relevant emojis (2-3 max)
6. Make it about {context['interests'].lower()} specifically
7. NEVER start with "Hey coder!", "Hello coder!", "Hi coder!" or similar repetitive greetings
8. Make each message structure completely different
9. Focus on {context['time_of_day']} {context['focus_area']} vibes
10. Be creative and avoid generic openings

STRICTLY AVOID:
- Generic greetings like "Hey", "Hello", "Hi there", "What's up"
- Repetitive openings
- Same sentence structure as previous messages
- Generic programming terms without context
- Starting with "Coder" or "Developer" or similar titles

BE CREATIVE WITH OPENINGS LIKE:
- Start with XP numbers, emojis, actions, or progress statements
- Use metaphors, time references, or achievement celebrations
- Focus on the coding journey, not just greeting the person

"""
        
        # Add state-specific guidance
        if context['state'] == 'streak_master':
            base_prompt += "Celebrate their amazing streak creatively without generic greetings!"
        elif context['state'] == 'consistent':
            base_prompt += "Acknowledge their consistency in a unique way!"
        elif context['state'] == 'building_habit':
            base_prompt += "Encourage their growing coding habit uniquely!"
        elif context['state'] == 'experienced':
            base_prompt += "Challenge them to reach new coding heights!"
        else:
            base_prompt += "Welcome their coding journey with fresh energy!"
            
        return base_prompt
    
    def _get_time_of_day(self):
        """Get current time period"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    def _get_fallback_message(self, user):
        """Fallback messages when AI is unavailable"""
        
        # More varied fallback messages
        messages = {
            'high_streak': [
                f"🔥 {user.streak} day streak! Code mastery in progress!",
                f"⚡ Level {user.get_level()} achieved! Your consistency is inspiring!",
                f"🌟 {user.streak} days of dedication! Keep this momentum flowing!",
                f"🚀 Streak level: {user.streak}! You're building something amazing!",
                f"💪 {user.streak}-day coding warrior! Your persistence pays off!"
            ],
            'medium_streak': [
                f"📈 {user.streak} day streak! Building habits like a pro!",
                f"💻 Level {user.get_level()} unlocked! Your progress is real!",
                f"🎯 {user.streak} days in! You're creating coding momentum!",
                f"⚡ Progress mode: ON! {user.streak} days of consistent effort!",
                f"🔧 Debug your limits! {user.streak} days of growth!"
            ],
            'beginner': [
                "🌱 Every coding expert started with Level 1! You've got this!",
                f"⭐ Level {user.get_level()} initiated! Your learning adventure begins!",
                "💫 Building code skills one commit at a time!",
                "🚀 Compilation successful! Ready for the next challenge?",
                "🎪 Welcome to the coding journey! Every line counts!",
                f"⚡ {user.xp} XP earned! Your programming foundation is growing!"
            ]
        }
        
        if user.streak >= 7:
            category = 'high_streak'
        elif user.streak >= 3:
            category = 'medium_streak'
        else:
            category = 'beginner'
            
        return random.choice(messages[category])

# Initialize service
def get_motivation_service(api_key):
    """Get motivation service instance"""
    return MotivationService(api_key)
