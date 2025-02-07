from blog_improved.presentation import GridLayout
from blog_improved.posts.post_list_markup import PostListMarkup

layout_presets = {
    "standard_3by3": GridLayout(
        rows=3,
        columns=3,
        row_width=(33,33,33,),
        ),
    "standard_4by4": GridLayout(
        rows=4,
        columns=4,
        row_width=(25,25,25,25,),
        ),
}

# Grab the first key available
try: 
    default_preset = next(iter(layout_presets)) 
    layout_presets["default"] = layout_presets[default_preset]
except StopIteration:
    layout_presets["default"] = {}

# Function to fetch preset and construct the object
def create_post_list_markup(name, posts, preset, sgml):
    if not preset:
        raise ValueError(f"Preset '{preset_name}' not found.")

    # Unpack preset and pass to the constructor
    return PostListMarkup(
        name=name,
        posts=posts,
        rows=preset.rows,
        columns=preset.columns,
        proportions=preset.row_width,
        sgml=sgml,
    )
