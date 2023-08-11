def username_splitter(nickname):
    username = nickname.replace(' ', '')
    username_split = username.rsplit('(', 1)[0]
    if username_split == username:
        username_split = username_split.rsplit('_', 1)[0]
    return username_split