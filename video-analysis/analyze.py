import time
from google import genai 
from google.genai import types

#Create a client object to communicate with Gemini
client = genai.Client(api_key="<YOUR_API_KEY_HERE")
 
success = False
while not success:
    try:
        response = client.models.generate_content(
        model='models/gemini-2.5-flash',
        contents=types.Content(
            parts=[
                types.Part(
                    file_data=types.FileData(file_uri='<url_of_some_video_on_youtube>'), # the video must be public - unlisted or private videos won't work.
                    video_metadata=types.VideoMetadata(
                    start_offset='0s', #start offset in seconds, as far as I know half of an hour is workable, hour and a half was too much.
                    end_offset='1800s'
                )
                ),
                types.Part(text='Make a transcript of the video. Annotate who is speaking and add timestamps for every speaker.')
            ]
        )
    )
    
        print(response.text) #The most basic way of printing output, there are definitely much nicer ways to do this.
        success = True
    except Exception as e:
        # Basic retry mechanism to catch trivial failures. Beware though - read the error and if it is something that you think can't be recovered from, terminate the program via Ctrl + C.
        print("there was an error")
        print(str(e))
        if "RESOURCE_EXHAUSTED" in str(e):
            print("resource exhausted, waiting for a minute")
            time.sleep(60)
        else:
            print(e)
            time.sleep(6)
