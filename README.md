# ComfyUI XY Plot Generator

## Overview

The ComfyUI XY Plot Generator is a powerful tool designed to create comparative visualizations of images generated using different samplers and schedulers in Stable Diffusion. This tool integrates with ComfyUI, a node-based interface for Stable Diffusion, allowing users to explore and analyze the effects of various parameters on image generation.

## Key Features

1. **Dynamic XY Plot Generation**: Create grids of images comparing different samplers and schedulers.
2. **Customizable UI**: Gradio-based interface for easy parameter adjustment.
3. **Real-time Progress Updates**: WebSocket integration for live generation progress.
4. **Flexible Image Labeling**: Options to show/hide image and axis labels.
5. **Adjustable Layout**: Controls for cell size, font size, and margin size.

## Recent Improvements

- **Enhanced UI Controls**: 
  - Added checkboxes for toggling image and axis labels.
  - Implemented sliders for adjusting margin and font sizes.
- **Improved Labeling System**: 
  - Inner labels for individual images.
  - Outer labels for samplers and schedulers.
- **Font Integration**: Now using Roboto-Regular font for consistent typography.
- **Optimized Layout**: Better handling of margins and label placement.

## Technical Details

### ComfyUI Integration
- Utilizes ComfyUI's API for workflow modification and image generation.
- WebSocket connection for real-time progress tracking.

### Image Processing
- PIL (Python Imaging Library) for image manipulation and grid creation.
- Dynamic resizing and positioning of images within the grid.

### User Interface
- Gradio-based interface for intuitive parameter control and real-time updates.

## Setup and Execution

1. **Dependencies**:
   ```
   pip install gradio pillow websocket-client
   ```

2. **ComfyUI Setup**:
   - Ensure ComfyUI is running on `http://127.0.0.1:8188`
   - Place `flux_workflow_api.json` in the script directory

3. **Execution**:
   ```
   python comfyui_xy_plot.py
   ```

4. Access the Gradio interface via the provided local URL.

## Future Development

- Implement image caching for improved performance.
- Explore parallel processing for faster grid generation.
- Enhance error handling and user feedback mechanisms.
- Develop a comprehensive testing suite.
- Expand documentation with detailed API references and usage examples.

## Conclusion

The ComfyUI XY Plot Generator offers a robust solution for visualizing and comparing Stable Diffusion outputs. Its recent improvements in UI flexibility and image handling make it an even more valuable tool for researchers and enthusiasts in the field of AI-generated imagery.
