import discord
from discord.ext import commands
from discord.ui import View, Select, Button
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

bot = commands.Bot(command_prefix="+", intents=intents)

# All roles that can see Support + Scammer tickets
ALL_STAFF_ROLES = [
    "1545842045258825809",  # Creator
    "1545482300601405590",  # Mari
    "1512494871171043543",  # owners
    "1544803993480466563",  # co owners
    "1534637036542365787",  # king
    "1543925240705585284",  # overlord
    "1512494871171043541",  # manager
    "1545847662392119367",  # head manager
    "1512494871171043540",  # Administrator
    "1543926509520293908",  # head staff
    "1540434933166776400",  # senior mod
    "1512494871158591779",  # Moderator
]

# Extra roles that can ONLY see Support tickets (not Report)
SUPPORT_ONLY_ROLES = [
    "1545147283987894272",
    "1545147223140995142",
    "1545147164651683920",
    "1545140559365283972",
]

# Only Manager and above (excluding Admin + Head Staff) can see Reward tickets
REWARD_STAFF_ROLES = [
    "1545842045258825809",  # Creator
    "1545482300601405590",  # Mari
    "1512494871171043543",  # owners
    "1544803993480466563",  # co owners
    "1534637036542365787",  # king
    "1543925240705585284",  # overlord
    "1512494871171043541",  # manager
]

# Only Creator + Owner can see Ads tickets
ADS_STAFF_ROLES = [
    "1545842045258825809",  # Creator
    "1512494871171043543",  # owner
]

# Only these roles can use +add and +remove
HIGH_STAFF_ROLES = [
    "1545842045258825809",  # Creator
    "1512494871171043543",  # owner
    "1544803993480466563",  # co owner
    "1534637036542365787",  # king
    "1543925240705585284",  # overlord
    "1512494871171043541",  # manager
    "1512494871171043540",  # Administrator
    "1545847662392119367",  # head manager
]

# Only Creator + Owner + Co Owner can see Pay for Rolls tickets
ROLLS_STAFF_ROLES = [
    "1545842045258825809",  # Creator
    "1512494871171043543",  # owner
    "1544803993480466563",  # co owner
]


# ==================== MIDDLEMAN SERVICE ====================
MM_CATEGORY_ID = 1545891563903910020  # where tickets go

MM_ROLES = {
    "cross": "1545889601166778468",      # Cross trade
    "og": "1545889664249110569",         # OG Middleman
    "1b": "1544463220377526383",         # 1B+ middleman
    "250m": "1544463037266657391",       # 250M-1B / 500m middleman
    "0-250m": "1544462860359442442",     # 0-250M middleman
}

MM_DISPLAY = {
    "cross": "Cross Trade",
    "og": "OG Trade",
    "1b": "1B+ Trades",
    "250m": "250M-1B Trades",
    "0-250m": "0-250M Trades",
}

MM_EMOJIS = {
    "cross": "⬡",
    "og": "🥇",
    "1b": "🥈",
    "250m": "🥉",
    "0-250m": "✅",
}

ALL_MM_ROLES = list(MM_ROLES.values())

# ==================== INDEXING SERVICE ====================
INDEX_CATEGORY_ID = 1545599546342510623

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

# All index role IDs for staff permission checks
ALL_INDEX_ROLES = list(INDEX_ROLES.values())


def save_config():
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)


def get_staff_mentions(ticket_type="support"):
    if ticket_type == "ads":
        roles = [
            "1545842045258825809",  # Creator
            "1545482300601405590",  # Mari
            "1512494871171043543",  # owner
        ]
    elif ticket_type == "rolls":
        roles = [
            "1545842045258825809",  # Creator
            "1512494871171043543",  # owner
            "1544803993480466563",  # co owner
        ]
    elif ticket_type == "support":
        roles = [
            "1545842045258825809",  # Creator
            "1545482300601405590",  # Mari
            "1512494871171043543",  # owner
            "1512494871171043541",  # manager
            "1545847662392119367",  # head manager
            "1544803993480466563",  # co owner
            "1543925240705585284",  # overlord
            "1545140559365283972",  # extra support ping
        ]
    else:
        roles = [
            "1545842045258825809",  # Creator
            "1545482300601405590",  # Mari
            "1512494871171043543",  # owner
            "1512494871171043541",  # manager
            "1545847662392119367",  # head manager
            "1544803993480466563",  # co owner
            "1543925240705585284",  # overlord
        ]
    return " ".join([f"<@&{r}>" for r in roles])


