@bot.tree.command(
    name="security",
    description="Проверить состояние антискам системы"
)
@app_commands.default_permissions(administrator=True)
async def security(interaction: discord.Interaction):

    trap_channel = discord.utils.get(
        interaction.guild.text_channels,
        name=TRAP_CHANNEL_NAME
    )

    log_channel = discord.utils.get(
        interaction.guild.text_channels,
        name=LOG_CHANNEL_NAME
    )

    embed = discord.Embed(
        title="🛡️ Security System",
        color=discord.Color.green()
    )

    embed.add_field(
        name="🚨 Ловушка",
        value=(
            trap_channel.mention
            if trap_channel
            else "❌ Не найдена"
        ),
        inline=False
    )

    embed.add_field(
        name="📋 Логи",
        value=(
            log_channel.mention
            if log_channel
            else "❌ Не найдены"
        ),
        inline=False
    )

    embed.add_field(
        name="Статус",
        value="🟢 Активна",
        inline=False
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )
