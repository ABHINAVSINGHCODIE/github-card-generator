from fastmcp import FastMCP
import httpx
import json

mcp = FastMCP("GitHub Card Generator Tools")

@mcp.tool()
async def get_github_user_stats(username: str) -> str:
    """Fetches GitHub stats for a given user from GitHub API."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.github.com/users/{username}",
                headers={"Accept": "application/vnd.github.v3+json"},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            return json.dumps({
                "username": data.get("login"),
                "name": data.get("name"),
                "bio": data.get("bio"),
                "public_repos": data.get("public_repos"),
                "public_gists": data.get("public_gists"),
                "followers": data.get("followers"),
                "following": data.get("following"),
                "created_at": data.get("created_at"),
                "avatar_url": data.get("avatar_url")
            })
    except httpx.HTTPError as e:
        return json.dumps({"error": f"Failed to fetch GitHub user: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"})

if __name__ == "__main__":
    mcp.run()