def has_staff_permission(member: discord.Member):
    try:
        all_roles = ALL_STAFF_ROLES + SUPPORT_ONLY_ROLES + REWARD_STAFF_ROLES + ADS_STAFF_ROLES + ALL_INDEX_ROLES + ALL_MM_ROLES
        return any(str(role.id) in all_roles for role in member.roles)
    except:
        return False


def has_high_staff_permission(member: discord.Member):
    """For +add and +remove only"""
    try:
        return any(str(role.id) in HIGH_STAFF_ROLES for role in member.roles)
    except:
        return False


def is_ticket_opener(channel, user):
    """Check if the user is the one who opened the ticket"""
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
    """Resolve a user by mention, ID, or username"""
    # Try mention first
    if ctx.message.mentions:
        return ctx.message.mentions[0]

    # Try ID
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

    # Try username
    user_input_lower = user_input.lower()
    for member in ctx.guild.members:
        if member.name.lower() == user_input_lower or member.display_name.lower() == user_input_lower:
            return member
        if user_input_lower in member.name.lower() or user_input_lower in member.display_name.lower():
            return member

    return None


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
        await create_ticket(interaction, self.values[0])


class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


# ==================== INDEX SELECT MENU ====================
class IndexSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Gold Base",
                description=INDEX_PRICES["gold"],
                value="gold",
                emoji="🟡"
            ),
            discord.SelectOption(
                label="Diamond Base",
                description=INDEX_PRICES["diamond"],
                value="diamond",
                emoji="💠"
            ),
            discord.SelectOption(
                label="Rainbow Base",
                description=INDEX_PRICES["rainbow"],
                value="rainbow",
                emoji="🌈"
            ),
            discord.SelectOption(
                label="Galaxy Base",
                description=INDEX_PRICES["galaxy"],
                value="galaxy",
                emoji="🌌"
            ),
            discord.SelectOption(
                label="Candy Base",
                description=INDEX_PRICES["candy"],
                value="candy",
                emoji="🍬"
            ),
            discord.SelectOption(
                label="Lava Base",
                description=INDEX_PRICES["lava"],
                value="lava",
                emoji="🌋"
            ),
            discord.SelectOption(
                label="Radioactive Base",
                description=INDEX_PRICES["radioactive"],
                value="radioactive",
                emoji="☢️"
            ),
            discord.SelectOption(
                label="YingYang Base",
                description=INDEX_PRICES["yingyang"],
                value="yingyang",
                emoji="☯️"
            ),
            discord.SelectOption(
                label="Cursed Base",
                description=INDEX_PRICES["cursed"],
                value="cursed",
                emoji="☠️"
            ),
            discord.SelectOption(
                label="Divine Base",
                description=INDEX_PRICES["divine"],
                value="divine",
                emoji="✨"
            ),
            discord.SelectOption(
                label="Cyber Base",
                description=INDEX_PRICES["cyber"],
                value="cyber",
                emoji="🤖"
            ),
            discord.SelectOption(
                label="Phantom Base",
                description=INDEX_PRICES["phantom"],
                value="phantom",
                emoji="👻"
            ),
            discord.SelectOption(
                label="Crystal Base",
                description=INDEX_PRICES["crystal"],
                value="crystal",
                emoji="💎"
            ),
        ]
        super().__init__(
            placeholder="Select a base to index...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="index_select"
        )

    async def callback(self, interaction: discord.Interaction):
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
        # Ticket opener OR staff can close
        if not (is_ticket_opener(interaction.channel, interaction.user) or has_staff_permission(interaction.user)):
            return await interaction.response.send_message("Only staff or the ticket owner can close tickets.", ephemeral=True)

        await interaction.response.defer()
        await close_ticket(interaction.channel, interaction.user)


