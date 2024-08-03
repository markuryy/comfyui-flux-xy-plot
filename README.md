# ComfyUI XY Plot Generator

## Detailed Technical Overview

### ComfyUI Basics

ComfyUI is a node-based interface for Stable Diffusion, allowing for complex image generation workflows. Key concepts:

1. Nodes: Represent operations (e.g., loading models, sampling, encoding prompts).
2. Workflows: Connections of nodes defining the generation process.
3. API Format: JSON representation of workflows for programmatic interaction.

### WebSocket Usage

WebSockets are crucial for real-time communication with ComfyUI:

1. Purpose: To receive live updates on generation progress and execution status.
2. Connection: Established using `websocket-client` library.
3. Messages: JSON-formatted, including types like 'executing', 'progress', and 'executed'.

### HTTP Interaction

RESTful endpoints are used for non-real-time operations:

1. `/prompt`: POST request to queue a workflow for execution.
2. `/history/{prompt_id}`: GET request to retrieve execution results.
3. `/view`: GET request to fetch generated images.

### Workflow Modification

The script dynamically modifies the ComfyUI workflow:

1. Loading: Workflow loaded from `flux_workflow_api.json`.
2. Modification: Update node inputs based on user parameters (e.g., prompt, seed, sampler).
3. Execution: Modified workflow sent to ComfyUI for processing.

### Image Generation Process

1. Queue Prompt: Send modified workflow to ComfyUI.
2. Track Progress: Listen to WebSocket for execution updates.
3. Retrieve Image: Fetch generated image data using history and view endpoints.
4. Process Image: Load image data into PIL Image object for manipulation.

### XY Plot Creation

1. Grid Calculation: Determine dimensions based on selected samplers and schedulers.
2. Image Placement: Resize and paste generated images into grid.
3. Labeling: Add sampler and scheduler labels using PIL's ImageDraw.
4. Scaling: Maintain aspect ratio and quality during resizing.

### Gradio Interface

Gradio is used for the web-based UI:

1. Components: Textboxes, sliders, checkbox groups for user input.
2. Event Handling: Generate button triggers the main workflow.
3. Output Updates: Uses Gradio's yielding mechanism for live updates.

## Current Implementation Details

### Class Structure: `ComfyUIXYPlot`

#### Initialization
- Sets up ComfyUI server connection details
- Initializes WebSocket client
- Defines available samplers and schedulers
- Loads workflow defaults

#### Key Methods

1. `load_workflow_defaults()`:
   - Parses `flux_workflow_api.json`
   - Extracts default values for width, height, steps, sampler, and scheduler

2. `create_interface()`:
   - Builds Gradio UI components
   - Sets up event handlers for generate and cancel buttons

3. `generate_xy_plot()`:
   - Main execution flow
   - Validates inputs
   - Iterates through sampler/scheduler combinations
   - Yields intermediate results for live updates

4. `modify_workflow(workflow, prompt, seed, width, height, steps, sampler, scheduler)`:
   - Updates specific nodes in the workflow JSON
   - Node IDs: 28 (prompt), 25 (seed), 5 (dimensions), 17 (steps, scheduler), 16 (sampler)

5. `generate_image(workflow)`:
   - Queues prompt with ComfyUI
   - Establishes WebSocket connection
   - Tracks execution progress
   - Retrieves final image data

6. `create_xy_plot(images, samplers, schedulers)`:
   - Creates grid image using PIL
   - Maintains aspect ratio of original images
   - Adds labels and titles
   - Saves final plot as PNG

#### WebSocket Handling

- `track_progress(prompt_id)`:
  - Listens for WebSocket messages
  - Handles 'executing' and 'progress' message types
  - Determines when execution is complete

#### HTTP Requests

- `queue_prompt(prompt)`: POST to `/prompt`
- `get_history(prompt_id)`: GET from `/history/{prompt_id}`
- `get_image_data(filename, subfolder, folder_type)`: GET from `/view`

### Current Limitations and Issues

1. Image Preview Sizing: Preview in Gradio UI is too large, affecting usability.
2. Final Plot Display: XY plot not shown in Gradio interface after generation.
3. Margin and Label Toggling: No UI options to toggle outermost margins and labels.
4. Aspect Ratio Consistency: Improvements needed in maintaining consistent aspect ratios.
5. Error Handling: Limited error handling and user feedback mechanisms.
6. Performance: Potential bottlenecks in generating large grids.

### Technical Debt and Optimization Opportunities

1. Caching: Implement caching to avoid regenerating unchanged images.
2. Parallel Processing: Explore options for parallel image generation.
3. Memory Management: Optimize memory usage, especially for large grids.
4. Modularization: Separate ComfyUI interaction, image processing, and UI components.

## Development Roadmap

1. UI Enhancements:
   - Implement resizable image preview
   - Add toggle controls for margins and labels
   - Develop progress bar for overall generation process

2. Image Handling Improvements:
   - Refine aspect ratio maintenance algorithm
   - Implement adaptive cell sizing based on image dimensions

3. Performance Optimizations:
   - Implement image caching system
   - Explore asynchronous processing for improved responsiveness

4. Error Handling and Logging:
   - Develop comprehensive error catching and reporting system
   - Implement detailed logging for debugging and analysis

5. Testing Suite:
   - Develop unit tests for core functions (e.g., workflow modification, image processing)
   - Create integration tests for ComfyUI interaction
   - Implement UI testing using Gradio's testing utilities

6. Documentation:
   - Generate detailed API documentation for each class and method
   - Create user guide with examples of different XY plot configurations

7. Advanced Features:
   - Support for custom node configurations in workflows
   - Implement save/load functionality for XY plot configurations
   - Develop batch processing capabilities for multiple prompts

## Setup and Execution

1. Dependencies:
   ```
   pip install gradio pillow websocket-client
   ```

2. ComfyUI Setup:
   - Ensure ComfyUI is running on `http://127.0.0.1:8188`
   - Place `flux_workflow_api.json` in the script directory

3. Execution:
   ```
   python comfyui_xy_plot.py
   ```

4. Access Gradio interface via the provided local URL

## Conclusion

This XY Plot Generator for ComfyUI provides a powerful tool for comparing different sampling and scheduling methods in image generation. By leveraging WebSockets for real-time updates and dynamically modifying ComfyUI workflows, it offers a flexible and interactive way to visualize the effects of various parameters on the generated images.

The current implementation serves as a solid foundation, but there are several areas for improvement and optimization. Future development should focus on enhancing the user interface, improving image handling and quality, optimizing performance for large-scale comparisons, and expanding the tool's capabilities to support more complex ComfyUI workflows and configurations.