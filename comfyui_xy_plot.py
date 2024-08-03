import gradio as gr
import json
import websocket
import uuid
import urllib.request
import urllib.parse
import os
from PIL import Image, ImageDraw, ImageFont
import io
import threading
import os
from datetime import datetime

class ComfyUIXYPlot:
    def __init__(self):
        self.output_dir = "xy_plot_outputs"
        os.makedirs(self.output_dir, exist_ok=True)
        self.server_address = '127.0.0.1:8188'
        self.client_id = str(uuid.uuid4())
        self.ws = None
        self.cancel_flag = False

        # Initialize WebSocket connection
        self.ws = websocket.WebSocket()
        self.ws.connect(f"ws://{self.server_address}/ws?clientId={self.client_id}")

        self.samplers = [
            "euler", "euler_ancestral", "heun", "dpm_2", "dpm_2_ancestral",
            "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral", "dpmpp_sde",
            "dpmpp_2m", "dpmpp_3m_sde", "ddpm", "lcm", "ddim", "uni_pc"
        ]
        self.schedulers = [
            "normal", "karras", "exponential", "sgm_uniform", "simple",
            "ddim_uniform", "beta"
        ]

        # Default values for new parameters
        self.default_cell_size = 512
        self.default_margin_size = 200
        self.default_font_size = 24
        self.default_show_image_labels = True
        self.default_show_axis_labels = True
        self.default_swap_xy_axis = True

        self.load_workflow_defaults()
        self.create_interface()

    def load_workflow_defaults(self):
        with open("flux_workflow_api.json", "r") as file:
            workflow = json.load(file)
        
        self.default_width = workflow['5']['inputs']['width']
        self.default_height = workflow['5']['inputs']['height']
        self.default_steps = workflow['17']['inputs']['steps']
        self.default_sampler = workflow['16']['inputs']['sampler_name']
        self.default_scheduler = workflow['17']['inputs']['scheduler']

    def create_interface(self):
        with gr.Blocks() as self.interface:
            gr.Markdown("# ComfyUI XY Plot Generator")
            
            with gr.Row():
                prompt = gr.Textbox(label="Prompt")
                seed = gr.Number(label="Seed", precision=0)

            with gr.Row():
                width = gr.Slider(minimum=64, maximum=2048, step=64, label="Width", value=self.default_width)
                height = gr.Slider(minimum=64, maximum=2048, step=64, label="Height", value=self.default_height)
                steps = gr.Slider(minimum=1, maximum=150, step=1, label="Steps", value=self.default_steps)

            with gr.Row():
                samplers = gr.CheckboxGroup(choices=self.samplers, label="Samplers", value=[self.default_sampler])
                schedulers = gr.CheckboxGroup(choices=self.schedulers, label="Schedulers", value=[self.default_scheduler])

            with gr.Row():
                gr.Markdown("### Label and Margin Settings")
            
            with gr.Row():
                cell_size = gr.Slider(minimum=128, maximum=1024, step=32, label="Cell Size", value=self.default_cell_size)
                font_size = gr.Slider(minimum=8, maximum=32, step=1, label="Font Size", value=self.default_font_size)
                margin_size = gr.Slider(minimum=50, maximum=400, step=10, label="Margin Size", value=self.default_margin_size)

            with gr.Row():
                show_image_labels = gr.Checkbox(label="Show Image Labels", value=self.default_show_image_labels)
                show_axis_labels = gr.Checkbox(label="Show Axis Labels", value=self.default_show_axis_labels)
                swap_xy_axis = gr.Checkbox(label="Swap X/Y Axis", value=self.default_swap_xy_axis)

            generate_button = gr.Button("Generate XY Plot")
            cancel_button = gr.Button("Cancel")

            status = gr.Textbox(label="Status")

            generate_button.click(
                self.generate_xy_plot,
                inputs=[prompt, seed, width, height, steps, samplers, schedulers, 
                        cell_size, font_size, margin_size, show_image_labels, show_axis_labels, swap_xy_axis],
                outputs=[status]
            )
            cancel_button.click(self.cancel_generation, outputs=[status])

    def create_xy_plot(self, images, samplers, schedulers, cell_size, font_size, margin_size, show_image_labels, show_axis_labels, swap_xy_axis):
        if swap_xy_axis:
            samplers, schedulers = schedulers, samplers
        
        rows = len(samplers)
        cols = len(schedulers)
        
        # Calculate the aspect ratio of the first image
        first_image = images[0][0]
        aspect_ratio = first_image.width / first_image.height
        
        cell_height = int(cell_size / aspect_ratio)
        
        # Calculate margins and total dimensions
        left_margin = margin_size if show_image_labels or show_axis_labels else 0
        top_margin = margin_size if show_image_labels or show_axis_labels else 0
        
        total_width = cols * cell_size + left_margin
        total_height = rows * cell_height + top_margin
        
        grid_image = Image.new('RGB', (total_width, total_height), color='white')
        draw = ImageDraw.Draw(grid_image)
        
        try:
            font = ImageFont.truetype("static/Roboto-Regular.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        for i, row_label in enumerate(samplers):
            for j, col_label in enumerate(schedulers):
                for img, label in images:
                    img_label = f"{row_label}-{col_label}" if not swap_xy_axis else f"{col_label}-{row_label}"
                    if label == img_label:
                        img_resized = img.resize((cell_size, cell_height), Image.LANCZOS)
                        paste_x = j * cell_size + left_margin
                        paste_y = i * cell_height + top_margin
                        grid_image.paste(img_resized, (paste_x, paste_y))
                
                # Draw image labels if enabled
                if show_image_labels:
                    # Draw column labels (top)
                    if i == 0:
                        label_x = j * cell_size + left_margin + cell_size // 2
                        label_y = top_margin // 2
                        draw.text((label_x, label_y), col_label, fill="black", font=font, anchor="mm")
                    
                    # Draw row labels (left)
                    if j == 0:
                        label_x = left_margin // 2
                        label_y = i * cell_height + top_margin + cell_height // 2
                        draw.text((label_x, label_y), row_label, fill="black", font=font, anchor="mm", rotation=90)

        # Draw axis labels if enabled
        if show_axis_labels:
            x_axis_label = "Schedulers" if not swap_xy_axis else "Samplers"
            y_axis_label = "Samplers" if not swap_xy_axis else "Schedulers"
            draw.text((total_width // 2, top_margin // 4), x_axis_label, fill="black", font=font, anchor="mm")
            draw.text((left_margin // 4, total_height // 2), y_axis_label, fill="black", font=font, anchor="mm", rotation=90)

        return grid_image, self.save_xy_plot(grid_image)

    def save_xy_plot(self, grid_image):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"xy_plot_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        grid_image.save(filepath)
        return filepath

    def generate_xy_plot(self, prompt, seed, width, height, steps, samplers, schedulers, 
                         cell_size, font_size, margin_size, show_image_labels, show_axis_labels, swap_xy_axis):
        self.cancel_flag = False
        
        if not all([prompt, seed, width, height, steps, samplers, schedulers]):
            return None, "Please fill all fields and select at least one sampler and scheduler."

        try:
            seed = int(seed)
            width = int(width)
            height = int(height)
            steps = int(steps)
        except ValueError:
            return None, "Seed, width, height, and steps must be integers."

        with open("flux_workflow_api.json", "r") as file:
            workflow = json.load(file)

        total_images = len(samplers) * len(schedulers)
        images = []

        for i, sampler in enumerate(samplers):
            for j, scheduler in enumerate(schedulers):
                if self.cancel_flag:
                    return None, "Generation cancelled."
                modified_workflow = self.modify_workflow(workflow, prompt, seed, width, height, steps, sampler, scheduler)
                image_data = self.generate_image(modified_workflow)
                if image_data:
                    image = Image.open(io.BytesIO(image_data))
                    images.append((image, f"{sampler}-{scheduler}"))
                    yield None, f"Generated {len(images)}/{total_images} images"

        if images and not self.cancel_flag:
            _, filepath = self.create_xy_plot(images, samplers, schedulers, cell_size, font_size, 
                                              margin_size, show_image_labels, show_axis_labels, swap_xy_axis)
            return None, f"XY Plot generated successfully and saved to {filepath}"
        elif not images:
            return None, "Failed to generate any images."

    def cancel_generation(self):
        self.cancel_flag = True
        return "Cancelling..."

    def modify_workflow(self, workflow, prompt, seed, width, height, steps, sampler, scheduler):
        workflow['28']['inputs']['string'] = prompt
        workflow['25']['inputs']['noise_seed'] = seed
        workflow['5']['inputs']['width'] = width
        workflow['5']['inputs']['height'] = height
        workflow['17']['inputs']['steps'] = steps
        workflow['16']['inputs']['sampler_name'] = sampler
        workflow['17']['inputs']['scheduler'] = scheduler
        return workflow

    def generate_image(self, workflow):
        prompt_id = self.queue_prompt(workflow)
        if prompt_id:
            return self.track_progress(prompt_id)
        return None

    def queue_prompt(self, prompt):
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data, headers={'Content-Type': 'application/json'})
        response = urllib.request.urlopen(req)
        return json.loads(response.read())['prompt_id']

    def track_progress(self, prompt_id):
        while True:
            out = self.ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    if message['data']['node'] is None and message['data']['prompt_id'] == prompt_id:
                        break
            else:
                continue
        return self.get_image(prompt_id)

    def get_image(self, prompt_id):
        history = self.get_history(prompt_id)
        if history:
            for node_id in history['outputs']:
                node_output = history['outputs'][node_id]
                if 'images' in node_output:
                    image = node_output['images'][0]
                    return self.get_image_data(image['filename'], image['subfolder'], image['type'])
        return None

    def get_history(self, prompt_id):
        with urllib.request.urlopen(f"http://{self.server_address}/history/{prompt_id}") as response:
            return json.loads(response.read())[prompt_id]

    def get_image_data(self, filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen(f"http://{self.server_address}/view?{url_values}") as response:
            return response.read()

    def launch(self):
        self.interface.launch()

if __name__ == "__main__":
    app = ComfyUIXYPlot()
    app.launch()
