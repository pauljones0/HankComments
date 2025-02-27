import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from matplotlib.ticker import MaxNLocator
import config

def prepare_data_for_visualization(analysis_data):
    """Convert analysis data to a format suitable for visualization."""
    # Convert the nested dictionary to a DataFrame
    df = pd.DataFrame(analysis_data.items(), columns=['category', 'count'])
    
    # Clean data by removing specified items
    clean_data_dict = {}
    for index, row in df.iterrows():
        category = row['category']
        suggestions = pd.DataFrame(row['count'].items(), columns=['item', 'count'])
        
        # Filter out non-integer counts
        clean_suggestions = suggestions[suggestions['count'].apply(lambda x: isinstance(x, int))]
        
        # Remove specified items
        if config.ITEMS_TO_REMOVE:
            clean_suggestions = clean_suggestions[~clean_suggestions['item'].isin(config.ITEMS_TO_REMOVE)]
        
        # Calculate percentage
        total = clean_suggestions['count'].sum()
        if total > 0:  # Avoid division by zero
            clean_suggestions['percentage'] = (clean_suggestions['count'] / total) * 100
            
        clean_data_dict[category] = clean_suggestions
    
    return clean_data_dict

def generate_graph(category, data, color_palette, output_dir=None, top_n=40):
    """Generate and save a bar graph for a specific category."""
    # Sort by percentage and get top N items
    top_suggestions = data.sort_values(by="percentage", ascending=False).head(top_n)
    
    # Create figure with appropriate size
    plt.figure(figsize=(10, 15))
    
    # Create bar plot
    ax = sns.barplot(
        x="percentage", 
        y="item", 
        data=top_suggestions, 
        palette=color_palette, 
        edgecolor=".2"
    )
    
    # Add percentage labels to the bars
    for i, p in enumerate(ax.patches):
        width = p.get_width()
        ax.text(
            width + 0.5,  # Slightly offset from the end of the bar
            p.get_y() + p.get_height()/2,
            f'{width:.1f}%',
            va='center'
        )
    
    # Set title and labels
    plt.title(f"Top {top_n} {category} Suggestions by Percentage", fontsize=16)
    plt.xlabel("Percentage (%)", fontsize=12)
    plt.ylabel("")
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{category.replace(' ', '_')}_Top_{top_n}_Suggestions.png")
    else:
        output_path = f"{category.replace(' ', '_')}_Top_{top_n}_Suggestions.png"
    
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    return output_path

def create_animated_visualization(clean_data_dict, categories=None, top_n=15, output_file=None):
    """Create an animated GIF that transitions between top recommendations for each category."""
    if output_file is None:
        output_file = os.path.join(config.OUTPUT_DIR, config.GIF_OUTPUT)
        
    if not categories:
        categories = list(clean_data_dict.keys())
    
    # Set up the figure
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.suptitle("Top Recommendations from Hank Green's Viewers", fontsize=16)
    
    # Create custom colormap
    colors = ["#4287f5", "#42c5f5", "#42f5d1", "#42f584", "#8af542", "#f5d742", "#f59c42", "#f55442"]
    custom_cmap = LinearSegmentedColormap.from_list("custom_cmap", colors, N=top_n)
    
    # Find the maximum percentage across all categories for consistent scaling
    max_percentage = 0
    for category in categories:
        if category in clean_data_dict:
            top_suggestions = clean_data_dict[category].sort_values(by="percentage", ascending=False).head(top_n)
            if not top_suggestions.empty:
                max_percentage = max(max_percentage, top_suggestions['percentage'].max())
    
    # Add a bit of padding to the max percentage
    max_percentage = max_percentage * 1.1
    
    def update(frame):
        ax.clear()
        
        # Determine which category to show based on the frame
        category_idx = frame // 15  # Show each category for 15 frames
        if category_idx >= len(categories):
            category_idx = len(categories) - 1
        
        category = categories[category_idx]
        
        if category in clean_data_dict:
            # Get top suggestions for this category
            top_suggestions = clean_data_dict[category].sort_values(by="percentage", ascending=False).head(top_n)
            
            # Create horizontal bar chart
            bars = ax.barh(
                y=top_suggestions['item'], 
                width=top_suggestions['percentage'],
                color=[custom_cmap(i/top_n) for i in range(len(top_suggestions))],
                edgecolor='black',
                linewidth=0.5,
                alpha=0.8
            )
            
            # Add percentage labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(
                    width + max_percentage * 0.02,  # Slightly offset from the end of the bar
                    bar.get_y() + bar.get_height()/2,
                    f'{width:.1f}%',
                    va='center',
                    fontweight='bold'
                )
            
            # Add category title with frame-dependent animation
            fade_in = min(1.0, (frame % 15) / 5)  # Fade in over first 5 frames of each category
            ax.text(
                0.5, 0.95, 
                f"Top {top_n} {category}", 
                transform=ax.transAxes,
                ha='center',
                fontsize=14,
                fontweight='bold',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray', boxstyle='round,pad=0.5'),
                alpha=fade_in
            )
            
            # Set axis limits and labels
            ax.set_xlabel("Percentage (%)", fontsize=12)
            ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
            
            # Remove y-axis label
            ax.set_ylabel("")
            
            # Add grid lines
            ax.grid(axis='x', linestyle='--', alpha=0.7)
            
            # Add a subtle background color
            ax.set_facecolor('#f8f8f8')
            
        return [ax]
    
    # Calculate total frames (15 frames per category)
    total_frames = len(categories) * 15
    
    # Create animation
    ani = animation.FuncAnimation(
        fig, 
        update, 
        frames=total_frames,
        blit=True,
        interval=200  # 200ms between frames
    )
    
    # Save as GIF
    print(f"Creating animation with {total_frames} frames...")
    ani.save(
        output_file, 
        writer='pillow', 
        fps=5,
        dpi=100
    )
    plt.close(fig)
    
    print(f"Animation saved to {output_file}")
    return output_file

def generate_all_graphs(clean_data_dict, categories=None, top_n=40):
    """Generate graphs for all specified categories."""
    if not categories:
        categories = list(clean_data_dict.keys())
    
    # Define color palette
    color_palette = sns.color_palette("viridis", top_n)
    
    generated_paths = {}
    for category in categories:
        if category in clean_data_dict:
            path = generate_graph(
                category, 
                clean_data_dict[category], 
                color_palette, 
                config.OUTPUT_DIR, 
                top_n
            )
            generated_paths[category] = path
        else:
            print(f"Warning: Category '{category}' not found in data")
    
    return generated_paths

def create_visualizations(analysis_data, create_gif=True, create_static=True):
    """Create visualizations from analysis data."""
    # Prepare data for visualization
    clean_data_dict = prepare_data_for_visualization(analysis_data)
    
    results = {}
    
    # Generate static graphs if requested
    if create_static:
        static_paths = generate_all_graphs(
            clean_data_dict, 
            config.CATEGORIES, 
            top_n=40
        )
        results['static_graphs'] = static_paths
        
    # Create animated visualization if requested
    if create_gif:
        gif_path = create_animated_visualization(
            clean_data_dict,
            config.CATEGORIES,
            top_n=15
        )
        results['animated_gif'] = gif_path
    
    return results 