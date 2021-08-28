music_help = "**Music Commands** --> [Venti-san!, Venti!, ++] <command> \n \n" + \
"***play*** <song_url> - Plays the song specified by <song_url>. At the current moment, only YouTube and Spotify links (tracks and playlists) are supported by the bot. \n \n" + \
"***stop*** - Stops the current song that is playing. \n \n" + \
"***join*** - Joins the voice channel that the invoker is in. **NOTE - You must be in a voice channel to summon the bot** \n \n" + \
"***leave*** - Disconnects from the voice channel that the invoker is in. \n \n" + \
"***volume*** <volume_value> - Adjusts the volume of the bot based on the specified <volume_value>. \n \n" + \
"***now*** - Shows the song that is currently playing. \n \n" + \
"***pause*** - Pauses the song that is currently playing. \n \n" + \
"***resume*** - Resumes the song that was paused. \n \n" + \
"***skip*** - Skips the song that is currently playing \n \n" + \
"***queue*** <queue_page> - Shows the queue of songs on the givene <queue_page> (by default, shows the first page of the queue). \n \n" + \
"***shuffle*** - Shuffles the songs in the queue. \n \n" + \
"***remove*** <song_number> - Removes a song at a given index specified by <song_number>. To figure out the index of the song you wish to remove, you must go through the queue by calling the 'queue' command. \n \n" + \
"***loop*** - Loops the song that is currently playing. (Patrick still needs to work on allowing you to choose between looping a song and looping a queue of songs) \n \n"

stocks_help = "**Stock Commands** --> ++<command> \n \n" + \
"***BTO***  *stock_name* *entry_price* - BUY TO OPEN - Create an entry for the given stock <stock_name> at the price of <entry_price>.   \n \n" + \
"***STC***  *stock_name* *closing_price* - SELL TO CLOSE - Close the most recent set of entries for a given stock <stock_name> at the price of <closing_price>. You cannot STC on a stock if you haven't bought it yet (either you have never bought to open on the stock OR your previous transaction on the stock was already an STC). \n \n" + \
"***AVG***  *stock_name* - Get the average value of the most recent open entries for a given stock <stock_name>. If your latest transaction on the stock was a STC, an average of $0.00 will be returned. \n \n" + \
"***OPEN*** - Get a list of all the stocks that currently have open entries (i.e., stocks that have not been STC'd). \n \n" + \
"***HISTORY*** - Get a list of all the closed transactions from the past 30 days. \n \n" + \
"***PSTC***  *stock_name* *partial_exit_price* - Make a partial exit on a stock at the price of <partial_exit_price>. NOTE - You can make 3 partial exits on an open entry where the 3rd exit will be noted as a STC. \n \n"