# ==================== CREATE TICKET ====================
async def create_ticket(interaction: discord.Interaction, ticket_type: str):
    guild = interaction.guild
    member = interaction.user

    # Prevent multiple open tickets
    for channel in guild.text_channels:
        if channel.topic == f"ticket-{member.id}":
            return await interaction.response.send_message(
                f"You already have an open ticket: {channel.mention}", ephemeral=True
            )

    config["ticketCounter"] += 1
    save_config()

    # Channel name = username
    channel_name = clean_channel_name(member.name)

    # Different category for each ticket type
    if ticket_type == "support":
        category_id = 1545526574592303134
    elif ticket_type == "scammer":
        category_id = 1545526637112729651
    elif ticket_type == "reward":
        category_id = 1545526714573004831
    elif ticket_type == "ads":
        category_id = 1545526574592303134
    else:  # rolls
        category_id = 1545526574592303134

    # Choose which roles can see this ticket
    if ticket_type == "reward":
        allowed_roles = REWARD_STAFF_ROLES
    elif ticket_type == "ads":
        allowed_roles = ADS_STAFF_ROLES
    elif ticket_type == "rolls":
        allowed_roles = ROLLS_STAFF_ROLES
    elif ticket_type == "support":
        allowed_roles = ALL_STAFF_ROLES + SUPPORT_ONLY_ROLES
    else:  # scammer/report
        allowed_roles = ALL_STAFF_ROLES

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        member: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            attach_files=True,
            read_message_history=True
        ),
        guild.me: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            manage_channels=True,
            manage_messages=True
        )
    }

    for role_id in allowed_roles:
        role = guild.get_role(int(role_id))
        if role:
            overwrites[role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                attach_files=True,
                read_message_history=True,
                manage_messages=True
            )

    category = guild.get_channel(category_id)

    channel = await guild.create_text_channel(
        name=channel_name,
        category=category,
        topic=f"ticket-{member.id}",
        overwrites=overwrites
    )

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
            description=(
                "**📢 Promote Your Server!**\n\n"
                "**Package 1:** 2 Days | 1 Ping — 1x Tang Tang Keletang / Equivalent Value\n"
                "**Package 2:** 3 Days | 2 Pings — 1x Garama / Equivalent Value\n"
                "**Package 3:** 7 Days | 4 Pings — 1x La Secret / Garama / Equivalent Value\n"
                "**Package 4:** 12 Days | 6 Pings — 1x Cerberus / 4 Garamas / Equivalent Value\n\n"
                "Please tell us which package you want and wait for staff."
            ),
            color=0xED4245
        )
    else:  # rolls
        embed = discord.Embed(
            title=f"Ticket opened by {member.name}",
            description=(
                "**💰 Pay for Rolls**\n\n"
                "Thank you for opening a Pay for Rolls ticket.\n\n"
                "Please tell us:\n"
                "• How many rolls you want\n"
                "• What you are offering as payment\n\n"
                "A Founder / Owner / Co Owner will assist you shortly."
            ),
            color=0xED4245
        )

    await channel.send(
        content=get_staff_mentions(ticket_type),
        embed=embed,
        view=TicketButtons()
    )

    await interaction.response.send_message(f"Ticket created: {channel.mention}", ephemeral=True)


