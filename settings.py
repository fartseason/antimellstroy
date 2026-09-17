class TimeoutModal(discord.ui.Modal, title="⏱️ Настройка тайм-аута"):

    minutes = discord.ui.TextInput(
        label="Продолжительность в минутах",
        placeholder="Например: 30",
        required=True,
        min_length=1,
        max_length=5
    )

    def __init__(self, guild_id):
        super().__init__()
        self.guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):

        # Проверяем владельца
        if interaction.guild.owner_id != interaction.user.id:

            await interaction.response.send_message(
                "❌ Только создатель сервера может изменять настройки.",
                ephemeral=True
            )
            return

        try:
            minutes = int(self.minutes.value)

        except ValueError:

            await interaction.response.send_message(
                "❌ Введи число. Например: `30`.",
                ephemeral=True
            )
            return

        # Discord позволяет максимум 28 дней
        if minutes < 1 or minutes > 40320:

            await interaction.response.send_message(
                "❌ Тайм-аут должен быть от **1 до 40320 минут**.",
                ephemeral=True
            )
            return

        guild_settings = get_guild_settings(
            self.guild_id
        )

        guild_settings["punishment"] = "timeout"
        guild_settings["timeout_minutes"] = minutes

        save_settings(settings)

        embed = create_settings_embed(
            interaction.guild
        )

        await interaction.response.edit_message(
            embed=embed,
            view=SettingsView()
        )


def create_settings_embed(guild):

    guild_settings = get_guild_settings(
        guild.id
    )

    punishment = guild_settings["punishment"]

    punishment_names = {
        "ban": "🔨 Бан",
        "kick": "👢 Кик",
        "timeout": "⏱️ Тайм-аут"
    }

    current = punishment_names.get(
        punishment,
        "🔨 Бан"
    )

    embed = discord.Embed(
        title="⚙️ НАСТРОЙКИ ANTI-SCAM",
        description=(
            "Здесь создатель сервера может выбрать "
            "наказание за отправку сообщения в "
            "канал `🚨・ловушка`.\n\n"
            
            f"**Текущее наказание:** {current}\n\n"
            
            "Выберите нужный вариант ниже."
        ),
        color=discord.Color.blurple(),
        timestamp=datetime.now()
    )

    if punishment == "timeout":

        minutes = guild_settings.get(
            "timeout_minutes",
            10
        )

        embed.add_field(
            name="⏱️ Длительность тайм-аута",
            value=f"**{minutes} минут**",
            inline=False
        )

    embed.add_field(
        name="🚨 Как работает система",
        value=(
            "Если участник отправит любое сообщение "
            "в канал-ловушку, бот удалит его сообщение "
            "и применит выбранное наказание."
        ),
        inline=False
    )

    embed.set_footer(
        text="Изменять настройки может только создатель сервера"
    )

    return embed


class SettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Бан",
        emoji="🔨",
        style=discord.ButtonStyle.danger,
        custom_id="settings_ban"
    )
    async def ban_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if interaction.guild.owner_id != interaction.user.id:

            await interaction.response.send_message(
                "❌ Только создатель сервера может изменять настройки.",
                ephemeral=True
            )
            return

        guild_settings = get_guild_settings(
            interaction.guild.id
        )

        guild_settings["punishment"] = "ban"

        save_settings(settings)

        embed = create_settings_embed(
            interaction.guild
        )

        await interaction.response.edit_message(
            embed=embed,
            view=SettingsView()
        )

    @discord.ui.button(
        label="Кик",
        emoji="👢",
        style=discord.ButtonStyle.secondary,
        custom_id="settings_kick"
    )
    async def kick_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if interaction.guild.owner_id != interaction.user.id:

            await interaction.response.send_message(
                "❌ Только создатель сервера может изменять настройки.",
                ephemeral=True
            )
            return

        guild_settings = get_guild_settings(
            interaction.guild.id
        )

        guild_settings["punishment"] = "kick"

        save_settings(settings)

        embed = create_settings_embed(
            interaction.guild
        )

        await interaction.response.edit_message(
            embed=embed,
            view=SettingsView()
        )

    @discord.ui.button(
        label="Тайм-аут",
        emoji="⏱️",
        style=discord.ButtonStyle.primary,
        custom_id="settings_timeout"
    )
    async def timeout_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if interaction.guild.owner_id != interaction.user.id:

            await interaction.response.send_message(
                "❌ Только создатель сервера может изменять настройки.",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            TimeoutModal(
                interaction.guild.id
            )
        )

@bot.tree.command(
    name="settings",
    description="Настройки системы Anti-Scam"
)
async def settings_command(
    interaction: discord.Interaction
):

    # Только создатель сервера
    if interaction.guild.owner_id != interaction.user.id:

        await interaction.response.send_message(
            "❌ Эта команда доступна только **создателю сервера**.",
            ephemeral=True
        )

        return

    embed = create_settings_embed(
        interaction.guild
    )

    await interaction.response.send_message(
        embed=embed,
        view=SettingsView(),
        ephemeral=True
    )
