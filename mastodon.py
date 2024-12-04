# collect Mostodon data

'''
Mastodon Account (User Account):

This is your personal account on Mastodon, which you created using your email (e.g., https://mastodon.social/@yourusername).
You can use this account to post updates, follow users, interact with the community, etc.

Client Application (OAuth Application):

This is the application you create (using the registration process), typically for interacting with Mastodon's API.
It doesn't have its own "user account" but instead acts on behalf of a user (you or others) through OAuth authorization.
The client application is used to collect data, post tweets, interact with timelines, etc., but only after gaining the proper permissions (scopes) from users.

User Account: This is where your posts and interactions are stored.
Client Application: This is what you use to interact with Mastodon programmatically. It needs to be authorized by you or other users (via OAuth) to access or post data on their behalf.
'''
## create client account, get client id and client secret

import requests

# Step 1: Register the client application
def register_client(api_base_url, client_name, redirect_uri, scopes, website):
    url = f'{api_base_url}/api/v1/apps'
    data = {
        'client_name': client_name,
        'redirect_uris': redirect_uri,
        'scopes': scopes,
        'website': website
    }

    response = requests.post(url, data=data)
    if response.status_code == 200:
        app_info = response.json()
        print("Client ID:", app_info['client_id'])
        print("Client Secret:", app_info['client_secret'])
        return app_info
    else:
        print(f"Error registering app: {response.status_code}")
        return None

# Step 2: Authorize the client application
def authorize_client(api_base_url, client_id, redirect_uri):
    # Construct the URL to authorize the application
    auth_url = f"{api_base_url}/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=read+write"
    print(f"Please go to the following URL and authorize the application:\n{auth_url}")
    # The user must paste the code from the authorization redirect
    auth_code = input("Enter the authorization code from the URL: ")
    return auth_code

# Step 3: Get the access token using the authorization code
def get_access_token(api_base_url, client_id, client_secret, redirect_uri, auth_code):
    url = f"{api_base_url}/oauth/token"
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'code': auth_code,
        'grant_type': 'authorization_code'
    }

    response = requests.post(url, data=data)
    if response.status_code == 200:
        token_info = response.json()
        print("Access Token:", token_info['access_token'])
        return token_info['access_token']
    else:
        print(f"Error getting access token: {response.status_code}")
        return None

# Step 4: Use the access token to make an authenticated API request
def verify_credentials(api_base_url, access_token):
    url = f"{api_base_url}/api/v1/accounts/verify_credentials"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        print("Verified user account:", user_info['username'])
        return user_info
    else:
        print(f"Error verifying credentials: {response.status_code}")
        return None



# Step 1: Register the client application
api_base_url = 'https://mastodon.social'  # Change to your Mastodon instance URL
client_name = 'Test Application'
redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'  # Out-of-band URI for manual token copy-pasting
scopes = 'read write push'
website = 'https://myapp.example'

print("Step 1: Register the client application")
app_info = register_client(api_base_url, client_name, redirect_uri, scopes, website)
if app_info:
    client_id = app_info['client_id']
    client_secret = app_info['client_secret']

    # Step 2: Authorize the client application
    print("\nStep 2: Authorize the client application")
    auth_code = authorize_client(api_base_url, client_id, redirect_uri)

    # Step 3: Get the access token
    print("\nStep 3: Get the access token using the authorization code")
    access_token = get_access_token(api_base_url, client_id, client_secret, redirect_uri, auth_code)

    if access_token:
        # Step 4: Verify the user's credentials using the access token
        print("\nStep 4: Verify credentials using the access token")
        verify_credentials(api_base_url, access_token)

print(client_id)
print(client_secret)






#_________________________________________________________________________________________________
# get data

# Step 1: Set up your Mastodon instance and client details
api_base_url = 'https://mastodon.social'  # Change to your Mastodon instance
client_id = 'your_client_id'  # Replace with your registered client_id
client_secret = 'your_client_secret'  # Replace with your registered client_secret
redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'  # Redirect URI for out-of-band token generation
scopes = 'read write push'  # Define the scope of your app's permissions

# Step 2: Request the access token using OAuth
# Here we use the client credentials flow (for machine-to-machine requests)

# Obtain the authorization code (This is done manually by visiting the URL)
print("Please visit this URL to authorize your app:")
print(f"{api_base_url}/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scopes}")

authorization_code = input("Enter the authorization code from the above URL: ")




import requests
import pandas as pd
import time
import csv



# Load the CSV file
df = pd.read_csv('mastodon_user_name')

