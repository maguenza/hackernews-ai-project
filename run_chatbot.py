from src.ai.chatbot import HackerNewsChatbot

# Initialize chatbot
chatbot = HackerNewsChatbot()

# Send a message
response = chatbot.chat("What are the top stories from the last week?")
print(response)