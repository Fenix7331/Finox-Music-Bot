import discord
import os
import wavelink
from discord.ext import commands
import asyncio
import typing
import jishaku

loda=[]
async def get_prefix(bot, message):
    idk = discord.utils.get(message.guild.roles, id=992464079140704326)
    if message.author.id in loda:
        return ["","."]
    elif idk in message.author.roles:
        return ["","."]
    else:
        return "."


token="MTAyMTM0NzEyNTQ2MTc4NjcxNQ.GAqTib.Cf4ZR1BGL4IXZ-nn1QBB6K_FYKqFHrAJDIGu4Y"

OWNER_IDS= [808230072536006697]

intents = discord.Intents.default()
intents.members = False
#intents.guilds = False
intents.presences = False
bot = commands.AutoShardedBot(command_prefix=get_prefix,intents=intents,owner_ids=OWNER_IDS,case_insensitive=True,strip_after_prefix=True,replied_user=False,shard_count=1, sync_commands_debug= True, sync_commands=True)

import os
os.system("pip install jishaku")

bot.remove_command("help")

async def node_connect():
    await bot.wait_until_ready()
    await wavelink.NodePool.create_node(bot=bot,host="lava.link", port=80, password="youshallnotpass", https=False)


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.listening, name=f'/play'))
    print("[+] Loaded & Online!")
    print(f"[+] Logged in as: {bot.user}")
    print(f"[+] Connected In: {len(bot.guilds)} guilds")
    print(f"[+] Connected To: {len(bot.users)} users")
    bot.loop.create_task(node_connect())
    try:
        synced = await bot.tree.sync()
        print(f"[+] Synced {len(synced)} Commands")
    except Exception as e:
        print (e)

cross = "<:error:992024170785427537>"
tick = "<:success:992024105975037992>"
music = "<a:gwl_WhiteMusic:1045275455206457374>"
@bot.event
async def on_wavelink_node_ready(node: wavelink.Node):
    print(f"[+] Node {node.identifier} is ready!")


@bot.event
async def on_wavelink_track_end(player: wavelink.Player, track: wavelink.Track, reason):
    ctx = player.ctx
    vc: player = ctx.voice_client
    if vc.loop:
        return await vc.play(track)
    next_song = vc.queue.get()
    await vc.play(next_song)
    emb = discord.Embed(title=f"**Now Playing**",
                         description=f"\n{next_song.title}", color=0x2f3136)
    await ctx.send(embed=emb)


async def play_next(ctx):
    if not ctx.voice_client.is_playing():
        next_song = ctx.voice_client.queue.get()
        await ctx.voice_client.play(next_song)
        emb = discord.Embed(title=f"**Now Playing**",
                             description=f"\n{next_song.title}", color=0x2f3136)
        await ctx.send(embed=emb)
    else:
        await ctx.voice_client.stop()
        return ctx.send(f"{cross} Nothing To Play In Queue")

@bot.event
async def on_message(message):
  await bot.process_commands(message)
  if message.content.startswith(f'<@{bot.user.id}>'):
    embed = discord.Embed(color=0x2f3136,
    title=f"Finox™#3987", description = f"**Hey, Thanks For Choosing <@1021347125461786715>, I Promise You To Provide Best Music Quality Without Stutter. <:Flantic_oki_oki:1039471757922418729>\n\n<:stolen_emoji:1047501090515582976> Use `/play` To Play Songs\n<:stolen_emoji:1047501090515582976> Use `/help` For List Of Commands\n\n<:Giveaway_2:1040573109411004466> Finox Is Trusted In More Than 200+ Servers**")
    await message.reply(embed=embed)
  
@bot.hybrid_command(name="play",aliases=["p"])
async def play(ctx, *, search: wavelink.YouTubeTrack):
    if not ctx.voice_client:
        vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    elif not getattr(ctx.author.voice, "channel", None):
        embed = discord.Embed(
            description=f"{ctx.author.mention} No Song(s) Are Being Played", color=0x2f3136)
        return await ctx.send(embed=embed)
    else:
        vc: wavelink.Player = ctx.voice_client

    if vc.queue.is_empty and vc.is_connected and vc._source is None:
        await vc.play(search)
        embe = discord.Embed(
            description=f"\n {search.title}", color=0x2f3136)
        embe.set_author(name=f"[+] Now Playing", icon_url=f"{ctx.author.avatar}")
        await ctx.send(embed=embe)
    else:
        print("Added to queue")
        await vc.queue.put_wait(search)
        emb = discord.Embed(
            description=f"\n {search.title} Added To The Queue", color=0x2f3136)
        emb.set_author(name=f"[+] Track Queue", icon_url=f"{ctx.author.avatar}")
	#emb.set_footer(name=f"Requested By {ctx.author.name}", icon_url=f"{ctx.author.avatar}")
        await ctx.send(embed=emb)
    vc.ctx = ctx
    setattr(vc, "loop", False)

