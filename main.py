import discord
from discord.ext import commands
from discord.ui import View, Select, Button, Modal, TextInput
import json
import os
from datetime import datetime
import asyncio
import re

# ==================== LOAD CONFIG ====================
with open("config.json", "r") as f:
    config = json.load(f)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.voice_states = True  # REQUIRED for Join-to-Create

bot = commands.Bot(command_prefix="+", intents=intents)

# ==================== JOIN TO CREATE CONFIG ====================
JOIN_TO_CREATE_CHANNEL_ID = int(config.get("joinToCreateChannelId", 0))  # <-- PUT YOUR JOIN CHANNEL ID
TEMP_VC_CATEGORY_ID = int(config.get("tempVcCategoryId", 0))            # <-- PUT YOUR CATEGORY ID

# Tracks temporary channels: {channel_id: {"owner_id": int, "text_channel_id": int or None}}
temp_channels = {}

# ==================== YOUR EXISTING ROLE LISTS ====================
ALL_STAFF_ROLES = [
    "1545842045258825809",  # Creator
    "1545482300601405590",  # Mari
    "1512494871171043543",  # owners
    "1544803993480466563",  # co owners
    "1534637036542365787",  # king
    "1546192012435390515",  # overlord
    "1512494871171043541",  # manager
    "1545847662392119367",  # head manager
    "1512494871171043540",  # Administrator
    "1543926509520293908",  # head staff
    "1540434933166776400",  # senior mod
    "1512494871158591779",  # Moderator
]

SUPPORT_ONLY_ROLES = [
    "1545147283987894272",
    "1545147223140995142",
    "1545147164651683920",
    "1545140559365283972",
]

REWARD_STAFF_ROLES = [
    "1545842045258825809",
    "1545482300601405590",
    "1512494871171043543",
    "1544803993480466563",
    "1534637036542365787",
    "1546192012435390515",
    "1512494871171043541",
]

ADS_STAFF_ROLES = [
    "1545842045258825809",
    "1512494871171043543",
]

HIGH_STAFF_ROLES = [
    "1545842045258825809",
    "1545482300601405590",
    "1512494871171043543",
    "1544803993480466563",
    "1534637036542365787",
    "1546192012435390515",
    "1512494871171043541",
    "1512494871171043540",
    "1545847662392119367",
    "1543926509520293908",
]

ROLLS_STAFF_ROLES = [
    "1545842045258825809",
    "1512494871171043543",
    "1544803993480466563",
]

# ==================== MIDDLEMAN SERVICE ====================
MM_CATEGORY_ID = 1546222244995539024

MM_ROLES = {
    "cross": "1545889601166778468",
    "og": "1545889664249110569",
    "1b": "1544463220377526383",
    "250m": "1544463037266657391",
    "0-250m": "1544462860359442442",
}

MM_DISPLAY = {
    "cross": "Cross Trade",
    "og": "OG Trade",
    "1b": "1B+ Trades",
    "250m": "250M-1B Trades",
    "0-250m": "0-250M Trades",
}

MM_EMOJIS = {
    "cross": "🟡",
    "og": "🥇",
    "1b": "🥈",
    "250m": "🥉",
    "0-250m": "✅",
}

ALL_MM_ROLES = list(MM_ROLES.values())

# ==================== REACTION ROLES ====================
REACTION_ROLES = {
    "🧠": 1512494871045210206,
    "🍉": 1512494871045210207,
    "🌱": 1512494871045210205,
    "🎮": 1545889711116124222,
    "⚔️": 1546202492440682496,
}

REACTION_ROLE_LABELS = {
    "🧠": "SAB",
    "🍉": "BLOX FRUITS",
    "🌱": "GAG2",
    "🎮": "OTHER GAMES",
    "⚔️": "JJS",
}

# ==================== STAFF / RECRUITMENT ====================
STAFF_CATEGORY_IDS = {
    "recruitment": 1545919848490733718,
    "payrolls": 1545919791670370475,
    "indexprovider": 1545919725228400800,
    "mmapplication": 1545919661584158910,
}

STAFF_PANEL_ROLES = [
    "1545842045258825809",
    "1512494871171043543",
    "1544803993480466563",
    "1546192012435390515",
]

# ==================== INDEXING SERVICE ====================
INDEX_CATEGORY_ID = 1546222306148360223

INDEX_ROLES = {
    "crystal": "1545595662756876338",
    "phantom": "1545590572293824592",
    "cyber": "1545590491305877534",
    "divine": "1545591239599194162",
    "cursed": "1545590394048225370",
    "radioactive": "1545590875026104421",
    "yingyang": "1545591594416345088",
    "galaxy": "1545590794323370075",
    "lava": "1545590664652398602",
    "candy": "1545591008841048065",
    "rainbow": "1545591478049444021",
    "diamond": "1545591134456381530",
    "gold": "1545591381349900368",
}

INDEX_PRICES = {
    "crystal": "1x Base Drag (or equivalent value ; collat will be needed)",
    "phantom": "9 garam (or equivalent value ; collat will be needed)",
    "cyber": "9 garam (or equivalent value ; collat will be needed)",
    "divine": "Ask staff for current price (or equivalent value ; collat will be needed)",
    "cursed": "7+ garams (or equivalent value ; collat will be needed)",
    "radioactive": "6+ garams (or equivalent value ; collat will be needed)",
    "yingyang": "5+ garams (or equivalent value ; collat will be needed)",
    "galaxy": "3+ garams (or equivalent value ; collat will be needed)",
    "lava": "3+ garams (or equivalent value ; collat will be needed)",
    "candy": "2+ garams (or equivalent value ; collat will be needed)",
    "rainbow": "5 garams (or equivalent value ; collat will be needed)",
    "diamond": "4 garams (or equivalent value ; collat will be needed)",
    "gold": "3 garams (or equivalent value ; collat will be needed)",
}

