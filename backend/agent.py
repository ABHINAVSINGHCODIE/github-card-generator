import os
from typing import List
import google.generativeai as genai
from dotenv import load_dotenv
import httpx
import json
from collections import Counter

load_dotenv()

class GitHubCardAgent:
    def __init__(self):
        self.model_name = "gemini-2.0-flash" 
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.model_name)

    async def get_github_stats(self, username: str) -> dict:
        """Fetch real GitHub user stats from GitHub API."""
        try:
            headers = {"Accept": "application/vnd.github.v3+json"}
            github_token = os.getenv("GITHUB_TOKEN")
            if github_token:
                headers["Authorization"] = f"token {github_token}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.github.com/users/{username}",
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                return {
                    "username": data.get("login"),
                    "name": data.get("name"),
                    "bio": data.get("bio"),
                    "public_repos": data.get("public_repos"),
                    "followers": data.get("followers"),
                    "following": data.get("following"),
                    "avatar_url": data.get("avatar_url"),
                    "profile_url": data.get("html_url")
                }
        except httpx.HTTPError as e:
            return {"error": f"Failed to fetch GitHub user: {str(e)}"}

    async def get_top_repositories(self, username: str, limit: int = 5) -> list:
        """Fetch top repositories by stars for a user."""
        try:
            headers = {"Accept": "application/vnd.github.v3+json"}
            github_token = os.getenv("GITHUB_TOKEN")
            if github_token:
                headers["Authorization"] = f"token {github_token}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.github.com/users/{username}/repos",
                    params={"sort": "stars", "direction": "desc", "per_page": limit},
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                repos = response.json()
                
                top_repos = []
                for repo in repos[:limit]:
                    top_repos.append({
                        "name": repo.get("name"),
                        "stars": repo.get("stargazers_count", 0),
                        "language": repo.get("language"),
                        "url": repo.get("html_url")
                    })
                return top_repos
        except Exception as e:
            return []

    async def get_languages(self, username: str) -> list:
        """Get the top programming languages used by a user."""
        try:
            headers = {"Accept": "application/vnd.github.v3+json"}
            github_token = os.getenv("GITHUB_TOKEN")
            if github_token:
                headers["Authorization"] = f"token {github_token}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.github.com/users/{username}/repos",
                    params={"per_page": 100},
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                repos = response.json()
                
                languages = Counter()
                for repo in repos:
                    lang = repo.get("language")
                    if lang:
                        languages[lang] += 1
                
                # Return top 5 languages
                return [lang for lang, _ in languages.most_common(5)]
        except Exception as e:
            return []

    async def generate_card_data(self, username: str):
        """Generate card data with real GitHub stats."""
        github_stats = await self.get_github_stats(username)
        
        if "error" in github_stats:
            return {
                "username": username,
                "rank": "ERROR",
                "stats": github_stats["error"]
            }
        
        # Fetch additional data
        top_repos = await self.get_top_repositories(username)
        languages = await self.get_languages(username)
        
        # Calculate rank based on followers and repos
        followers = github_stats.get("followers", 0)
        repos = github_stats.get("public_repos", 0)
        score = followers + (repos * 2)
        
        if score > 500:
            rank = "S"
        elif score > 200:
            rank = "A"
        elif score > 100:
            rank = "B"
        elif score > 50:
            rank = "C"
        else:
            rank = "D"
        
        return {
            "username": github_stats.get("username"),
            "name": github_stats.get("name"),
            "bio": github_stats.get("bio"),
            "rank": rank,
            "followers": followers,
            "repos": repos,
            "avatar_url": github_stats.get("avatar_url"),
            "profile_url": github_stats.get("profile_url"),
            "top_projects": top_repos,
            "languages": languages
        }

agent = GitHubCardAgent()