@bot.hybrid_command(name="queue")
async def queue(ctx):
    if not ctx.voice_client:
        vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    elif not getattr(ctx.author.voice, "channel", None):
        embed = discord.Embed(
            description=f"[-] {ctx.author.mention}: No song(s) are playing.", color=0x2f3136)
        return await ctx.send(embed=embed)

    else:
        vc: wavelink.Player = ctx.voice_client

    if vc.queue.is_empty:
        emb = discord.Embed(
            description=f"[-] {ctx.author.mention}: Empty Queue Please Add Few Songs!",color=0x2f3136)
        return await ctx.send(embed=emb)
    lp = discord.Embed(title="Queue",color=0xF181FF)
    queue = vc.queue.copy()
    song_count = 0
    for song in queue:
        song_count += 1
        lp.add_field(name=f"[+] [{song_count}] Song", value=f"{song.title}")
        return await ctx.send(embed=lp)


@bot.hybrid_command(name="stop")
async def stop(ctx: commands.Context):
    if not ctx.voice_client:
        return await ctx.send(f"{cross} I Am Not Connected To Any Voice Channel")
    await ctx.voice_client.stop()
    await ctx.send(f"{tick} Stopped Playing!")


@bot.hybrid_command(name="pause")
async def pause(ctx: commands.Context):
    if not ctx.voice_client:
        return await ctx.send(f"{cross} I Am Not Connected To Any Voice Channel")
    await ctx.voice_client.pause()
    await ctx.send(f"{tick} Player Paused")


@bot.hybrid_command(name="resume", aliases=["unpause", "continue"])
async def resume(ctx: commands.Context):
    if not ctx.voice_client:
        return await ctx.send(f"{cross} I Am Not Connected To Any Voice Channel")
    await ctx.voice_client.resume()
    await ctx.send(f"{tick} Player Resumed")


@bot.hybrid_command(name="skip", pass_context=True)
async def skip(ctx: commands.Context):
    if not ctx.voice_client:
        return await ctx.send(f"{cross} I Am Not Connected To Any Voice Channel")
    await ctx.voice_client.pause()
    await play_next(ctx)
    await ctx.send(f"{tick} Player Skipped")


@bot.hybrid_command(name="disconnect", aliases=["dc"])
async def disconnect(ctx: commands.Context):
    if not ctx.voice_client:
        return await ctx.send(f"{cross} I Am Not Connected To Any Voice Channel")
    await ctx.voice_client.disconnect()
    await ctx.send(f"{tick} Disconnected The Player")

@bot.hybrid_command(name="seek")
async def seek(ctx: commands.Context, time: int):
    if not ctx.voice_client:
        return await ctx.send(f"{cross} I Am Not Connected To Any Voice Channel")
    await ctx.voice_client.seek(time)
    await ctx.send(f"{tick} Seeked To `{time}` Seconds")

@bot.hybrid_command(name="help")
async def help(ctx):
        embed = discord.Embed(
            description=f"{music} **_Finox's Music Commands_** {music}\n\n`play` | `queue` | `stop` | `pause` | `resume` | `skip` | `disconnect` | `seek`\n", color=0x2f3136)
        embed.set_footer(text="Made By Cyborg Development!")
        await ctx.send(embed=embed)

@bot.hybrid_command(name="ping")
async def ping(ctx):
        embed = discord.Embed(
            description=f"**_Finox's Latency: {int(bot.latency * 1000)}ms_**", color=0x2f3136)
        await ctx.send(embed=embed)

@bot.hybrid_command(name="connect",aliases=["j"])
async def join(ctx: commands.Context, channel: typing.Optional[discord.VoiceChannel]):
    if channel is None:
        channel = ctx.author.voice.channel
    node = wavelink.NodePool.get_node()
    player = node.get_player(ctx.guild)

    if player is not None:
        if player.is_connected():
            return await ctx.send(f"{cross} Already Connected To Any Channel")
    await channel.connect(cls=wavelink.Player)
    mbed=discord.Embed(title=f"{tick} Connected To {channel.name}", color=0x2f3136)
    await ctx.send(embed=mbed)

async def main () :
    await bot.start(token)


asyncio.run(main())
