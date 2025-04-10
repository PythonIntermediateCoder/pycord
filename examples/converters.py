# This example requires the 'members' privileged intent to use the Member converter.

import typing

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot("!", intents=intents)


@bot.command()
async def userinfo(ctx: commands.Context, user: discord.User):
    # In the command signature above, you can see that the `user`
    # Parameter is typehinted to `discord.User`. This means that
    # During command invocation we will attempt to convert
    # The value passed as `user` to a `discord.User` instance.
    # The documentation notes what can be converted, in the case of `discord.User`
    # You pass an ID, mention or username (discrim optional)
    # E.g. 80088516616269824, @Danny or Danny#0007

    # NOTE: typehinting acts as a converter within the `commands` framework only.
    # In standard Python, it is use for documentation and IDE assistance purposes.

    # If the conversion is successful, we will have a `discord.User` instance
    # And can do the following:
    user_id = user.id
    username = user.name
    avatar = user.avatar.url
    await ctx.send(f"User found: {user_id} -- {username}\n{avatar}")


@userinfo.error
async def userinfo_error(ctx: commands.Context, error: commands.CommandError):
    # If the conversion above fails for any reason, it will raise `commands.BadArgument`
    # So we handle this in this error handler:
    if isinstance(error, commands.BadArgument):
        return await ctx.send("Couldn't find that user.")


# Custom Converter here
class ChannelOrMemberConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str):
        # In this example we have made a custom converter.
        # This checks if an input is convertible to a
        # `discord.Member` or `discord.TextChannel` instance from the
        # Input the user has given us using the pre-existing converters
        # That the library provides.

        member_converter = commands.MemberConverter()
        try:
            # Try and convert to a Member instance.
            # If this fails, then an exception is raised.
            # Otherwise, we just return the converted member value.
            member = await member_converter.convert(ctx, argument)
        except commands.MemberNotFound:
            pass
        else:
            return member

        # Do the same for TextChannel...
        textchannel_converter = commands.TextChannelConverter()
        try:
            channel = await textchannel_converter.convert(ctx, argument)
        except commands.ChannelNotFound:
            pass
        else:
            return channel

        # If the value could not be converted we can raise an error
        # So our error handlers can deal with it in one place.
        # The error has to be CommandError derived, so BadArgument works fine here.
        raise commands.BadArgument(
            f'No Member or TextChannel could be converted from "{argument}"'
        )


@bot.command()
async def notify(ctx: commands.Context, target: ChannelOrMemberConverter):
    # This command signature utilises the custom converter written above
    # What will happen during command invocation is that the `target` above will be passed to
    # The `argument` parameter of the `ChannelOrMemberConverter.convert` method and
    # The conversion will go through the process defined there.

    await target.send(f"Hello, {target.name}!")


@bot.command()
async def ignore(
    ctx: commands.Context, target: typing.Union[discord.Member, discord.TextChannel]
):
    # This command signature utilises the `typing.Union` typehint.
    # The `commands` framework attempts a conversion of each type in this Union *in order*.
    # So, it will attempt to convert whatever is passed to `target` to a `discord.Member` instance.
    # If that fails, it will attempt to convert it to a `discord.TextChannel` instance.
    # See: https://docs.pycord.dev/en/latest/ext/commands/commands.html#typing-union
    # NOTE: If a Union typehint converter fails it will raise `commands.BadUnionArgument`
    # Instead of `commands.BadArgument`.

    # To check the resulting type, `isinstance` is used
    if isinstance(target, discord.Member):
        await ctx.send(
            f"Member found: {target.mention}, adding them to the ignore list."
        )
    elif isinstance(
        target, discord.TextChannel
    ):  # This could be an `else` but for completeness' sake.
        await ctx.send(
            f"Channel found: {target.mention}, adding it to the ignore list."
        )


# Built-in type converters.
@bot.command()
async def multiply(ctx: commands.Context, number: int, maybe: bool):
    # We want an `int` and a `bool` parameter here.
    # `bool` is a slightly special case, as shown here:
    # See: https://docs.pycord.dev/en/latest/ext/commands/commands.html#bool

    if maybe:
        return await ctx.send(number * 2)
    await ctx.send(number * 5)


bot.run("token")
