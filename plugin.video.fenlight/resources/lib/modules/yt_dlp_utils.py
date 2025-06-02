# This is a wrapper module for yt-dlp functionalities.
# It will be used to fetch trailer URLs.

try:
    # Attempt to import the yt_dlp module from the designated location
    from ..modules.yt_dlp import yt_dlp
except ImportError:
    # Fallback for cases where the module structure might be different (e.g., local testing)
    try:
        import yt_dlp
    except ImportError:
        # If yt-dlp is not found, set it to None to handle gracefully
        yt_dlp = None

def get_trailer_url(video_url_or_search_query):
    """
    Fetches the direct video URL for a given YouTube video URL or search query.

    Args:
        video_url_or_search_query (str): A YouTube video URL or a search query string.
                                         For searches, it will find the first video result.

    Returns:
        str: The direct URL to the video, or None if an error occurs or yt_dlp is not available.
    """
    if yt_dlp is None:
        print("yt-dlp module is not available. Please ensure it is installed correctly.")
        return None

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch',  # Use ytsearch for queries
        'extract_flat': 'in_playlist', # Faster when searching, gets only first result info
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # If it's not a URL, yt-dlp will use default_search
            info_dict = ydl.extract_info(video_url_or_search_query, download=False)

            # If search is used, info_dict will contain a list of entries
            if 'entries' in info_dict and info_dict['entries']:
                # Get the first video from search results
                video_info = info_dict['entries'][0]
            elif 'url' in info_dict: # Direct URL was provided
                video_info = info_dict
            else: # No URL and no entries found (e.g. invalid direct URL or no search results)
                print(f"No video found for '{video_url_or_search_query}'.")
                return None

            # After potentially getting the first entry from a search,
            # we might need to extract full info for that specific video ID
            # if 'url' is not directly available (common with 'extract_flat':'in_playlist')
            if 'url' not in video_info and 'id' in video_info:
                nested_ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'noplaylist': True,
                    'quiet': True,
                }
                with yt_dlp.YoutubeDL(nested_ydl_opts) as nested_ydl:
                    video_info = nested_ydl.extract_info(f"https://www.youtube.com/watch?v={video_info['id']}", download=False)

            if 'url' in video_info:
                return video_info['url']
            else:
                print(f"Could not extract direct video URL for '{video_url_or_search_query}'.")
                return None

    except yt_dlp.utils.DownloadError as e:
        print(f"yt-dlp download error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == '__main__':
    # Example Usage (for testing purposes)
    if yt_dlp:
        # Test with a direct YouTube URL
        # test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        # print(f"Fetching URL for: {test_url}")
        # direct_url = get_trailer_url(test_url)
        # if direct_url:
        #     print(f"Direct URL: {direct_url}")
        # else:
        #     print("Failed to get direct URL.")

        # print("-" * 30)

        # Test with a search query
        test_query = "official dune trailer"
        print(f"Searching for: '{test_query}'")
        search_url = get_trailer_url(test_query)
        if search_url:
            print(f"Direct URL for search result: {search_url}")
        else:
            print("Failed to get URL for search query.")

        print("-" * 30)

        test_query_no_results = "asdflkjhglkjhfdsasdfasdfasdf"
        print(f"Searching for: '{test_query_no_results}' (expected no results)")
        search_url_no_results = get_trailer_url(test_query_no_results)
        if search_url_no_results:
            print(f"Direct URL for search result: {search_url_no_results}")
        else:
            print("Failed to get URL for search query (as expected).")

    else:
        print("yt_dlp module not loaded, cannot run examples.")