INDEX_DISPLAY = {
    "crystal": "Crystal Base",
    "phantom": "Phantom Base",
    "cyber": "Cyber Base",
    "divine": "Divine Base",
    "cursed": "Cursed Base",
    "radioactive": "Radioactive Base",
    "yingyang": "YingYang Base",
    "galaxy": "Galaxy Base",
    "lava": "Lava Base",
    "candy": "Candy Base",
    "rainbow": "Rainbow Base",
    "diamond": "Diamond Base",
    "gold": "Gold Base",
}

INDEX_EMOJIS = {
    "crystal": "💎",
    "phantom": "👻",
    "cyber": "🤖",
    "divine": "✨",
    "cursed": "☠️",
    "radioactive": "☢️",
    "yingyang": "☯️",
    "galaxy": "🌌",
    "lava": "🌋",
    "candy": "🍬",
    "rainbow": "🌈",
    "diamond": "💠",
    "gold": "🟡",
}

ALL_INDEX_ROLES = list(INDEX_ROLES.values())


def save_config():
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)


def get_staff_mentions(ticket_type="support"):
    if ticket_type == "ads":
        roles = ["1545842045258825809", "1545482300601405590", "1512494871171043543", "1546192012435390515"]
    elif ticket_type == "rolls":
        roles = ["1545842045258825809", "1512494871171043543", "1544803993480466563", "1546192012435390515"]
    elif ticket_type == "support":
        roles = [
            "1545842045258825809", "1545482300601405590", "1512494871171043543",
            "1512494871171043541", "1545847662392119367", "1544803993480466563",
            "1546192012435390515", "1545140559365283972"
        ]
    else:
        roles = [
            "1545842045258825809", "1545482300601405590", "1512494871171043543",
            "1512494871171043541", "1545847662392119367", "1544803993480466563",
            "1546192012435390515"
        ]
    return " ".join([f"<@&{r}>" for r in roles])


def has_staff_permission(member: discord.Member):
    try:
        all_roles = ALL_STAFF_ROLES + SUPPORT_ONLY_ROLES + REWARD_STAFF_ROLES + ADS_STAFF_ROLES + ALL_INDEX_ROLES + ALL_MM_ROLES
        return any(str(role.id) in all_roles for role in member.roles)
    except:
        return False


def has_high_staff_permission(member: discord.Member):
    try:
        return any(str(role.id) in HIGH_STAFF_ROLES for role in member.roles)
    except:
        return False


def is_ticket_opener(channel, user):
    if not channel.topic or not str(channel.topic).startswith("ticket-"):
        return False
    opener_id = str(channel.topic).replace("ticket-", "")
    return str(user.id) == opener_id


def clean_channel_name(name: str) -> str:
    name = name.lower()
    name = re.sub(r'[^a-z0-9\-]', '-', name)
    name = re.sub(r'-+', '-', name).strip('-')
    return name[:90] if name else "ticket"


async def resolve_member(ctx: commands.Context, user_input: str):
    if ctx.message.mentions:
        return ctx.message.mentions[0]

    user_input = user_input.strip()
    if user_input.isdigit():
        member = ctx.guild.get_member(int(user_input))
        if member:
            return member
        try:
            user = await bot.fetch_user(int(user_input))
            return user
        except:
            pass

    user_input_lower = user_input.lower()
    for member in ctx.guild.members:
        if member.name.lower() == user_input_lower or member.display_name.lower() == user_input_lower:
            return member
        if user_input_lower in member.name.lower() or user_input_lower in member.display_name.lower():
            return member
    return None


