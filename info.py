class BotInfoView(discord.ui.View):

    def __init__(self, bot_user_id: int):
        super().__init__(timeout=None)

        # Кнопка добавления бота
        invite_url = (
            "https://discord.com/oauth2/authorize"
            f"?client_id={bot_user_id}"
            "&permissions=8"
            "&scope=bot%20applications.commands"
        )

        self.add_item(
            discord.ui.Button(
                label="Добавить бота",
                emoji="🤖",
                style=discord.ButtonStyle.link,
                url=invite_url
            )
        )

        # Кнопка сервера поддержки
        self.add_item(
            discord.ui.Button(
                label="Сервер поддержки",
                emoji="💬",
                style=discord.ButtonStyle.link,
                url=SUPPORT_SERVER_URL
            )
        )
@bot.tree.command(
    name="info",
    description="Информация о боте и системе защиты"
)
async def botinfo(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🛡️ Anti-Scam Security",
        description=(
            "Автоматическая система защиты Discord-серверов "
            "от фишинга, скам-ссылок и вредоносных сообщений.\n\n"
            
            "Бот автоматически создаёт специальный канал-ловушку, "
            "который используется для обнаружения пользователей, "
            "пытающихся отправить подозрительный контент."
        ),
        color=discord.Color.red(),
        timestamp=datetime.now()
    )

    # Возможности
    embed.add_field(
        name="🚨 Канал-ловушка",
        value=(
            "Создаёт специальный канал, в котором любое сообщение "
            "обычного участника приводит к автоматическому бану."
        ),
        inline=False
    )

    embed.add_field(
        name="🔨 Автоматический бан",
        value=(
            "Сообщение нарушителя удаляется, после чего бот "
            "выдаёт перманентный бан с причиной:\n"
            "`Антискам: сообщение в канале-ловушке`"
        ),
        inline=False
    )

    embed.add_field(
        name="📋 Логи",
        value=(
            "Все автоматические баны записываются в отдельный "
            "закрытый канал для администраторов.\n\n"
            "В лог попадает:\n"
            "• нарушитель\n"
            "• ID пользователя\n"
            "• сообщение\n"
            "• вложения\n"
            "• канал\n"
            "• дата и время"
        ),
        inline=False
    )

    embed.add_field(
        name="🛡️ Защита",
        value=(
            "Бот помогает обнаруживать:\n"
            "• фишинг\n"
            "• скам\n"
            "• подозрительные ссылки\n"
            "• скам-картинки\n"
            "• вредоносные вложения"
        ),
        inline=False
    )

    embed.add_field(
        name="⚙️ Автоматическая настройка",
        value=(
            "После добавления на сервер бот самостоятельно "
            "создаёт необходимые каналы и настраивает систему защиты."
        ),
        inline=False
    )

    embed.add_field(
        name="👨‍💻 Разработчик",
        value="**@fartseason**",
        inline=False
    )

    embed.set_footer(
        text="Anti-Scam Security • Защита Discord-серверов"
    )

    # Аватар бота
    if bot.user.avatar:
        embed.set_thumbnail(
            url=bot.user.avatar.url
        )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True,
        view=BotInfoView(bot.user.id)
    )

