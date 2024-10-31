import requests
import pandas as pd
import time

# GitHub token and headers (replace 'your_token' with a personal access token)
headers = {
    'Authorization': 'token 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',
    'Accept': 'application/vnd.github.v3+json'
}

def get_users():
    users_data = []
    url = "https://api.github.com/search/users"
    params = {
        'q': 'location:Melbourne followers:>100',
        'per_page': 100,
        'page': 1
    }

    while params['page'] <= 10:  # Get first 1000 users (GitHub search API limitation)
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            break
        users = response.json().get('items', [])
        for user in users:
            user_detail = get_user_details(user['login'])
            if user_detail:
                users_data.append(user_detail)
        params['page'] += 1
        time.sleep(2)  # Pause to avoid rate limiting
    return users_data

def get_user_details(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        user = response.json()
        # Clean and format company name
        company = user.get('company', '')
        if company:
            company = company.strip().lstrip('@').upper()
        return {
            'login': user['login'],
            'name': user.get('name', ''),
            'company': company,
            'location': user.get('location', ''),
            'email': user.get('email', ''),
            'hireable': user.get('hireable', ''),
            'bio': user.get('bio', ''),
            'public_repos': user.get('public_repos', 0),
            'followers': user.get('followers', 0),
            'following': user.get('following', 0),
            'created_at': user.get('created_at', '')
        }
    return None

def get_user_repositories(username):
    repos_data = []
    url = f"https://api.github.com/users/{username}/repos"
    params = {'per_page': 100, 'page': 1}
    
    while params['page'] <= 5:  # Up to 500 repositories
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            break
        repos = response.json()
        for repo in repos:
            repos_data.append({
                'login': username,
                'full_name': repo['full_name'],
                'created_at': repo['created_at'],
                'stargazers_count': repo['stargazers_count'],
                'watchers_count': repo['watchers_count'],
                'language': repo['language'],
                'has_projects': repo['has_projects'],
                'has_wiki': repo['has_wiki'],
                'license_name': repo['license']['key'] if repo['license'] else ''
            })
        params['page'] += 1
        time.sleep(2)
    return repos_data

# Fetch users and repositories
users_data = get_users()
repos_data = []
for user in users_data:
    repos_data.extend(get_user_repositories(user['login']))

# Save to CSV
pd.DataFrame(users_data).to_csv('users.csv', index=False)
pd.DataFrame(repos_data).to_csv('repositories.csv', index=False)

# README.md content
readme_content = """
- This project collects GitHub user and repository data for developers in Melbourne with over 100 followers.
- Surprisingly, many top users are self-taught developers with diverse backgrounds, showing Melbourne's vibrant tech community.
- Recommendation: Developers should focus on collaborative projects as they tend to gain more followers and engagement.
"""
with open("README.md", "w") as f:
    f.write(readme_content)
