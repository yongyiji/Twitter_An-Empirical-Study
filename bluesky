# collect Blueskye data

import pandas as pd
from atproto import Client, CAR, models
from tqdm import tqdm
import re


df = pd.read_csv('bluesky_account_name.csv')
df['bluesky_account'] = df['bluesky_account'].str.replace('@', '', regex=False) # account should be account_name.bsky.social


# Initialize the Bluesky client
at_client = Client()
USERNAME = "your_bluesky_account"
PASSWD = "your_password"
at_client.login(USERNAME, PASSWD)

## collect user profile

def profile_to_dict(profile_obj):
    return {x: str(profile_obj[x]) for x in dir(profile_obj) if '_' not in x}

def username_to_did(username):
    # Fetch the DID based on the Bluesky username
    params = models.AppBskyActorGetProfile.Params(actor=username)
    user_profile_obj = at_client.app.bsky.actor.get_profile(params)
    return user_profile_obj.did

bluesky_user_profiles = []

# Iterate through the DataFrame and get the profile for each username
for i, row in tqdm(df.iterrows(), total=len(df)):
    try:
        bluesky_username = row['bluesky_account']  # Make sure this is the correct column in your CSV
        bluesky_user_did = username_to_did(bluesky_username)  # Get DID using the username
        print(bluesky_user_did)
        params = models.AppBskyActorGetProfile.Params(actor=bluesky_user_did)  # Use DID to fetch the profile
        print(params)
        user_profile_obj = at_client.app.bsky.actor.get_profile(params)
        user_profile = profile_to_dict(user_profile_obj)
    except Exception as e:
        user_profile = {}
        print(f"Error processing {bluesky_username}: {e}")

    bluesky_user_profiles.append(user_profile)

# Add the profiles as a new column in your DataFrame
df["bluesky_user_profile"] = bluesky_user_profiles

# Collect user's number of followers and followees

def extract_profile_data(profile):
    if profile is None:
        return {
            "display_name": None,
            "followers_count": None,
            "follows_count": None,
            "posts_count": None
        }

    # Use regex to extract the necessary values from the profile string
    #display_name_match = re.search(r"display_name='([^']*)'", profile)
    followers_count_match = re.search(r"followers_count=(\d+)", profile)
    follows_count_match = re.search(r"follows_count=(\d+)", profile)
    posts_count_match = re.search(r"posts_count=(\d+)", profile)

    # Extract values, or set to None if not found
    #display_name = display_name_match.group(1) if display_name_match else None
    followers_count = int(followers_count_match.group(1)) if followers_count_match else None
    follows_count = int(follows_count_match.group(1)) if follows_count_match else None
    posts_count = int(posts_count_match.group(1)) if posts_count_match else None

    # Return the extracted values as a dictionary
    return {
        #"display_name": display_name,
        "followers_count": followers_count,
        "follows_count": follows_count,
        "posts_count": posts_count
    }


# Apply the function to every row in the "bluesky_user_profile" column
profile_data = df["bluesky_user_profile"].apply(
    lambda profile: extract_profile_data(profile.get('copy', None) if isinstance(profile, dict) else None))

# Convert the resulting list of dictionaries into separate columns
df_profile_data = pd.json_normalize(profile_data)

# Add the extracted data back to the original DataFrame
df = pd.concat([df, df_profile_data], axis=1)

# Print the updated DataFrame with the new columns
print(df[['followers_count', 'follows_count', 'posts_count']])




# get user post

post_data = []  # List to collect post information

# Function to split a list into chunks of a specified size
def chunk_list(input_list, chunk_size):
    for i in range(0, len(input_list), chunk_size):
        yield input_list[i:i + chunk_size]

for i, row in tqdm(df.iterrows(), total=len(df)):
    bluesky_username = row['bluesky_account']
    bluesky_user_did = username_to_did(bluesky_username)

    # Step 1: Get the user's feed
    author_feed_params = models.AppBskyFeedGetAuthorFeed.Params(
        actor=bluesky_user_did,
        limit=10
    )

    all_post_uris = []

    cursor = None
    while True:
        if cursor:
            author_feed_params.cursor = cursor

        author_feed_response = at_client.app.bsky.feed.get_author_feed(author_feed_params)

        if not author_feed_response.feed:
            print(f"No posts found for user: {bluesky_username}")
            break

        try:
            post_uris = [post.post.uri for post in author_feed_response.feed]
            all_post_uris.extend(post_uris)
        except AttributeError:
            print(f"URI not found in feed response for user: {bluesky_username}")
            break

        cursor = author_feed_response.cursor
        if not cursor:
            break

    if all_post_uris:
        # Chunk the post URIs into groups of 25
        for uri_chunk in chunk_list(all_post_uris, 25):
            params = models.AppBskyFeedGetPosts.Params(uris=uri_chunk)
            response = at_client.app.bsky.feed.get_posts(params)

            for post in response.posts:
                # identify whether the post is a repost
                if hasattr(post, 'repost_count'):
                    reposted_by_params = models.AppBskyFeedGetRepostedBy.Params(
                        uri=post.uri)
                    reposted_by_response = at_client.app.bsky.feed.get_reposted_by(reposted_by_params)
                    reposted_by_list = reposted_by_response.reposted_by

                    # Create a set to store unique repost author names
                    repost_authors = set()

                    # Loop through the list and add each reposer's name to the set
                    for profile in reposted_by_list:
                        repost_authors.add(profile.handle)  # Add the author's display name to the set

                    if bluesky_username in repost_authors:
                        is_report = True
                    else:
                        is_report = False
                else:
                    is_report = False

                try:
                    # Debug: Print the structure of the post to understand its attributes
                    print(f"Post structure for {bluesky_username}: {post}")

                    # Access available attributes based on the printed structure
                    post_info = {
                        'username': bluesky_username,
                        'post_uri': post.uri,  # Directly available
                        'text': post.record.text if hasattr(post, 'record') and hasattr(post.record, 'text') else None,
                        'created_at': post.record.created_at if hasattr(post, 'record') and hasattr(post.record,
                                                                                                    'created_at') else None,
                        'favorite_count': post.like_count if hasattr(post, 'like_count') else None,
                        'reply_count': post.reply_count if hasattr(post, 'reply_count') else None,
                        'repost_count': post.repost_count if hasattr(post, 'repost_count') else None,
                        'lang': post.lang if hasattr(post, 'lang') else None,
                        'embed_uri': post.embed.external.uri if hasattr(post, 'embed') and hasattr(post.embed,
                                                                                                   'external') and hasattr(
                            post.embed.external, 'uri') else None,
                        'is_report': is_report
                    }
                    post_data.append(post_info)


                except AttributeError as e:
                    print(f"Error processing post for {bluesky_username}: {e}")
    else:
        print(f"No posts found for user: {bluesky_username}")

# Step 7: Convert the collected post data into a DataFrame
posts_df = pd.DataFrame(post_data)
