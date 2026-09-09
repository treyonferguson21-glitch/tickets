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

# Extra roles that can see every ticket type EXCEPT Index and Middleman, and get pinged
# Can +add only in Support, Report (scammer), and Middleman tickets
EXTRA_PANEL_ROLES = [
    "1546912446004994108",  # supervisor
    "1545847662392119367",  # head manager
    "1547283985271365662",  # ticket manager
]

# All roles that can see Support + Scammer tickets
# NOTE: Index and MM tickets do NOT use this list — only the specific service role can see them
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
    "1546192012435390515",  # overlord
    "1512494871171043541",  # manager
    "1546912446004994108",  # supervisor
    "1545847662392119367",  # head manager
    "1547283985271365662",  # ticket manager
]

# Ads ticket visibility
ADS_STAFF_ROLES = [
    "1545842045258825809",  # Creator
    "1512494871171043543",  # owner
    "1546912446004994108",  # supervisor
    "1545847662392119367",  # head manager
    "1547283985271365662",  # ticket manager
]

# Administrator and above — can +add/+remove on all tickets EXCEPT Index and MM
ADMIN_AND_ABOVE_ROLES = [
    "1545842045258825809",  # Creator
    "1545482300601405590",  # Mari
    "1512494871171043543",  # owners
    "1544803993480466563",  # co owners
    "1534637036542365787",  # king
    "1546192012435390515",  # overlord
    "1512494871171043541",  # manager
    "1545847662392119367",  # head manager
    "1512494871171043540",  # Administrator
]

# Used for +mmpanel command permission (admin-level)
HIGH_STAFF_ROLES = [
    "1545842045258825809",  # Creator
    "1545482300601405590",  # Mari
    "1512494871171043543",  # owner
    "1544803993480466563",  # co owner
    "1534637036542365787",  # king
    "1546192012435390515",  # overlord
    "1512494871171043541",  # manager
    "1512494871171043540",  # Administrator
    "1545847662392119367",  # head manager
    "1543926509520293908",  # head staff
    "1546912446004994108",  # supervisor
    "1547283985271365662",  # ticket manager
]

# Pay for Rolls ticket visibility
ROLLS_STAFF_ROLES = [
    "1545842045258825809",  # Creator
    "1512494871171043543",  # owner
    "1544803993480466563",  # co owner
    "1546912446004994108",  # supervisor
    "1545847662392119367",  # head manager
    "1547283985271365662",  # ticket manager
]

# Category IDs used to detect ticket type for +add/+remove
SUPPORT_CATEGORY_ID = 1545526574592303134
SCAMMER_CATEGORY_ID = 1546222360179376290
REWARD_CATEGORY_ID = 1545526714573004831


# ==================== MIDDLEMAN SERVICE ====================
MM_CATEGORY_ID = 1546222244995539024  # where middleman tickets go

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
    "cross": "🟡",
    "og": "🥇",
    "1b": "🥈",
    "250m": "🥉",
    "0-250m": "✅",
}

ALL_MM_ROLES = list(MM_ROLES.values())

# ==================== REACTION ROLES (Game Access) ====================
REACTION_ROLES = {
    "🧠": 1512494871045210206,   # SAB
    "🍉": 1512494871045210207,   # Blox Fruits
    "🌱": 1512494871045210205,   # GAG2
    "🎮": 1545889711116124222,   # Other Games
    "⚔️": 1546202492440682496,   # JJS
}

REACTION_ROLE_LABELS = {
    "🧠": "SAB",
    "🍉": "BLOX FRUITS",
    "🌱": "GAG2",
    "🎮": "OTHER GAMES",
    "⚔️": "JJS",
}



# ==================== STAFF / RECRUITMENT PANEL ====================
STAFF_CATEGORY_IDS = {
    "recruitment": 1545919848490733718,    # MOD / staff application
    "payrolls": 1545919791670370475,       # Pay for rolls
    "indexprovider": 1545919725228400800,  # Indexers application
    "mmapplication": 1545919661584158910,  # MM application
}

