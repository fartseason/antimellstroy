async def get_server_invite(guild: discord.Guild):
    try:
        if guild.vanity_url:
            return str(guild.vanity_url)
    except:
        pass
    channels = []

    if guild.system_channel:
        channels.append(guild.system_channel)

    channels.extend(guild.text_channels)

    checked = set()

    for channel in channels:

        if channel.id in checked:
            continue

        checked.add(channel.id)

        try:

            permissions = channel.permissions_for(
                guild.me
            )

            if not permissions.create_instant_invite:
                continue

            invite = await channel.create_invite(
                max_age=0,
                max_uses=0,
                unique=False,
                reason="Получение ссылки для команды !servers"
            )

            return invite.url

        except Exception:
            continue

    return None


class ServersView(discord.ui.View):

    def __init__(
        self,
        guilds,
        author_id,
        page=0
    ):

        super().__init__(timeout=300)

        self.guilds = guilds
        self.author_id = author_id
        self.page = page

        self.per_page = 10

        self.max_page = max(
            0,
            (len(guilds) - 1) // self.per_page
        )

        self.update_buttons()
    async def interaction_check(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.author_id:

            await interaction.response.send_message(
                "❌ Эта панель принадлежит другому пользователю.",
                ephemeral=True
            )

            return False

        return True
    def update_buttons(self):

        self.previous_button.disabled = (
            self.page <= 0
        )

        self.next_button.disabled = (
            self.page >= self.max_page
        )
    @discord.ui.button(
        label="Назад",
        emoji="◀️",
        style=discord.ButtonStyle.secondary
    )
    async def previous_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if self.page > 0:

            self.page -= 1

        self.update_buttons()

        embed = await create_servers_embed(
            self.guilds,
            self.page
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )
    @discord.ui.button(
        label="Далее",
        emoji="▶️",
        style=discord.ButtonStyle.primary
    )
    async def next_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if self.page < self.max_page:

            self.page += 1

        self.update_buttons()

        embed = await create_servers_embed(
            self.guilds,
            self.page
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )
async def create_servers_embed(
    guilds,
    page
):

    per_page = 10

    start = page * per_page
    end = start + per_page

    current_guilds = guilds[
        start:end
    ]

    max_page = max(
        0,
        (len(guilds) - 1) // per_page
    )

    embed = discord.Embed(
        title="📋 Серверы бота",
        description=(
            f"🛡️ Бот находится на "
            f"**{len(guilds)} серверах**.\n\n"
            f"📄 Страница **{page + 1}/{max_page + 1}**"
        ),
        color=discord.Color.blurple(),
        timestamp=datetime.now()
    )
    for index, guild in enumerate(
        current_guilds,
        start=start + 1
    ):

        invite = await get_server_invite(
            guild
        )

        # Количество участников
        member_count = guild.member_count or 0

        if invite:

            value = (
                f"👥 Участников: **{member_count:,}**\n"
                f"🆔 ID: `{guild.id}`\n"
                f"🔗 [Перейти на сервер]({invite})"
            )

        else:

            value = (
                f"👥 Участников: **{member_count:,}**\n"
                f"🆔 ID: `{guild.id}`\n"
                f"🔗 Ссылка недоступна"
            )

        embed.add_field(
            name=f"{index}. {guild.name}",
            value=value,
            inline=False
        )
    embed.set_footer(
        text=(
            "Anti-Scam Security • "
            f"Всего серверов: {len(guilds)}"
        )
    )

    return embed
@bot.command(
    name="servers"
)
async def servers_command(ctx):
    if ctx.author.id != SERVERS_OWNER_ID:

        await ctx.reply(
            "❌ У тебя нет доступа к этой команде.",
            mention_author=False
        )

        return
    guilds = sorted(
        bot.guilds,
        key=lambda guild: guild.name.lower()
    )

    if not guilds:

        await ctx.send(
            "❌ Бот сейчас не находится ни на одном сервере."
        )

        return

    # =========================
    # EMBED
    # =========================

    embed = await create_servers_embed(
        guilds,
        0
    )

    view = ServersView(
        guilds=guilds,
        author_id=ctx.author.id,
        page=0
    )

    await ctx.send(
        embed=embed,
        view=view
    )
