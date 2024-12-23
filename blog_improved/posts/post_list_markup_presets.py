from blog_improved.posts.post_list_markup import PostListMarkup

POST_LIST_GRID_PRESETS = {
    "standard_3by3": {
        "rows": 3,
        "columns": 3,
        "proportions": (33, 33, 33),
    },
    "standard_4by4": {
        "rows": 4,
        "columns": 4,
        "proportions": (25, 25, 25, 25),
    },
}

# Function to fetch preset and construct the object
def create_post_list_markup(name, posts, preset_name, sgml):
    # Fetch the preset configuration
    preset = POST_LIST_GRID_PRESETS.get(preset_name)
    if not preset:
        raise ValueError(f"Preset '{preset_name}' not found.")

    # Unpack preset and pass to the constructor
    return PostListMarkup(
        name=name,
        posts=posts,
        rows=preset["rows"],
        columns=preset["columns"],
        proportions=preset["proportions"],
        sgml=sgml,
    )
