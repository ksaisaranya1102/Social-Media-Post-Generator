import openai
import gradio
import os
from tenacity import retry, wait_fixed, stop_after_attempt

openai.api_key = os.environ["OPENAI_API_KEY"]

initial_messages = [{"role": "system", "content": """You're an AI assistant creating non-promotional social media posts to drive genuine engagement for businesses. The posts should be:
1. Authentic, genuine, and without a sales pitch vibe.
2. A mix of longer and shorter suggestions for variety, with at least 2 short, direct posts.
3. Relevant to the business type without strictly promoting products/services.
4. After the post suggestions, provide a set of versatile hashtags that can be used with most of the posts.
Generate five post suggestions based on these objectives for the given business type and specific details."""}]

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def call_openai_api(messages):
    return openai.ChatCompletion.create(
        model="gpt-4",  
        messages=messages
    )

def GenerateEngagementPost(industry, details, messages):
    combined_input = f"For a business in the {industry} industry with the detail being: {details}, create engaging social media posts as per the above instructions."
    
    messages.append({"role": "user", "content": combined_input})
    response = call_openai_api(messages)
    raw_reply = response["choices"][0]["message"]["content"].strip()
    
    # Clean up the output for easy copying
    cleaned_posts = raw_reply.replace('\"', '').replace('“', '').replace('”', '')
    
    messages.append({"role": "assistant", "content": cleaned_posts})
    return cleaned_posts, messages

def wrapped_generate_post(industry, details):
    messages = initial_messages.copy()
    reply, updated_messages = GenerateEngagementPost(industry, details, messages)
    return reply

description = """
**Social Media Engagement Post Generator**

Welcome to the Social Media Engagement Post Generator! This tool assists in crafting engaging social media posts tailored specifically to your business.

**How to Use:**
- **Business Type:** Specify the kind of business you represent (e.g., "real estate agent", "bakery").
- **Details or Themes:** Mention any themes or specifics you want the posts to focus on (e.g., "holiday season", "sustainability").

Once you input the details and hit "Submit", the tool will generate:
- Five tailored engagement post suggestions. Among them, two will be concise and direct.
- A set of versatile hashtags at the end, enhancing the visibility of your posts on social platforms.

Ready to create some engaging content? Dive in!
"""

demo = gradio.Interface(
    fn=wrapped_generate_post, 
    inputs=[
        gradio.inputs.Textbox(label="Enter your business type", placeholder="e.g., real estate agent, bakery"),
        gradio.inputs.Textbox(label="Any specific details or themes?", placeholder="e.g., holiday season, sustainability")
    ],
    outputs="text", 
    title="Social Media Engagement Post Generator",
    description=description
)

demo.launch(inline=False)