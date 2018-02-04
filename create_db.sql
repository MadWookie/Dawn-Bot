CREATE TABLE privatechannels (
    guild_id bigint,
    channel_num smallint,
    owner_id bigint,
    password text,
    UNIQUE(guild_id, channel_num)
);