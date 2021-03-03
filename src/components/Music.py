import math
import os
import discord

from discord.ext import commands
from src.songs.YTDL import YTDLSource, YTDLError
from src.songs.Songs import Song
from src.songs.Spotify import SpotifyTool
from src.components.Voice import VoiceState, VoiceError

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}
        self.spotify = SpotifyTool(os.getenv("SPOTIFY_ID"), os.getenv("SPOTIFY_CLIENT_SECRET"))

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state
        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage('This command can\'t be used in DM channels.')

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('An error occurred: {}'.format(str(error)))

    @commands.command(name='join', invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        """Joins a voice channel."""
        await ctx.send("Joining your call, Traveler-dono :blush:")
        destination = ctx.author.voice.channel

        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='summon')
    @commands.has_permissions(manage_guild=True)
    async def _summon(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        """Summons the bot to a voice channel.

        If no channel was specified, it joins your channel.
        """

        if not channel and not ctx.author.voice:
            await ctx.send('Traveler-dono! You aren\'t connected to any voice channel :stuck_out_tongue:')
            raise

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='leave', aliases=['disconnect'])
    async def _leave(self, ctx: commands.Context):
        """Clears the queue and leaves the voice channel."""

        if not ctx.voice_state.voice:
            return await ctx.send('Baka!! I\'m not connected to any channel! :yum:')

        await ctx.send('Sayonara, Traveler-dono! :blush:')
        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    @commands.command(name='volume')
    async def _volume(self, ctx: commands.Context, *, volume: int):
        """Sets the volume of the player."""

        if not ctx.voice_state.is_playing:
            return await ctx.send('Nothing is playing at the moment, Traveler-dono :relaxed:.')

        if 0 > volume > 100:
            return await ctx.send('Traveler-dono! The volume must be between 0 and 100! :sad:')

        ctx.voice_state.volume = volume / 100
        await ctx.send('Okay Traveler-dono, the volume of the player has been set to {}%'.format(volume))

    @commands.command(name='now', aliases=['current', 'playing'])
    async def _now(self, ctx: commands.Context):
        """Displays the currently playing song."""

        await ctx.send(embed=ctx.voice_state.current.create_embed())

    @commands.command(name='pause')
    #@commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx: commands.Context):
        """Pauses the currently playing song."""

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='resume')
    #@commands.has_permissions(manage_guild=True)
    async def _resume(self, ctx: commands.Context):
        """Resumes a currently paused song."""

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='stop')
    #@commands.has_permissions(manage_guild=True)
    async def _stop(self, ctx: commands.Context):
        """Stops playing song and clears the queue."""

        ctx.voice_state.songs.clear()

        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction('⏹')

    @commands.command(name='skip')
    async def _skip(self, ctx: commands.Context):
        """Vote to skip a song. The requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('Not playing any music right now, Traveler-dono...')

        # voter = ctx.message.author
        # if voter == ctx.voice_state.current.requester:
        await ctx.message.add_reaction('⏭')
        ctx.voice_state.skip()

        # elif voter.id not in ctx.voice_state.skip_votes:
        #     ctx.voice_state.skip_votes.add(voter.id)
        #     total_votes = len(ctx.voice_state.skip_votes)

        #     if total_votes >= 3:
        #         await ctx.message.add_reaction('⏭')
        #         ctx.voice_state.skip()
        #     else:
        #         await ctx.send('Skip vote added, currently at **{}/3**'.format(total_votes))

        # else:
        #     await ctx.send('You have already voted to skip this song.')

    @commands.command(name='queue')
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        """Shows the player's queue.

        You can optionally specify the page to show. Each page contains 10 elements.
        """

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('The queue is empty, Traveler-dono :relaxed:')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(description='**{} tracks:**\n\n{}'.format(len(ctx.voice_state.songs), queue))
                 .set_footer(text='Viewing page {}/{}'.format(page, pages)))
        await ctx.send(embed=embed)

    @commands.command(name='shuffle')
    async def _shuffle(self, ctx: commands.Context):
        """Shuffles the queue."""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('The queue is empty, Traveler-dono :relaxed:')

        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction('✅')

    @commands.command(name='remove')
    async def _remove(self, ctx: commands.Context, index: int):
        """Removes a song from the queue at a given index."""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('There is nothing to remove, Traveler-dono :relaxed:')

        ctx.voice_state.songs.remove(index - 1)
        await ctx.message.add_reaction('✅')

    @commands.command(name='loop')
    async def _loop(self, ctx: commands.Context):
        """Loops the currently playing song.

        Invoke this command again to unloop the song.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('You haven\'t told me to play anything, Traveler-dono... :point_right: :point_left:')

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        await ctx.message.add_reaction('✅')

    @commands.command(name='play')
    async def _play(self, ctx: commands.Context, *, search: str):
        """Plays a song.

        If there are songs in the queue, this will be queued until the
        other songs finished playing.

        This command automatically searches from various sites if no URL is provided.
        A list of these sites can be found here: https://rg3.github.io/youtube-dl/supportedsites.html
        """
        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)

        async with ctx.typing():

            # We are parsing a Spotify-related link
            if ("open.spotify.com" in search):
                song_info = await self.spotify.get_song_info(search)
                source = await YTDLSource.create_source(ctx, "%s %s" % (song_info["name"], song_info["artist"]), loop=self.bot.loop)

                song = Song(source)
                await ctx.voice_state.songs.put(song)
                await ctx.send('Hai hai! :blush: I shall play {} !'.format(str(source)))

            # We are parsing YouTube playlists
            else:
                try:
                    if ("playlist" in search):

                      # we will need to parse a playlist
                      entries = await YTDLSource.get_playlist_entries(ctx, search, loop=self.bot.loop)
                      await ctx.send('Hai hai! :blush: Time to queue up some songs...')
                      count = 0
                      for entry in entries:
                        try:
                          source = await YTDLSource.create_source(ctx, entry["id"], loop=self.bot.loop, using_id=True)

                          song = Song(source)
                          await ctx.voice_state.songs.put(song)
                        except Exception:
                            await ctx.send("Couldn't queue up %s" % (entry['title']))
                            continue
                        count += 1
                      await ctx.send('Queued up {} songs!'.format(count))
                      
                    else:
                      source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)

                    song = Song(source)

                    await ctx.voice_state.songs.put(song)
                    await ctx.send('Hai hai! :blush: I shall play {} !'.format(str(source)))

                except Exception as e:
                    await ctx.send('Gomenasai, Traveler-dono! Something happened :cry: ... {}'.format(str(e)))  

    @_join.before_invoke
    @_play.before_invoke
    @_loop.before_invoke
    @_queue.before_invoke
    @_shuffle.before_invoke
    @_remove.before_invoke
    @_leave.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send('Traveler-dono! You aren\'t connected to any voice channel :stuck_out_tongue:')
            raise

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                await ctx.send('Gomenasai, Traveler-dono! I\'m currently in the channel {}. Join that channel if you\'d like to use me, or wait until I\'m available :pleading_face:'.format(str(ctx.voice_client.channel)))
                raise