STAFF_PANEL_ROLES = [
    "1545842045258825809",  # Creator
    "1512494871171043543",  # owner
    "1544803993480466563",  # co owner
    "1546192012435390515",  # overlord
    "1546912446004994108",  # supervisor
    "1545847662392119367",  # head manager
    "1547283985271365662",  # ticket manager
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

# All index role IDs for staff permission checks
ALL_INDEX_ROLES = list(INDEX_ROLES.values())


def save_config():
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)


def get_staff_mentions(ticket_type="support"):
    # Overlord (1546192012435390515) is pinged on every ticket except Index and MM
    # EXTRA_PANEL_ROLES (supervisor, head manager, ticket manager) are also pinged on every ticket except Index and MM
    extra = [
        "1546912446004994108",  # supervisor
        "1545847662392119367",  # head manager
        "1547283985271365662",  # ticket manager
    ]
    if ticket_type == "ads":
        roles = [
            "1545842045258825809",  # Creator
            "1545482300601405590",  # Mari
            "1512494871171043543",  # owner
            "1546192012435390515",  # overlord
        ] + extra
    elif ticket_type == "rolls":
        roles = [
            "1545842045258825809",  # Creator
            "1512494871171043543",  # owner
            "1544803993480466563",  # co owner
            "1546192012435390515",  # overlord
        ] + extra
    elif ticket_type == "support":
        roles = [
            "1545842045258825809",  # Creator
            "1545482300601405590",  # Mari
            "1512494871171043543",  # owner
            "1512494871171043541",  # manager
            "1545847662392119367",  # head manager
            "1544803993480466563",  # co owner
            "1546192012435390515",  # overlord
            "1545140559365283972",  # extra support ping
            "1546912446004994108",  # supervisor
            "1547283985271365662",  # ticket manager
        ]
    else:
        # scammer / reward / default
        roles = [
            "1545842045258825809",  # Creator
            "1545482300601405590",  # Mari
            "1512494871171043543",  # owner
            "1512494871171043541",  # manager
            "1545847662392119367",  # head manager
            "1544803993480466563",  # co owner
            "1546192012435390515",  # overlord
            "1546912446004994108",  # supervisor
            "1547283985271365662",  # ticket manager
        ]
    # Deduplicate while preserving order
    seen = set()
    unique_roles = []
    for r in roles:
        if r not in seen:
            seen.add(r)
            unique_roles.append(r)
    return " ".join([f"<@&{r}>" for r in unique_roles])


def has_staff_permission(member: discord.Member):
    try:
        all_roles = ALL_STAFF_ROLES + SUPPORT_ONLY_ROLES + REWARD_STAFF_ROLES + ADS_STAFF_ROLES + ALL_INDEX_ROLES + ALL_MM_ROLES + EXTRA_PANEL_ROLES
        return any(str(role.id) in all_roles for role in member.roles)
    except:
        return False


def has_high_staff_permission(member: discord.Member):
    """For +mmpanel and similar admin-level commands"""
    try:
        return any(str(role.id) in HIGH_STAFF_ROLES for role in member.roles)
    except:
        return False


def member_has_any_role(member: discord.Member, role_ids) -> bool:
    try:
        return any(str(role.id) in role_ids for role in member.roles)
    except:
        return False


def get_ticket_kind(channel: discord.TextChannel) -> str:
    """Return ticket kind based on category: support, scammer, reward, ads_or_rolls, index, mm, staff, unknown"""
    if not channel or not channel.category_id:
        return "unknown"
    cat = channel.category_id
    if cat == INDEX_CATEGORY_ID:
        return "index"
    if cat == MM_CATEGORY_ID:
        return "mm"
    if cat == SCAMMER_CATEGORY_ID:
        return "scammer"
    if cat == REWARD_CATEGORY_ID:
        return "reward"
    if cat == SUPPORT_CATEGORY_ID:
        return "support"  # also used for ads + rolls
    if cat in STAFF_CATEGORY_IDS.values():
        return "staff"
    return "unknown"


