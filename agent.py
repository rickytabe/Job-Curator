import os
import feedparser
import datetime
from google import genai

def fetch_jobs(rss_url):
    # Parses the We Work Remotely programming jobs feed
    feed = feedparser.parse(rss_url)
    jobs = []
    # Grab the 5 most recent job postings
    for entry in feed.entries[:5]:
        jobs.append({
            "title": entry.title,
            "link": entry.link,
            "description": entry.description
        })
    return jobs

def curate_with_gemini(jobs):
    # Initialize the Gemini SDK
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    prompt = f"""
    You are an expert technical recruiter. I have a list of {len(jobs)} recent remote software dev jobs.
    Review them, summarize the key requirements, categorize the tech stack (e.g., Frontend, Backend, Fullstack, Web3), 
    and rate them (1 to 5 stars) based on how modern the tech stack is.
    
    Output a clean Markdown document. Include a catchy title for today, and create a 
    bulleted section for each job including: Title, Link, Stack Category, Summary, and Rating.
    
    Raw Job Data:
    {jobs}
    """
    
    # Generate the curation using the fast Flash model
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return response.text

if __name__ == "__main__":
    RSS_URL = "https://weworkremotely.com/categories/remote-programming-jobs.rss"
    print("Fetching jobs...")
    recent_jobs = fetch_jobs(RSS_URL)
    
    print("Curating with Gemini...")
    markdown_content = curate_with_gemini(recent_jobs)
    
    # Create a folder called 'gigs' if it doesn't exist
    os.makedirs("gigs", exist_ok=True)
    
    # Save the AI response to a markdown file with today's date
    today_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"gigs/curation-{today_str}.md"
    
    with open(filename, "w") as f:
        f.write(markdown_content)
        
    print(f"Successfully saved to {filename}")