# ==================== CREATE INDEX TICKET ====================
async def create_index_ticket(interaction: discord.Interaction, base_key: str):
    guild = interaction.guild
    member = interaction.user

    # Prevent multiple open tickets
    for channel in guild.text_channels:
        if channel.topic == f"ticket-{member.id}":
            return await interaction.response.send_message(
                f"You already have an open ticket: {channel.mention}", ephemeral=True
            )

    if base_key not in INDEX_ROLES:
        return await interaction.response.send_message("Invalid base selected.", ephemeral=True)

    config["ticketCounter"] += 1
    save_config()

    display_name = INDEX_DISPLAY.get(base_key, base_key.title())
    price = INDEX_PRICES.get(base_key, "Ask staff")
    role_id = INDEX_ROLES[base_key]
    emoji = INDEX_EMOJIS.get(base_key, "📦")

    # Channel name = the index they are wanting
    channel_name = clean_channel_name(display_name)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        member: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            attach_files=True,
            read_message_history=True
        ),
        guild.me: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            manage_channels=True,
            manage_messages=True
        )
    }

    # Allow all staff + the specific index role
    for role_id_str in ALL_STAFF_ROLES + [role_id]:
        role = guild.get_role(int(role_id_str))
        if role:
            overwrites[role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                attach_files=True,
                read_message_history=True,
                manage_messages=True
            )

    category = guild.get_channel(INDEX_CATEGORY_ID)

    channel = await guild.create_text_channel(
        name=channel_name,
        category=category,
        topic=f"ticket-{member.id}",
        overwrites=overwrites
    )

    embed = discord.Embed(
        title=f"{emoji} Index Request: {display_name}",
        description=(
            f"**Ticket opened by {member.mention}**\n\n"
            f"**Base:** {display_name}\n"
            f"**Price:** {price}\n\n"
            "**Index Base Rules**\n"
            "1. PLEASE HAVE AN EMPTY BASE\n"
            "2. IF YOU FAIL TO RETURN A BRAINROT THE INDEX WILL BE CANCELED\n"
            "3. HIGH VALUE BRAINROTS WILL BE GIVEN ONE AT A TIME\n\n"
            "We only take Garam's+ so please do not waste our time with lowballs.\n\n"
            "Please wait for the indexer to assist you."
        ),
        color=0xED4245
    )

    await channel.send(
        content=f"<@&{role_id}>",
        embed=embed,
        view=TicketButtons()
    )

    await interaction.response.send_message(f"Index ticket created: {channel.mention}", ephemeral=True)



# ==================== MIDDLEMAN SELECT + MODAL ====================
class MiddlemanModal(discord.ui.Modal, title="MiddleMan Request"):
    def __init__(self, trade_type: str):
        super().__init__()
        self.trade_type = trade_type

        self.trade_with = discord.ui.TextInput(
            label="Who is the trade with?",
            placeholder="Ex: @mari",
            required=True,
            max_length=100
        )
        self.trade_details = discord.ui.TextInput(
            label="What is the trade?",
            placeholder="Ex: Dragon for garamas",
            required=True,
            max_length=200
        )
        self.tip = discord.ui.TextInput(
            label="What is the tip?",
            placeholder="Please tip 10% of the trade or it might get closed.",
            required=True,
            max_length=100
        )
        self.add_item(self.trade_with)
        self.add_item(self.trade_details)
        self.add_item(self.tip)

    async def on_submit(self, interaction: discord.Interaction):
        await create_middleman_ticket(
            interaction,
            self.trade_type,
            self.trade_with.value,
            self.trade_details.value,
            self.tip.value
        )


class MiddlemanSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Cross Trades",
                description="Cross trade middleman service",
                value="cross",
                emoji="⬡"
            ),
            discord.SelectOption(
                label="OG Trades",
                description="OG trade middleman service",
                value="og",
                emoji="🥇"
            ),
            discord.SelectOption(
                label="1B+ Trades",
                description="1B+ value middleman service",
                value="1b",
                emoji="🥈"
            ),
            discord.SelectOption(
                label="250M-1B Trades",
                description="250M to 1B middleman service",
                value="250m",
                emoji="🥉"
            ),
            discord.SelectOption(
                label="0-250M Trades",
                description="0 to 250M middleman service",
                value="0-250m",
                emoji="✅"
            ),
        ]
        super().__init__(
            placeholder="Select an option",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="middleman_select"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(MiddlemanModal(self.values[0]))


class MiddlemanView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(MiddlemanSelect())


async def create_middleman_ticket(interaction: discord.Interaction, trade_type: str, trade_with: str, trade_details: str, tip: str):
    guild = interaction.guild
    member = interaction.user

    # Prevent multiple open tickets
    for channel in guild.text_channels:
        if channel.topic == f"ticket-{member.id}":
            return await interaction.response.send_message(
                f"You already have an open ticket: {channel.mention}", ephemeral=True
            )

    if trade_type not in MM_ROLES:
        return await interaction.response.send_message("Invalid trade type selected.", ephemeral=True)

    config["ticketCounter"] += 1
    save_config()

    display_name = MM_DISPLAY.get(trade_type, trade_type)
    role_id = MM_ROLES[trade_type]
    emoji = MM_EMOJIS.get(trade_type, "🤝")

    # Channel name = the option they picked
    channel_name = clean_channel_name(display_name)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        member: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            attach_files=True,
            read_message_history=True
        ),
        guild.me: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            manage_channels=True,
            manage_messages=True
        )
    }

    # Allow all staff + only the specific middleman role for this ticket type
    for role_id_str in ALL_STAFF_ROLES + [role_id]:
        role = guild.get_role(int(role_id_str))
        if role:
            overwrites[role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                attach_files=True,
                read_message_history=True,
                manage_messages=True
            )

    category = guild.get_channel(MM_CATEGORY_ID)

    channel = await guild.create_text_channel(
        name=channel_name,
        category=category,
        topic=f"ticket-{member.id}",
        overwrites=overwrites
    )

    embed = discord.Embed(
        title=f"{emoji} MiddleMan Request: {display_name}",
        description=(
            f"**Ticket opened by {member.mention}**\n\n"
            f"**Service:** {display_name}\n"
            f"**Trade with:** {trade_with}\n"
            f"**Trade:** {trade_details}\n"
            f"**Tip:** {tip}\n\n"
            "A middleman will assist you shortly.\n"
            "Please wait and do not ping staff repeatedly."
        ),
        color=0xED4245
    )

    # Only ping the specific middleman role for this ticket type
    await channel.send(
        content=f"<@&{role_id}>",
        embed=embed,
        view=TicketButtons()
    )

    await interaction.response.send_message(f"MiddleMan ticket created: {channel.mention}", ephemeral=True)