# Define the instance URL you're querying from
api_base_url = 'https://mastodon.social'  # Your instance here
output_file = 'output_path'
csv_columns = ['username_to_search', 'username', 'user_id', 'post_number', 'post_id', 'post_content',
               'post_created_at', 'likes', 'replies', 'retweets', 'boosted_by', 'following_count', 'followers_count']

# Open the CSV file in append mode
with open(output_file, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=csv_columns)

    # Write the header only once if the file is empty
    if file.tell() == 0:
        writer.writeheader()

    # Iterate over each username in the DataFrame
    for username_to_search in df['mastodon_account']:
        # Prepare the search URL and params
        search_url = f'{api_base_url}/api/v2/search'
        search_params = {'q': username_to_search.strip('@')}
        headers = {'Authorization': f'Bearer {access_token}'}

        # Get the user details by making a federated search
        response = requests.get(search_url, params=search_params, headers=headers)
        search_data = response.json()

        # Initialize a flag to check if any posts were found
        posts_found = False

        # Check if user exists
        if 'accounts' in search_data and search_data['accounts']:
            user_data = search_data['accounts'][0]  # Extract the first matching user
            user_id = user_data['id']  # Extract user ID
            username = user_data['username']  # Extract username
            following_count = user_data['following_count']  # Number of accounts they follow
            followers_count = user_data['followers_count']  # Number of followers

            # Fetch the posts of that user from the instance you queried
            statuses_url = f'{api_base_url}/api/v1/accounts/{user_id}/statuses'

            # Initialize the post counter for the user
            user_post_counter = 0

            # Pagination: Loop to get all posts
            while statuses_url:
                statuses_response = requests.get(statuses_url, headers=headers)

                if statuses_response.status_code == 200:
                    posts = statuses_response.json()
                    if posts:
                        # Loop through the posts and write each post to CSV
                        for post in posts:
                            user_post_counter += 1  # Increment the counter

                            if 'reblog' in post and post['reblog']:
                                # This is a boost (reblog); extract details from the reblog field
                                boosted_post = post['reblog']
                                post_info = {
                                    'username_to_search': username_to_search,
                                    'username': post['account']['username'],
                                    'user_id': post['account']['id'],
                                    'post_number': user_post_counter,
                                    'post_id': boosted_post['id'],
                                    'post_content': boosted_post['content'],
                                    'post_created_at': boosted_post['created_at'],
                                    'likes': boosted_post['favourites_count'],
                                    'replies': boosted_post['replies_count'],
                                    'retweets': boosted_post['reblogs_count'],
                                    'boosted_by': post['account']['username'],  # Username of the boosting user
                                    'following_count': following_count,
                                    'followers_count': followers_count,
                                }
                            else:
                                # This is an original post; extract details directly
                                post_info = {
                                    'username_to_search': username_to_search,
                                    'username': post['account']['username'],
                                    'user_id': post['account']['id'],
                                    'post_number': user_post_counter,
                                    'post_id': post['id'],
                                    'post_content': post['content'],
                                    'post_created_at': post['created_at'],
                                    'likes': post['favourites_count'],
                                    'replies': post['replies_count'],
                                    'retweets': post['reblogs_count'],
                                    'boosted_by': None,
                                    'following_count': following_count,
                                    'followers_count': followers_count,
                                }

                            # Write the post info to the CSV file
                            writer.writerow(post_info)
                        posts_found = True

                    # Check if there is a next page for pagination
                    if 'next' in statuses_response.links:
                        statuses_url = statuses_response.links['next']['url']
                        time.sleep(30)
                    else:
                        break
                else:
                    print(f"Error fetching posts: {statuses_response.status_code}")
                    break

        # If no posts were found, append a row with user details but NaN for post-related fields
        if not posts_found:
            writer.writerow({
                'username_to_search': username_to_search,
                'username': user_data['username'] if 'accounts' in search_data and search_data['accounts'] else None,
                'user_id': user_data['id'] if 'accounts' in search_data and search_data['accounts'] else None,
                'post_number': None,
                'post_id': None,
                'post_content': None,
                'post_created_at': None,
                'likes': None,
                'replies': None,
                'retweets': None,
                'boosted_by': None,
                'following_count': following_count if 'accounts' in search_data and search_data['accounts'] else None,
                'followers_count': followers_count if 'accounts' in search_data and search_data['accounts'] else None,
            })

        # Print a message indicating that the user processing is finished
        print(f"Finished processing user: {username_to_search}")
        time.sleep(180)


# Display the resulting DataFrame
print(df_posts)
