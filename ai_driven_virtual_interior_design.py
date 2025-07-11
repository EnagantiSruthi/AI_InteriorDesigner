import gradio as gr
import torch
from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler
from jinja2 import Template
from IPython.display import display, HTML
# Load the Stable Diffusion model
sd_model_id = "bhoomikagp/sd2-interior-model-version2"
scheduler = EulerDiscreteScheduler.from_pretrained(sd_model_id, subfolder="scheduler")

device = "cuda" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if device == "cuda" else torch.float32

sd_pipeline = StableDiffusionPipeline.from_pretrained(
    sd_model_id,
    torch_dtype=torch_dtype,
    scheduler=scheduler
).to(device)

# Choices lists
option_choices = ["Living Room", "Bedroom", "Kitchen", "Dining Room", "Bathroom", "Office Room", "Laundry Room", "Family Room", "Play Room", "Study Room"]
adj_1_choices = [
    "Large", "Comfortable", "Simple", "Fancy", "New", "Country Style",
    "Rich", "Friendly", "Bright", "Stylish", "Cheerful", "Warm",
    "Peaceful", "Trendy", "Chic"
]
architecture_style_choices = ["New", "Current", "Classic", "Factory", "Scandinavian",
    "Old Style", "Colonial", "Art Style", "Old Classic", "Mediterranean",
    "Pointed", "Fancy", "Japanese", "Rough", "Tropical"]
aesthetic_choices = ["Free Spirit", "Old", "Simple", "Rich", "Mixed",
    "Mid-Century", "Art Style", "Farmhouse", "Industrial",
    "Worn", "Rustic", "Beach", "City", "Mixed",
    "Classic Modern"]
accent_color_choices = ["blue", "green", "beige", "grey", "white", "black", "cream", "brown", "taupe", "burgundy", "mustard", "terracotta", "olive", "peach", "navy"]
wood_finish_choices = ["dark oak", "walnut", "mahogany", "teak", "maple", "cherry", "pine", "birch", "ash", "rosewood", "ebony", "cedar", "hickory", "elm", "red oak"]
wall_color_choices = ["cream", "off-white", "charcoal", "sage green", "navy blue", "taupe", "light grey", "soft pink", "mustard yellow", "deep teal", "warm beige", "pearl white", "slate blue", "coral", "mint green"]
tiles_choices = ["marble", "ceramic", "porcelain", "slate", "wooden-look", "mosaic", "granite", "terracotta", "cement", "quartz", "limestone", "onyx", "travertine", "glass", "encaustic"]

# Cost Data Links
cost_data = {
    "Accent Color": {color: f'<a href="https://materialdepot.in/primary%20color%20{color.replace(" ", "%20")}-search">{color}</a>' for color in accent_color_choices},
    "Wood Finish": {wood: f'<a href="https://materialdepot.in/wood%20finish%20{wood.replace(" ", "%20")}-search">{wood}</a>' for wood in wood_finish_choices},
    "Tiles": {tile: f'<a href="https://materialdepot.in/tiles%20{tile.replace(" ", "%20")}-search">{tile}</a>' for tile in tiles_choices},
    "Wall Color": {color: f'<a href="https://materialdepot.in/wall%20color%20{color.replace(" ", "%20")}-search">{color}</a>' for color in wall_color_choices},
}
def get_selected_cost_links(accent_color, wood_finish, wall_color, tiles):
    selected_links = [
        f"**Accent Color ({accent_color})**: {cost_data['Accent Color'].get(accent_color, 'No link available')}","\n"
        f"**Wood Finish ({wood_finish})**: {cost_data['Wood Finish'].get(wood_finish, 'No link available')}","\n"
        f"**Wall Color ({wall_color})**: {cost_data['Wall Color'].get(wall_color, 'No link available')}","\n"
        f"**Tiles ({tiles})**: {cost_data['Tiles'].get(tiles, 'No link available')}""\n"
    ]
    return "\n".join(selected_links)

# Templates for room descriptions
templates = {
    room: Template(
        """
        High quality, high resolution, interior render of a {{ adj_1 }} {{ room | lower }}, in {{ architecture_style }} architecture,
        with {{ aesthetic }} style, painted in {{ wall_color }} with {{ accent_color }} accents, {{ wood_finish }} wood finishes,
        and {{ tiles }} flooring.
        """
    ) for room in option_choices
}

def generate_prompt(option, adj_1, architecture_style, aesthetic, accent_color, wood_finish, wall_color, tiles):
    return templates[option].render(
        room=option,
        adj_1=adj_1,
        architecture_style=architecture_style,
        aesthetic=aesthetic,
        accent_color=accent_color,
        wood_finish=wood_finish,
        wall_color=wall_color,
        tiles=tiles
    )

def generate_image(option, adj_1, architecture_style, aesthetic, accent_color, wood_finish, wall_color, tiles):
    prompt = generate_prompt(option, adj_1, architecture_style, aesthetic, accent_color, wood_finish, wall_color, tiles)
    generator = torch.manual_seed(torch.randint(0, 2**32, (1,)).item())
    img = sd_pipeline(
        prompt=prompt,
        guidance_scale=7,
        num_inference_steps=20,
        width=640,
        height=640,
        generator=generator
    ).images[0]
    return img

# Gradio UI
with gr.Blocks() as app:

    def display_heading():
      return  """
      <div style='display: flex; justify-content: center; align-items: center; height: 10vh;'>
      <h1 style='font-size: 2rem; font-weight: bold;font-family: "Lucida Handwriting", cursive; background-image: linear-gradient(to right, #FF5733, #FFC300, #4A90E2, #8E44AD); -webkit-background-clip: text; color: transparent;'>AI-Driven Virtual Interior Design</h1>
      </div>
      """

    with gr.Blocks() as demo:
         gr.HTML(display_heading())


    with gr.Row():
        option = gr.Dropdown(label="Room Type", choices=option_choices, value="Living Room")
        adj_1 = gr.Dropdown(label="Primary Adjective", choices=adj_1_choices, value="Modern")
        architecture_style = gr.Dropdown(label="Architecture Style", choices=architecture_style_choices, value="Modern")

    with gr.Row():
        aesthetic = gr.Dropdown(label="Interior Theme", choices=aesthetic_choices, value="Minimalist")
        accent_color = gr.Dropdown(label="Primary Color", choices=accent_color_choices, value="White")
        wood_finish = gr.Dropdown(label="Wood Finish", choices=wood_finish_choices, value="Oak")

    with gr.Row():
        wall_color = gr.Dropdown(label="Wall Color", choices=wall_color_choices, value="Off-White")
        tiles = gr.Dropdown(label="Tile Type", choices=tiles_choices, value="Marble")

    generate_btn = gr.Button("🎨 Generate Image")
    output_image = gr.Image(label="Generated Image")

    calculate_costs_btn = gr.Button("💰 Check Costs")
    costs_output = gr.Markdown("\n")

    generate_btn.click(
        fn=generate_image,
        inputs=[option, adj_1, architecture_style, aesthetic, accent_color, wood_finish, wall_color, tiles],
        outputs=output_image
    )

    calculate_costs_btn.click(
        fn=get_selected_cost_links,
        inputs=[accent_color, wood_finish, wall_color, tiles],
        outputs=costs_output
    )

app.launch(debug=True, share=True)
display(HTML("<style>#calculate-costs-btn {background-color: #007bff; color: white; border: none; padding: 10px 20px; cursor: pointer;} #calculate-costs-btn:hover {background-color: #0056b3;}</style>"))

gradio deploy