# ==================== CLOSE TICKET ====================
async def close_ticket(channel: discord.TextChannel, closer: discord.Member):
    # Generate transcript quickly then delete channel immediately
    try:
        messages = [msg async for msg in channel.history(limit=50, oldest_first=True)]
        transcript = "---- TICKET LOGS ----\n\n"
        for msg in messages:
            time = msg.created_at.strftime("%d/%m/%Y %H:%M")
            transcript += f"{time} - {msg.author}: {msg.content}\n"
            if msg.embeds:
                transcript += f"<EMBED {msg.embeds[0].title or 'Embed'}>\n"

        with open("log.txt", "w", encoding="utf-8") as f:
            f.write(transcript)

        log_channel = bot.get_channel(int(config.get("transcriptChannelId", 0) or 0))
        if log_channel:
            await log_channel.send(
                content=f"Ticket closed by {closer} ({closer.id})\nChannel: `{channel.name}`",
                file=discord.File("log.txt", filename="log.txt")
            )
    except:
        pass

    # Delete channel immediately
    try:
        await channel.delete()
    except:
        pass

    if os.path.exists("log.txt"):
        try:
            os.remove("log.txt")
        except:
            pass


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
    bot.add_view(MiddlemanView())


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
            f"🟡 **Gold Base** — <@&{INDEX_ROLES['gold']}>\n"
            f"💠 **Diamond Base** — <@&{INDEX_ROLES['diamond']}>\n"
            f"🌈 **Rainbow Base** — <@&{INDEX_ROLES['rainbow']}>\n"
            f"🌌 **Galaxy Base** — <@&{INDEX_ROLES['galaxy']}>\n"
            f"🍬 **Candy Base** — <@&{INDEX_ROLES['candy']}>\n"
            f"🌋 **Lava Base** — <@&{INDEX_ROLES['lava']}>\n"
            f"☢️ **Radioactive Base** — <@&{INDEX_ROLES['radioactive']}>\n"
            f"☯️ **YingYang Base** — <@&{INDEX_ROLES['yingyang']}>\n"
            f"☠️ **Cursed Base** — <@&{INDEX_ROLES['cursed']}>\n"
            f"✨ **Divine Base** — <@&{INDEX_ROLES['divine']}>\n"
            f"🤖 **Cyber Base** — <@&{INDEX_ROLES['cyber']}>\n"
            f"👻 **Phantom Base** — <@&{INDEX_ROLES['phantom']}>\n"
            f"💎 **Crystal Base** — <@&{INDEX_ROLES['crystal']}>\n\n"
            "----------------------------------------\n"
            "**Index Base Rules**\n"
            "PLEASE FOLLOW THESE RULES DURING INDEXING\n\n"
            "1. PLEASE HAVE AN EMPTY BASE\n"
            "2. IF YOU FAIL TO RETURN A BRAINROT THE INDEX WILL BE CANCELED\n"
            "3. HIGH VALUE BRAINROTS WILL BE GIVEN ONE AT A TIME\n\n"
            "PLEASE MAKE A TICKET USING THE SELECT MENU BELOW TO PURCHASE\n\n"
            "**CHECK PRICES BELOW**\n"
            "We only take Garam's+ so please do not waste our time with lowballs."
        ),
        color=0xED4245
    )
    await ctx.send(embed=embed, view=IndexView())
    try:
        await ctx.message.delete()
    except:
        pass



@bot.command(name="mmpanel")
@commands.has_permissions(administrator=True)
async def mmpanel_command(ctx: commands.Context):
    embed = discord.Embed(
        title="MiddleMan Services",
        description=(
            "Click bellow to choose one of these trade services\n\n"
            "• **Cross Trades** ⬡\n"
            "• **OG Trades** 🥇\n"
            "• **1B+ Trades** 🥈\n"
            "• **250M-1B Trades** 🥉\n"
            "• **0-250M Trades** ✅\n\n"
            "*Powered by Ticket King*"
        ),
        color=0xED4245
    )
    await ctx.send(embed=embed, view=MiddlemanView())
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

    # Ticket opener OR staff can close
    if not (is_ticket_opener(ctx.channel, ctx.author) or has_staff_permission(ctx.author)):
        return await ctx.reply("❌ Only staff or the ticket owner can close tickets.", mention_author=False)

    await close_ticket(ctx.channel, ctx.author)


@bot.command(name="add")
async def add_command(ctx: commands.Context, *, user_input: str = None):
    """Add a user to the current ticket"""
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
    """Remove a user from the current ticket"""
    if not has_high_staff_permission(ctx.author):
        return await ctx.reply("❌ You do not have permission to use this command.", mention_author=False)

    if not ctx.channel.topic or not str(ctx.channel.topic).startswith("ticket-"):
        return await ctx.reply("❌ This command can only be used inside ticket channels.")

    if not user_input:
        return await ctx.reply("❌ Please provide a user.\nExample: `+remove @user` or `+remove 123456789` or `+remove username`")

    target = await resolve_member(ctx, user_input)
    if not target:
        return await ctx.reply("❌ Could not find that user.")

    # Don't allow removing the ticket opener
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


# ==================== RUN ====================
bot.run(os.getenv("TOKEN") or config.get("token"))