# ==================== JOIN TO CREATE – CONTROL PANEL ====================
class NameModal(Modal, title="Change Channel Name"):
    new_name = TextInput(label="New channel name", max_length=100, required=True)

    def __init__(self, channel: discord.VoiceChannel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        data = temp_channels.get(self.channel.id)
        if not data or data["owner_id"] != interaction.user.id:
            return await interaction.response.send_message("Only the owner can do this.", ephemeral=True)
        try:
            await self.channel.edit(name=self.new_name.value)
            await interaction.response.send_message(f"✅ Channel renamed to **{self.new_name.value}**", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)


class LimitModal(Modal, title="Change User Limit"):
    new_limit = TextInput(label="User limit (0 = unlimited)", max_length=2, required=True)

    def __init__(self, channel: discord.VoiceChannel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        data = temp_channels.get(self.channel.id)
        if not data or data["owner_id"] != interaction.user.id:
            return await interaction.response.send_message("Only the owner can do this.", ephemeral=True)
        try:
            limit = int(self.new_limit.value)
            if limit < 0 or limit > 99:
                return await interaction.response.send_message("Limit must be between 0-99.", ephemeral=True)
            await self.channel.edit(user_limit=limit)
            await interaction.response.send_message(
                f"✅ User limit set to **{'unlimited' if limit == 0 else limit}**", ephemeral=True
            )
        except ValueError:
            await interaction.response.send_message("Please enter a valid number.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)


class BitrateModal(Modal, title="Change Bitrate"):
    new_bitrate = TextInput(label="Bitrate in kbps (8-384)", max_length=3, required=True)

    def __init__(self, channel: discord.VoiceChannel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        data = temp_channels.get(self.channel.id)
        if not data or data["owner_id"] != interaction.user.id:
            return await interaction.response.send_message("Only the owner can do this.", ephemeral=True)
        try:
            bitrate = int(self.new_bitrate.value)
            bitrate = max(8, min(384, bitrate)) * 1000
            await self.channel.edit(bitrate=bitrate)
            await interaction.response.send_message(f"✅ Bitrate set to **{bitrate // 1000} kbps**", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("Please enter a valid number.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)


class ChannelSettingsSelect(Select):
    def __init__(self, channel_id: int):
        options = [
            discord.SelectOption(label="Name", description="Change the channel name", value="name", emoji="✏️"),
            discord.SelectOption(label="Limit", description="Change the channel limit", value="limit", emoji="👥"),
            discord.SelectOption(label="Status", description="Change the channel status", value="status", emoji="💬"),
            discord.SelectOption(label="Game", description="Change name to the game you're playing", value="game", emoji="🎮"),
            discord.SelectOption(label="LFM", description="Post a message to the LFM channel", value="lfm", emoji="🔍"),
            discord.SelectOption(label="Bitrate", description="Change the channel bitrate", value="bitrate", emoji="🔊"),
            discord.SelectOption(label="Region", description="Change the channel voice region", value="region", emoji="🌍"),
            discord.SelectOption(label="Text", description="Create a temporary text channel", value="text", emoji="#️⃣"),
            discord.SelectOption(label="NSFW", description="Set your temporary channel to NSFW", value="nsfw", emoji="⚠️"),
            discord.SelectOption(label="Claim", description="Claim ownership of the channel", value="claim", emoji="👑"),
        ]
        super().__init__(
            placeholder="Change channel settings",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"vc_settings_{channel_id}"
        )
        self.channel_id = channel_id

    async def callback(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel or not isinstance(channel, discord.VoiceChannel):
            return await interaction.response.send_message("Channel not found.", ephemeral=True)

        data = temp_channels.get(self.channel_id)
        choice = self.values[0]

        # Claim is special
        if choice == "claim":
            if data and data["owner_id"] != interaction.user.id:
                owner_still_here = any(m.id == data["owner_id"] for m in channel.members)
                if not owner_still_here:
                    data["owner_id"] = interaction.user.id
                    temp_channels[self.channel_id] = data
                    return await interaction.response.send_message("✅ You claimed ownership of this channel!", ephemeral=True)
            return await interaction.response.send_message("You cannot claim this channel right now.", ephemeral=True)

        if not data or data["owner_id"] != interaction.user.id:
            return await interaction.response.send_message("Only the channel owner can use this.", ephemeral=True)

        if choice == "name":
            return await interaction.response.send_modal(NameModal(channel))
        if choice == "limit":
            return await interaction.response.send_modal(LimitModal(channel))
        if choice == "bitrate":
            return await interaction.response.send_modal(BitrateModal(channel))

        if choice == "text":
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
                interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
            }
            text_ch = await interaction.guild.create_text_channel(
                name=f"text-{channel.name}",
                category=channel.category,
                overwrites=overwrites
            )
            data["text_channel_id"] = text_ch.id
            temp_channels[self.channel_id] = data
            return await interaction.response.send_message(f"✅ Temporary text channel created: {text_ch.mention}", ephemeral=True)

        if choice == "nsfw":
            await channel.edit(nsfw=not channel.nsfw)
            return await interaction.response.send_message(f"✅ Channel NSFW set to **{channel.nsfw}**", ephemeral=True)

        await interaction.response.send_message(f"**{choice}** is not fully implemented yet.", ephemeral=True)


class ChannelPermissionsSelect(Select):
    def __init__(self, channel_id: int):
        options = [
            discord.SelectOption(label="Lock", description="Lock the channel", value="lock", emoji="🔒"),
            discord.SelectOption(label="Unlock", description="Unlock the channel", value="unlock", emoji="🔓"),
            discord.SelectOption(label="Permit", description="Permit users/roles to access the channel", value="permit", emoji="✅"),
            discord.SelectOption(label="Reject", description="Reject/kick users/roles", value="reject", emoji="❌"),
            discord.SelectOption(label="Invite", description="Invite a user to access the channel", value="invite", emoji="➕"),
            discord.SelectOption(label="Ghost", description="Make your channel invisible", value="ghost", emoji="👻"),
            discord.SelectOption(label="Unghost", description="Make your channel visible", value="unghost", emoji="👁️"),
            discord.SelectOption(label="Transfer", description="Transfer ownership to another user", value="transfer", emoji="👑"),
        ]
        super().__init__(
            placeholder="Change channel permissions",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"vc_permissions_{channel_id}"
        )
        self.channel_id = channel_id

    async def callback(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel or not isinstance(channel, discord.VoiceChannel):
            return await interaction.response.send_message("Channel not found.", ephemeral=True)

        data = temp_channels.get(self.channel_id)
        if not data or data["owner_id"] != interaction.user.id:
            return await interaction.response.send_message("Only the channel owner can use this.", ephemeral=True)

        choice = self.values[0]

        if choice == "lock":
            await channel.set_permissions(interaction.guild.default_role, connect=False)
            return await interaction.response.send_message("🔒 Channel locked.", ephemeral=True)

        if choice == "unlock":
            await channel.set_permissions(interaction.guild.default_role, connect=True)
            return await interaction.response.send_message("🔓 Channel unlocked.", ephemeral=True)

        if choice == "ghost":
            await channel.set_permissions(interaction.guild.default_role, view_channel=False)
            return await interaction.response.send_message("👻 Channel is now invisible (ghosted).", ephemeral=True)

        if choice == "unghost":
            await channel.set_permissions(interaction.guild.default_role, view_channel=True)
            return await interaction.response.send_message("👁️ Channel is now visible.", ephemeral=True)

        await interaction.response.send_message(f"**{choice}** requires a user/role selector – coming next.", ephemeral=True)


class TempVCControlView(View):
    def __init__(self, channel_id: int):
        super().__init__(timeout=None)
        self.add_item(ChannelSettingsSelect(channel_id))
        self.add_item(ChannelPermissionsSelect(channel_id))


# ==================== TICKET SELECT MENU ====================
class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Make a ticket if need to contact a staff.",
                description="This option is for contacting a staff member.",
                value="support",
                emoji=discord.PartialEmoji(name="support", id=1437196724463734805, animated=True)
            ),
            discord.SelectOption(
                label="Scammer reports & files",
                description="This option is to report scammers.",
                value="scammer",
                emoji=discord.PartialEmoji(name="scammer", id=1437198712995581972, animated=True)
            ),
            discord.SelectOption(
                label="Claim your Reward!",
                description="This option is only available if you have won a giveaway.",
                value="reward",
                emoji=discord.PartialEmoji(name="reward", id=1407871379948175480, animated=True)
            ),
            discord.SelectOption(
                label="By Ads",
                description="Click on this option to create a ticket",
                value="ads",
                emoji=discord.PartialEmoji(name="ads", id=1407878663910723725, animated=True)
            ),
            discord.SelectOption(
                label="Pay for Rolls",
                description="Click this option to pay for rolls",
                value="rolls",
                emoji="💰"
            )
        ]
        super().__init__(
            placeholder="Make a selection",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_select"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await create_ticket(interaction, self.values[0])


class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


# ==================== INDEX SELECT MENU ====================
class IndexSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Gold Base", description=INDEX_PRICES["gold"], value="gold", emoji="🟡"),
            discord.SelectOption(label="Diamond Base", description=INDEX_PRICES["diamond"], value="diamond", emoji="💠"),
            discord.SelectOption(label="Rainbow Base", description=INDEX_PRICES["rainbow"], value="rainbow", emoji="🌈"),
            discord.SelectOption(label="Galaxy Base", description=INDEX_PRICES["galaxy"], value="galaxy", emoji="🌌"),
            discord.SelectOption(label="Candy Base", description=INDEX_PRICES["candy"], value="candy", emoji="🍬"),
            discord.SelectOption(label="Lava Base", description=INDEX_PRICES["lava"], value="lava", emoji="🌋"),
            discord.SelectOption(label="Radioactive Base", description=INDEX_PRICES["radioactive"], value="radioactive", emoji="☢️"),
            discord.SelectOption(label="YingYang Base", description=INDEX_PRICES["yingyang"], value="yingyang", emoji="☯️"),
            discord.SelectOption(label="Cursed Base", description=INDEX_PRICES["cursed"], value="cursed", emoji="☠️"),
            discord.SelectOption(label="Divine Base", description=INDEX_PRICES["divine"], value="divine", emoji="✨"),
            discord.SelectOption(label="Cyber Base", description=INDEX_PRICES["cyber"], value="cyber", emoji="🤖"),
            discord.SelectOption(label="Phantom Base", description=INDEX_PRICES["phantom"], value="phantom", emoji="👻"),
            discord.SelectOption(label="Crystal Base", description=INDEX_PRICES["crystal"], value="crystal", emoji="💎"),
        ]
        super().__init__(
            placeholder="Select a base to index...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="index_select"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await create_index_ticket(interaction, self.values[0])


class IndexView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(IndexSelect())


# ==================== TICKET BUTTONS ====================
class TicketButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.primary, emoji="👤", custom_id="ticket_claim")
    async def claim_button(self, interaction: discord.Interaction, button: Button):
        if is_ticket_opener(interaction.channel, interaction.user):
            return await interaction.response.send_message("You cannot claim your own ticket.", ephemeral=True)
        if not has_staff_permission(interaction.user):
            return await interaction.response.send_message("Only staff can claim tickets.", ephemeral=True)

        embed = interaction.message.embeds[0]
        for field in embed.fields:
            if field.name.lower() == "claimed by":
                return await interaction.response.send_message("This ticket is already claimed.", ephemeral=True)

        embed.add_field(name="Claimed by", value=interaction.user.mention, inline=True)
        await interaction.message.edit(embed=embed)
        await interaction.response.send_message(f"Ticket claimed by {interaction.user.mention}")

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="ticket_close")
    async def close_button(self, interaction: discord.Interaction, button: Button):
        if not (is_ticket_opener(interaction.channel, interaction.user) or has_staff_permission(interaction.user)):
            return await interaction.response.send_message("Only staff or the ticket owner can close tickets.", ephemeral=True)

        await interaction.response.defer()
        deleted = await close_ticket(interaction.channel, interaction.user)
        if not deleted:
            try:
                await interaction.followup.send("❌ Could not delete this channel. Make sure the bot has **Manage Channels** in this category.", ephemeral=True)
            except:
                pass


# ==================== CREATE TICKET ====================
async def create_ticket(interaction: discord.Interaction, ticket_type: str):
    guild = interaction.guild
    member = interaction.user

    for channel in guild.text_channels:
        if channel.topic == f"ticket-{member.id}":
            return await interaction.followup.send(f"You already have an open ticket: {channel.mention}", ephemeral=True)

    config["ticketCounter"] += 1
    save_config()

    channel_name = clean_channel_name(member.name)

    if ticket_type == "support":
        category_id = 1545526574592303134
    elif ticket_type == "scammer":
        category_id = 1546222360179376290
    elif ticket_type == "reward":
        category_id = 1545526714573004831
    elif ticket_type == "ads":
        category_id = 1545526574592303134
    else:
        category_id = 1545526574592303134

    if ticket_type == "reward":
        allowed_roles = REWARD_STAFF_ROLES
    elif ticket_type == "ads":
        allowed_roles = ADS_STAFF_ROLES
    elif ticket_type == "rolls":
        allowed_roles = ROLLS_STAFF_ROLES
    elif ticket_type == "support":
        allowed_roles = ALL_STAFF_ROLES + SUPPORT_ONLY_ROLES
    else:
        allowed_roles = ALL_STAFF_ROLES

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        member: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, read_message_history=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True, manage_messages=True)
    }

    for role_id in allowed_roles:
        role = guild.get_role(int(role_id))
        if role:
            overwrites[role] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, attach_files=True, read_message_history=True, manage_messages=True
            )

    category = guild.get_channel(category_id)

    channel = await guild.create_text_channel(
        name=channel_name,
        category=category,
        topic=f"ticket-{member.id}",
        overwrites=overwrites
    )

    ping = get_staff_mentions(ticket_type)

    if ticket_type == "support":
        embed = discord.Embed(
            title=f"Ticket opened by {member.name}",
            description="Thank you for contacting the support\nPlease describe your problem and wait for an answer",
            color=0xED4245
        )
    elif ticket_type == "scammer":
        embed = discord.Embed(
            title=f"Ticket opened by {member.name}",
            description=(
                "**SCAMMER REPORT SERVICE**\n\n"
                "Please follow the format:\n\n"
                "`DISCORDIDOFSCAMMER - ID`\n"
                "`DISCORDIDOFVICTIM - ID`\n"
                "`ROBLOXUSEROFSCAMMER - USER`\n"
                "`ROBLOXUSEROFVICTIME - USER`\n\n"
                "**Deal:** (ex: Robux for Brainrots)\n"
                "**Evidences:**\n"
                "(Screens / Records only (Must include: The user of the scammer in the conversation, when he blocks or him assuming the scam))"
            ),
            color=0xED4245
        )
    elif ticket_type == "reward":
        embed = discord.Embed(
            title=f"Ticket opened by {member.name}",
            description=(
                "**REWARD CLAIMING SERVICE**\n\n"
                "Please follow the format:\n\n"
                "`DISCORDIDOFWINNER - ID`\n"
                "`ROBLOXUSEROFWINNER - USER`\n\n"
                "**Prize:** (EXAMPLE: x1 secret)\n"
                "**Evidences:**\n"
                "(Screens of the giveaway winning / etc)"
            ),
            color=0xED4245
        )
    elif ticket_type == "ads":
        embed = discord.Embed(
            title=f"Ticket opened by {member.name}",
            description="**📢 Promote Your Server!**\n\nPlease provide details about your ad request.",
            color=0xED4245
        )
    else:  # rolls
        embed = discord.Embed(
            title=f"Ticket opened by {member.name}",
            description="**Pay for Rolls**\n\nTell us which role you are paying for and what you are offering.",
            color=0x000000
        )
        embed.set_footer(text="Pay for Rolls")

    await channel.send(content=ping, embed=embed, view=TicketButtons())
    await interaction.followup.send(f"Ticket created: {channel.mention}", ephemeral=True)


# ==================== CLOSE TICKET ====================
async def close_ticket(channel: discord.TextChannel, closer: discord.Member) -> bool:
    channel_name = channel.name
    channel_id = channel.id
    guild = channel.guild

    try:
        await channel.edit(topic="closed", reason="Ticket closing")
    except:
        pass

    try:
        messages = [msg async for msg in channel.history(limit=50, oldest_first=True)]
        transcript = "---- TICKET LOGS ----\n\n"
        for msg in messages:
            time = msg.created_at.strftime("%d/%m/%Y %H:%M")
            transcript += f"{time} - {msg.author}: {msg.content}\n"
            if msg.embeds:
                transcript += f"<EMBED {msg.embeds[0].title or 'Embed'}>\n"

        log_path = f"log_{channel_id}.txt"
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(transcript)

        log_channel = bot.get_channel(int(config.get("transcriptChannelId", 0) or 0))
        if log_channel:
            try:
                await log_channel.send(
                    content=f"Ticket closed by {closer.mention}\nChannel: `{channel_name}`",
                    file=discord.File(log_path, filename="log.txt")
                )
            except Exception as e:
                print(f"Log send error: {e}")

        if os.path.exists(log_path):
            try:
                os.remove(log_path)
            except:
                pass
    except Exception as e:
        print(f"Transcript error: {e}")

    for attempt in range(5):
        try:
            ch = guild.get_channel(channel_id)
            if ch is None:
                return True
            await ch.delete(reason=f"Ticket closed by {closer}")
            return True
        except discord.NotFound:
            return True
        except discord.Forbidden:
            print(f"FORBIDDEN: Bot needs Manage Channels to delete {channel_name}")
            return False
        except Exception as e:
            print(f"Delete attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(0.8)

    return False


# ==================== EVENTS ====================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Bot is ready!")

    await bot.change_presence(
        activity=discord.Streaming(name="LEOS EMPIRE", url="https://twitch.tv/discord")
    )

    bot.add_view(TicketView())
    bot.add_view(TicketButtons())
    bot.add_view(IndexView())


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if member.bot:
        return

    # ========== JOIN TO CREATE ==========
    if after.channel and after.channel.id == JOIN_TO_CREATE_CHANNEL_ID:
        try:
            category = member.guild.get_channel(TEMP_VC_CATEGORY_ID)
            overwrites = {
                member.guild.default_role: discord.PermissionOverwrite(view_channel=True, connect=True),
                member: discord.PermissionOverwrite(
                    view_channel=True, connect=True, speak=True, stream=True,
                    manage_channels=True, move_members=True, mute_members=True, deafen_members=True
                ),
                member.guild.me: discord.PermissionOverwrite(
                    view_channel=True, connect=True, manage_channels=True, move_members=True
                )
            }

            new_channel = await member.guild.create_voice_channel(
                name=f"{member.display_name}'s Channel",
                category=category,
                overwrites=overwrites
            )

            temp_channels[new_channel.id] = {"owner_id": member.id, "text_channel_id": None}

            await member.move_to(new_channel)

            # Send control panel
            embed = discord.Embed(
                title="⚙️ Welcome to your own temporary voice channel",
                description=(
                    "Control your channel using the menus below\n"
                    "• Use the dropdowns to manage settings and permissions\n"
                    "• Alternatively use `/voice` commands\n\n"
                    "Create a **user profile** on the dashboard, then use **Load Settings** below to apply your saved settings to this channel.\n"
                    "**Gold options** require VoiceMaster+ or voting"
                ),
                color=0x2b2d31
            )
            view = TempVCControlView(new_channel.id)
            await new_channel.send(embed=embed, view=view)

        except Exception as e:
            print(f"Error creating temp VC: {e}")

    # ========== DELETE WHEN EVERYONE LEAVES ==========
    if before.channel and before.channel.id in temp_channels:
        # Small delay so Discord updates the member list
        await asyncio.sleep(0.4)

        channel = member.guild.get_channel(before.channel.id)

        # Channel already gone
        if channel is None:
            if before.channel.id in temp_channels:
                del temp_channels[before.channel.id]
            return

        # Count only real users (ignore bots)
        human_members = [m for m in channel.members if not m.bot]

        if len(human_members) == 0:
            data = temp_channels.get(channel.id)

            # Delete linked text channel if it exists
            if data and data.get("text_channel_id"):
                text_ch = member.guild.get_channel(data["text_channel_id"])
                if text_ch:
                    try:
                        await text_ch.delete(reason="Linked text channel - temp VC empty")
                    except:
                        pass

            # Delete the voice channel
            try:
                await channel.delete(reason="Temporary VC empty - everyone left")
                print(f"Deleted empty temp VC: {channel.name}")
            except Exception as e:
                print(f"Failed to delete temp VC: {e}")

            # Remove from tracking
            if channel.id in temp_channels:
                del temp_channels[channel.id]


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.user_id == bot.user.id:
        return
    emoji = str(payload.emoji)
    if emoji not in REACTION_ROLES:
        return
    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return
    role = guild.get_role(REACTION_ROLES[emoji])
    if not role:
        return
    member = guild.get_member(payload.user_id)
    if not member:
        try:
            member = await guild.fetch_member(payload.user_id)
        except:
            return
    try:
        await member.add_roles(role, reason="Reaction role")
    except Exception as e:
        print(f"Could not add role {role.name}: {e}")


@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    if payload.user_id == bot.user.id:
        return
    emoji = str(payload.emoji)
    if emoji not in REACTION_ROLES:
        return
    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return
    role = guild.get_role(REACTION_ROLES[emoji])
    if not role:
        return
    member = guild.get_member(payload.user_id)
    if not member:
        try:
            member = await guild.fetch_member(payload.user_id)
        except:
            return
    try:
        await member.remove_roles(role, reason="Reaction role removed")
    except Exception as e:
        print(f"Could not remove role {role.name}: {e}")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if bot.user.mentioned_in(message) and not message.mention_everyone:
        content = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        if len(content) < 3:
            await message.reply("My prefix on this server is: **+**", mention_author=False)
            return

    await bot.process_commands(message)


# ==================== COMMANDS ====================
@bot.command(name="invitepanel")
@commands.has_permissions(administrator=True)
async def invitepanel_command(ctx: commands.Context):
    channel = bot.get_channel(1546243778031919184)
    if channel is None:
        try:
            channel = await bot.fetch_channel(1546243778031919184)
        except:
            return await ctx.reply("❌ Could not find the invite rewards channel.")

    embed = discord.Embed(
        title="🎁 EARN FREE BRAINROTS",
        description=(
            "We have **invite rewards** so you can have a chance to win free brainrots.\n\n"
            "All you have to do is **invite people** to the server with your own link and have them join, "
            "and you can get free rewards.\n"
            "You can do so easily by sharing out many giveaways — they'd want free stuff.\n\n"
            "**REWARDS:**\n"
            "🥇 **Garama** = **8 invites**\n"
            "🐋 **Moby** (or same value) = **15 invites**\n"
            "🌈 **Colored Garama** or **Cerb** = **25 invites**\n"
            "💎 **2 Colored Garama** or **8 Garamas** = **50 invites**\n"
            "🐉 **Dragon** = **120 invites**\n\n"
            "**UNLIMITED STOCK** — Start inviting, get rewards! 🏆"
        ),
        color=0xFEE75C
    )
    embed.set_footer(text="Invite friends • Claim rewards with staff")

    await channel.send(content="@everyone @here", embed=embed)
    await ctx.reply(f"✅ Invite panel sent to {channel.mention}", mention_author=False)
    try:
        await ctx.message.delete()
    except:
        pass


@bot.command(name="rolepanel")
@commands.has_permissions(administrator=True)
async def rolepanel_command(ctx: commands.Context):
    embed = discord.Embed(
        title="🧠 LEOS MIDDLEMAN ROLES :",
        description=(
            "Take access to your favorite games by clicking on the corresponding reaction "
            "below this message.\n\n"
            "**Games available :**\n\n"
            "🧠 → **SAB**\n"
            "🍉 → **BLOX FRUITS**\n"
            "🌱 → **GAG2**\n"
            "🎮 → **OTHER GAMES**\n"
            "⚔️ → **JJS**\n\n"
            "React below to get / remove the role"
        ),
        color=0x5865F2
    )
    msg = await ctx.send(embed=embed)
    for emoji in REACTION_ROLES.keys():
        try:
            await msg.add_reaction(emoji)
        except Exception as e:
            print(f"Could not add reaction {emoji}: {e}")
    try:
        await ctx.message.delete()
    except:
        pass


@bot.command(name="panel")
@commands.has_permissions(administrator=True)
async def panel_command(ctx: commands.Context):
    embed = discord.Embed(
        title="Tickets",
        description="You can use this menu to create a ticket and contact the staff",
        color=0xED4245
    )
    await ctx.send(embed=embed, view=TicketView())
    try:
        await ctx.message.delete()
    except:
        pass


@bot.command(name="indexpanel")
@commands.has_permissions(administrator=True)
async def indexpanel_command(ctx: commands.Context):
    embed = discord.Embed(
        title="Request a Indexing Service",
        description=(
            "Request an indexing service by selecting one of the available bases below.\n\n"
            "🟡 **Gold Base**\n💠 **Diamond Base**\n🌈 **Rainbow Base**\n🌌 **Galaxy Base**\n"
            "🍬 **Candy Base**\n🌋 **Lava Base**\n☢️ **Radioactive Base**\n☯️ **YingYang Base**\n"
            "☠️ **Cursed Base**\n✨ **Divine Base**\n🤖 **Cyber Base**\n👻 **Phantom Base**\n💎 **Crystal Base**\n\n"
            "----------------------------------------\n"
            "**Index Base Rules**\nPLEASE FOLLOW THESE RULES DURING INDEXING\n\n"
            "1. PLEASE HAVE AN EMPTY BASE\n"
            "2. IF YOU FAIL TO RETURN A BRAINROT THE INDEX WILL BE CANCELED\n"
            "3. HIGH VALUE BRAINROTS WILL BE GIVEN ONE AT A TIME\n\n"
            "PLEASE MAKE A TICKET USING THE SELECT MENU BELOW TO PURCHASE\n\n"
            "**CHECK PRICES BELOW**\nWe only take Garam's+ so please do not waste our time with lowballs."
        ),
        color=0xED4245
    )
    await ctx.send(embed=embed, view=IndexView())
    try:
        await ctx.message.delete()
    except:
        pass


@bot.command(name="staffpanel")
@commands.has_permissions(administrator=True)
async def staffpanel_command(ctx: commands.Context):
    embed = discord.Embed(
        title="Staff & Team Opportunities",
        description=(
            "Interested in joining the team or unlocking staff services?\n"
            "Pick an option below to open a private ticket.\n\n"
            "📝 **Staff Application** — Apply for a staff position\n"
            "🎟️ **Pay for Rolls** — Purchase secure staff rolls\n"
            "📦 **Index Provider** — Apply to become an index provider\n"
            "🤝 **Middleman Application** — Apply to become a middleman\n\n"
            "Our team will review every request carefully."
        ),
        color=0x000000
    )
    embed.set_footer(text="Select an option to get started")
    await ctx.send(embed=embed)
    try:
        await ctx.message.delete()
    except:
        pass


@bot.command(name="mmpanel")
async def mmpanel_command(ctx: commands.Context):
    if not (ctx.author.guild_permissions.administrator or has_high_staff_permission(ctx.author)):
        return await ctx.reply("❌ You do not have permission to use this command.", mention_author=False)

    embed = discord.Embed(
        title="MiddleMan Services",
        description=(
            "Click bellow to choose one of these trade services\n\n"
            "• **Cross Trades** 🟡\n• **OG Trades** 🥇\n• **1B+ Trades** 🥈\n"
            "• **250M-1B Trades** 🥉\n• **0-250M Trades** ✅\n\n"
            "*Powered by Ticket King*"
        ),
        color=0xED4245
    )
    await ctx.send(embed=embed)
    try:
        await ctx.message.delete()
    except:
        pass


@bot.command(name="commands")
async def commands_command(ctx: commands.Context):
    if not has_staff_permission(ctx.author):
        return await ctx.reply("❌ You do not have permission to use this command.", mention_author=False)

    embed = discord.Embed(
        title="Ticket Bot Commands",
        description="Here are all the available commands:",
        color=0xED4245,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="`+panel`", value="Sends the ticket panel\n*(Admin only)*", inline=False)
    embed.add_field(name="`+indexpanel`", value="Sends the indexing service panel\n*(Admin only)*", inline=False)
    embed.add_field(name="`+mmpanel`", value="Sends the MiddleMan services panel\n*(Admin only)*", inline=False)
    embed.add_field(name="`+staffpanel`", value="Sends the staff recruitment panel\n*(Admin only)*", inline=False)
    embed.add_field(name="`+rolepanel`", value="Sends the game reaction role panel\n*(Admin only)*", inline=False)
    embed.add_field(name="`+invitepanel`", value="Sends the invite rewards panel\n*(Admin only)*", inline=False)
    embed.add_field(name="`+commands`", value="Shows this help menu", inline=False)
    embed.add_field(name="`+rename <name>`", value="Renames the current ticket", inline=False)
    embed.add_field(name="`+claim`", value="Claims the current ticket", inline=False)
    embed.add_field(name="`+close`", value="Closes the current ticket", inline=False)
    embed.add_field(name="`+add <user>`", value="Adds a user to the ticket\n(ID, @mention, or username)", inline=False)
    embed.add_field(name="`+remove <user>`", value="Removes a user from the ticket\n(ID, @mention, or username)", inline=False)
    embed.add_field(name="`+testperm`", value="Checks if the bot sees you as staff", inline=False)
    embed.set_footer(text="Prefix: + | Staff only")

    await ctx.reply(embed=embed, mention_author=False)


@bot.command(name="testperm")
async def testperm_command(ctx: commands.Context):
    if has_staff_permission(ctx.author):
        await ctx.reply("✅ You **have** staff permission.", mention_author=False)
    else:
        await ctx.reply("❌ You do **not** have staff permission.", mention_author=False)


@bot.command(name="rename")
async def rename_command(ctx: commands.Context, *, new_name: str = None):
    if not has_staff_permission(ctx.author):
        return await ctx.reply("❌ You do not have permission to use this command.", mention_author=False)

    if not ctx.channel.topic or not str(ctx.channel.topic).startswith("ticket-"):
        return await ctx.reply("❌ This command can only be used inside ticket channels.")

    if not new_name or len(new_name.strip()) < 2:
        return await ctx.reply("❌ Please provide a name.\nExample: `+rename giveaway won`")

    clean_name = new_name.lower().replace(" ", "-")[:100]

    try:
        await ctx.channel.edit(name=clean_name)
        await ctx.reply("✅ Ticket renamed successfully")
    except discord.Forbidden:
        await ctx.reply("❌ I don't have **Manage Channels** permission.")
    except Exception as e:
        await ctx.reply(f"❌ Error: `{e}`")


@bot.command(name="claim")
async def claim_command(ctx: commands.Context):
    if is_ticket_opener(ctx.channel, ctx.author):
        return await ctx.reply("❌ You cannot claim your own ticket.", mention_author=False)

    if not has_staff_permission(ctx.author):
        return await ctx.reply("❌ You do not have permission to use this command.", mention_author=False)

    if not ctx.channel.topic or not str(ctx.channel.topic).startswith("ticket-"):
        return await ctx.reply("❌ This command can only be used inside ticket channels.")

    try:
        found = False
        async for msg in ctx.channel.history(limit=30):
            if msg.author.id == bot.user.id and msg.embeds:
                embed = msg.embeds[0]
                for field in embed.fields:
                    if field.name.lower() == "claimed by":
                        return await ctx.reply("❌ This ticket is already claimed.")
                embed.add_field(name="Claimed by", value=ctx.author.mention, inline=True)
                await msg.edit(embed=embed)
                found = True
                break
        if found:
            await ctx.reply(f"✅ Ticket claimed by {ctx.author.mention}")
        else:
            await ctx.reply("❌ Could not find the ticket message.")
    except Exception as e:
        await ctx.reply(f"❌ Error while claiming: `{e}`")


@bot.command(name="close")
async def close_command(ctx: commands.Context):
    if not ctx.channel.topic or not str(ctx.channel.topic).startswith("ticket-"):
        return await ctx.reply("❌ This command can only be used inside ticket channels.")

    if not (is_ticket_opener(ctx.channel, ctx.author) or has_staff_permission(ctx.author)):
        return await ctx.reply("❌ Only staff or the ticket owner can close tickets.", mention_author=False)

    deleted = await close_ticket(ctx.channel, ctx.author)
    if not deleted:
        try:
            await ctx.reply("❌ Could not delete this channel. Make sure the bot has **Manage Channels** in this category.")
        except:
            pass


@bot.command(name="add")
async def add_command(ctx: commands.Context, *, user_input: str = None):
    if not has_high_staff_permission(ctx.author):
        return await ctx.reply("❌ You do not have permission to use this command.", mention_author=False)

    if not ctx.channel.topic or not str(ctx.channel.topic).startswith("ticket-"):
        return await ctx.reply("❌ This command can only be used inside ticket channels.")

    if not user_input:
        return await ctx.reply("❌ Please provide a user.\nExample: `+add @user` or `+add 123456789` or `+add username`")

    target = await resolve_member(ctx, user_input)
    if not target:
        return await ctx.reply("❌ Could not find that user.")

    try:
        await ctx.channel.set_permissions(
            target,
            view_channel=True,
            send_messages=True,
            attach_files=True,
            read_message_history=True
        )
        await ctx.reply(f"✅ Added {target.mention} to the ticket.")
    except discord.Forbidden:
        await ctx.reply("❌ I don't have permission to edit channel permissions.")
    except Exception as e:
        await ctx.reply(f"❌ Error: `{e}`")


@bot.command(name="remove")
async def remove_command(ctx: commands.Context, *, user_input: str = None):
    if not has_high_staff_permission(ctx.author):
        return await ctx.reply("❌ You do not have permission to use this command.", mention_author=False)

    if not ctx.channel.topic or not str(ctx.channel.topic).startswith("ticket-"):
        return await ctx.reply("❌ This command can only be used inside ticket channels.")

    if not user_input:
        return await ctx.reply("❌ Please provide a user.\nExample: `+remove @user` or `+remove 123456789` or `+remove username`")

    target = await resolve_member(ctx, user_input)
    if not target:
        return await ctx.reply("❌ Could not find that user.")

    if ctx.channel.topic and ctx.channel.topic.startswith("ticket-"):
        opener_id = ctx.channel.topic.replace("ticket-", "")
        if str(target.id) == opener_id:
            return await ctx.reply("❌ You cannot remove the person who opened the ticket.")

    try:
        await ctx.channel.set_permissions(target, overwrite=None)
        await ctx.reply(f"✅ Removed {target.mention} from the ticket.")
    except discord.Forbidden:
        await ctx.reply("❌ I don't have permission to edit channel permissions.")
    except Exception as e:
        await ctx.reply(f"❌ Error: `{e}`")


@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingPermissions):
        return await ctx.reply("❌ You do not have permission to use this command.", mention_author=False)
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        return await ctx.reply(f"❌ Missing argument: `{error.param.name}`", mention_author=False)
    try:
        await ctx.reply(f"❌ Error: `{error}`", mention_author=False)
    except:
        pass
    print(f"Command error in {ctx.command}: {error}")


# ==================== RUN ====================
bot.run(os.getenv("TOKEN") or config.get("token"))