def can_add_or_remove(member: discord.Member, channel: discord.TextChannel) -> bool:
    """
    +add / +remove rules:
    - Index tickets: nobody (staff cannot manage members here)
    - MM tickets: any MM role OR EXTRA_PANEL_ROLES (supervisor / head manager / ticket manager)
    - Support + Scammer (report): EXTRA_PANEL_ROLES OR Administrator and above
    - All other tickets (reward, ads, rolls, staff): Administrator and above only
    """
    kind = get_ticket_kind(channel)

    if kind == "index":
        return False

    if kind == "mm":
        return (
            member_has_any_role(member, ALL_MM_ROLES)
            or member_has_any_role(member, EXTRA_PANEL_ROLES)
        )

    if kind in ("support", "scammer"):
        return (
            member_has_any_role(member, EXTRA_PANEL_ROLES)
            or member_has_any_role(member, ADMIN_AND_ABOVE_ROLES)
        )

    # reward, staff, ads/rolls (support category), unknown
    return member_has_any_role(member, ADMIN_AND_ABOVE_ROLES)


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
        # Ticket opener OR staff can close
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

    # Prevent multiple open tickets
    for channel in guild.text_channels:
        if channel.topic == f"ticket-{member.id}":
            return await interaction.followup.send(
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
        category_id = 1546222360179376290
    elif ticket_type == "reward":
        category_id = 1545526714573004831
    elif ticket_type == "ads":
        category_id = 1545526574592303134
    else:  # rolls
        category_id = 1545526574592303134

    # Choose which roles can see this ticket
    # EXTRA_PANEL_ROLES (supervisor, head manager, ticket manager) see every type except Index/MM
    if ticket_type == "reward":
        allowed_roles = REWARD_STAFF_ROLES
    elif ticket_type == "ads":
        allowed_roles = ADS_STAFF_ROLES
    elif ticket_type == "rolls":
        allowed_roles = ROLLS_STAFF_ROLES
    elif ticket_type == "support":
        allowed_roles = ALL_STAFF_ROLES + SUPPORT_ONLY_ROLES + EXTRA_PANEL_ROLES
    else:  # scammer/report
        allowed_roles = ALL_STAFF_ROLES + EXTRA_PANEL_ROLES

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

    await interaction.followup.send(f"Ticket created: {channel.mention}", ephemeral=True)


# ==================== CREATE INDEX TICKET ====================
async def create_index_ticket(interaction: discord.Interaction, base_key: str):
    guild = interaction.guild
    member = interaction.user

    # Prevent multiple open tickets
    for channel in guild.text_channels:
        if channel.topic == f"ticket-{member.id}":
            return await interaction.followup.send(
                f"You already have an open ticket: {channel.mention}", ephemeral=True
            )

    if base_key not in INDEX_ROLES:
        return await interaction.followup.send("Invalid base selected.", ephemeral=True)

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

    # ONLY the specific index role can see this ticket (no general staff)
    role = guild.get_role(int(role_id))
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

    await interaction.followup.send(f"Index ticket created: {channel.mention}", ephemeral=True)



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
                emoji="🟡"
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
            return await interaction.followup.send(
                f"You already have an open ticket: {channel.mention}", ephemeral=True
            )

    if trade_type not in MM_ROLES:
        return await interaction.followup.send("Invalid trade type selected.", ephemeral=True)

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

    # ONLY the specific middleman role can see this ticket (no general staff)
    role = guild.get_role(int(role_id))
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

    await interaction.followup.send(f"MiddleMan ticket created: {channel.mention}", ephemeral=True)



# ==================== STAFF PANEL SELECT ====================
class StaffPanelSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Staff Application",
                description="Apply for a staff position on the team",
                value="recruitment",
                emoji="📝"
            ),
            discord.SelectOption(
                label="Pay for Rolls",
                description="Purchase secure rolls for staff",
                value="payrolls",
                emoji="🎟️"
            ),
            discord.SelectOption(
                label="Index Provider",
                description="Apply to become an index provider",
                value="indexprovider",
                emoji="📦"
            ),
            discord.SelectOption(
                label="Middleman Application",
                description="Apply to become a middleman",
                value="mmapplication",
                emoji="🤝"
            ),
        ]
        super().__init__(
            placeholder="Choose a staff option...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="staff_panel_select"
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await create_staff_ticket(interaction, self.values[0])


class StaffPanelView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(StaffPanelSelect())


async def create_staff_ticket(interaction: discord.Interaction, ticket_type: str):
    guild = interaction.guild
    member = interaction.user

    for channel in guild.text_channels:
        if channel.topic == f"ticket-{member.id}":
            return await interaction.followup.send(
                f"You already have an open ticket: {channel.mention}", ephemeral=True
            )

    category_id = STAFF_CATEGORY_IDS.get(ticket_type)
    if not category_id:
        return await interaction.followup.send(
            "Staff category is not set for this option. Please contact an administrator.", ephemeral=True
        )

    config["ticketCounter"] += 1
    save_config()

    # Channel name = username (same as other tickets)
    channel_name = clean_channel_name(member.name)

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

    for role_id_str in STAFF_PANEL_ROLES:
        role = guild.get_role(int(role_id_str))
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

    # Pings:
    # - Pay for Rolls: Creator + Owner + Overlord + EXTRA_PANEL_ROLES
    # - Other staff tickets: Creator, Owner, Co Owner, Overlord + EXTRA_PANEL_ROLES
    extra_ping = " ".join([
        "<@&1546912446004994108>",  # supervisor
        "<@&1545847662392119367>",  # head manager
        "<@&1547283985271365662>",  # ticket manager
    ])
    if ticket_type == "payrolls":
        ping = f"<@&1545842045258825809> <@&1512494871171043543> <@&1546192012435390515> {extra_ping}"  # Creator + Owner + Overlord + extra
    else:
        ping = " ".join([
            "<@&1545842045258825809>",  # Creator
            "<@&1512494871171043543>",  # Owner
            "<@&1544803993480466563>",  # Co Owner
            "<@&1546192012435390515>",  # Overlord
        ]) + " " + extra_ping

    if ticket_type == "recruitment":
        embed = discord.Embed(
            title="📝 Staff Application",
            description=(
                f"Welcome {member.mention}! Thanks for applying to join the team.\n\n"
                "Please answer **every question** below honestly and professionally. "
                "A recruiter will review your application shortly.\n\n"
                "**Application Form**\n"
                "```\n"
                "1. Discord Username:\n"
                "2. Age:\n"
                "3. Are you fluent in English?\n"
                "4. How many days per week are you active?\n"
                "5. How many hours per day are you usually online?\n"
                "6. How would you handle a toxic member breaking the rules?\n"
                "7. Do you have any previous moderation or staff experience?\n"
                "   (If yes, please explain)\n"
                "8. Why do you want to become a staff member?\n"
                "9. Anything else you would like us to know?\n"
                "```\n\n"
                "Copy the form, fill it out, and send it in this ticket."
            ),
            color=0x000000
        )
        embed.set_footer(text="Staff Recruitment")
    elif ticket_type == "payrolls":
        embed = discord.Embed(
            title="🎟️ Pay for Rolls",
            description=(
                f"Ticket opened by {member.mention}\n\n"
                "**Staff Pay Rates**\n"
                "```\n"
                "Test Mod          — 2 Garams\n"
                "Moderator         — 3 Garams\n"
                "Senior Moderator  — 4 Garams\n"
                "Head Staff        — 5 Garams\n"
                "Admin             — 7 Garams OR 1 Colored Garam\n"
                "Manager           — 2 Colored Garams\n"
                "Head Manager      — 3 Colored Garams\n"
                "```\n\n"
                "Tell us which role you are paying for and what you are offering. "
                "A Creator / Owner will assist you shortly."
            ),
            color=0x000000
        )
        embed.set_footer(text="Pay for Rolls")
    elif ticket_type == "indexprovider":
        embed = discord.Embed(
            title="📦 Index Provider Application",
            description=(
                f"Welcome {member.mention}!\n\n"
                "Thanks for your interest in becoming an **Index Provider**.\n\n"
                "**Payment & Collat:** 1+ Drag\n\n"
                "Please tell us:\n"
                "• Why you want to be an index provider\n"
                "• How active you are\n"
                "• Any relevant experience\n\n"
                "Staff will review your request soon."
            ),
            color=0x000000
        )
        embed.set_footer(text="Index Provider")
    else:  # mmapplication
        embed = discord.Embed(
            title="🤝 Middleman Application",
            description=(
                f"Welcome {member.mention}!\n\n"
                "Thanks for applying to become a **Middleman**.\n\n"
                "**Payment & Collat:** 1+ Drag\n\n"
                "Please tell us:\n"
                "• Why you want to middleman\n"
                "• How often you can be online\n"
                "• Any past middleman experience\n\n"
                "Staff will get back to you shortly."
            ),
            color=0x000000
        )
        embed.set_footer(text="Middleman Application")

    await channel.send(content=ping, embed=embed, view=TicketButtons())
    await interaction.followup.send(f"Ticket created: {channel.mention}", ephemeral=True)


# ==================== CLOSE TICKET ====================
async def close_ticket(channel: discord.TextChannel, closer: discord.Member) -> bool:
    """Close ticket, send transcript, then permanently delete the channel."""
    channel_name = channel.name
    channel_id = channel.id
    guild = channel.guild

    # Mark as closed so it can't be treated as open anymore
    try:
        await channel.edit(topic="closed", reason="Ticket closing")
    except:
        pass

    # Snapshot transcript (best effort — never block delete)
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

    # Always try to delete — up to 5 attempts
    for attempt in range(5):
        try:
            ch = guild.get_channel(channel_id)
            if ch is None:
                print(f"Channel {channel_name} already gone")
                return True
            await ch.delete(reason=f"Ticket closed by {closer}")
            print(f"Deleted ticket channel: {channel_name} ({channel_id})")
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
    bot.add_view(MiddlemanView())
    bot.add_view(StaffPanelView())



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
    """Posts the invite rewards panel to the invite channel"""
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
    """Posts the LEOS Middleman reaction role panel"""
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
            "🟡 **Gold Base**\n"
            "💠 **Diamond Base**\n"
            "🌈 **Rainbow Base**\n"
            "🌌 **Galaxy Base**\n"
            "🍬 **Candy Base**\n"
            "🌋 **Lava Base**\n"
            "☢️ **Radioactive Base**\n"
            "☯️ **YingYang Base**\n"
            "☠️ **Cursed Base**\n"
            "✨ **Divine Base**\n"
            "🤖 **Cyber Base**\n"
            "👻 **Phantom Base**\n"
            "💎 **Crystal Base**\n\n"
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
    await ctx.send(embed=embed, view=StaffPanelView())
    try:
        await ctx.message.delete()
    except:
        pass


@bot.command(name="mmpanel")
async def mmpanel_command(ctx: commands.Context):
    # Admin Discord perm OR high staff roles
    if not (ctx.author.guild_permissions.administrator or has_high_staff_permission(ctx.author)):
        return await ctx.reply("❌ You do not have permission to use this command.", mention_author=False)

    embed = discord.Embed(
        title="MiddleMan Services",
        description=(
            "Click bellow to choose one of these trade services\n\n"
            "• **Cross Trades** 🟡\n"
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

    # Ticket opener OR staff can close
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
    """Add a user to the current ticket"""
    if not ctx.channel.topic or not str(ctx.channel.topic).startswith("ticket-"):
        return await ctx.reply("❌ This command can only be used inside ticket channels.")

    if not can_add_or_remove(ctx.author, ctx.channel):
        return await ctx.reply("❌ You do not have permission to add users to this ticket.", mention_author=False)

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
    if not ctx.channel.topic or not str(ctx.channel.topic).startswith("ticket-"):
        return await ctx.reply("❌ This command can only be used inside ticket channels.")

    if not can_add_or_remove(ctx.author, ctx.channel):
        return await ctx.reply("❌ You do not have permission to remove users from this ticket.", mention_author=False)

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



@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingPermissions):
        return await ctx.reply("❌ You do not have permission to use this command.", mention_author=False)
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        return await ctx.reply(f"❌ Missing argument: `{error.param.name}`", mention_author=False)
    # Log unexpected errors
    try:
        await ctx.reply(f"❌ Error: `{error}`", mention_author=False)
    except:
        pass
    print(f"Command error in {ctx.command}: {error}")


# ==================== RUN ====================
bot.run(os.getenv("TOKEN") or config.get("token"))
