import argparse
import os
from youtube_comments import extract_comments
from comment_analyzer import CommentAnalyzer
from visualization import create_visualizations
import config

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='YouTube Comment Analysis Pipeline')
    
    parser.add_argument('--video-id', type=str, default=config.VIDEO_ID,
                        help='YouTube video ID to analyze')
    
    parser.add_argument('--force-refresh', action='store_true',
                        help='Force refresh of all steps, ignoring cached data')
    
    parser.add_argument('--skip-comments', action='store_true',
                        help='Skip comment extraction (use cached comments)')
    
    parser.add_argument('--skip-analysis', action='store_true',
                        help='Skip comment analysis (use cached analysis)')
    
    parser.add_argument('--skip-visualization', action='store_true',
                        help='Skip visualization generation')
    
    parser.add_argument('--no-gif', action='store_true',
                        help='Skip animated GIF generation')
    
    parser.add_argument('--no-static', action='store_true',
                        help='Skip static graph generation')
    
    return parser.parse_args()

def run_pipeline(args):
    """Run the complete analysis pipeline."""
    print("Starting YouTube comment analysis pipeline...")
    
    # Step 1: Extract comments
    if not args.skip_comments:
        print("\n=== Step 1: Extracting YouTube comments ===")
        comments = extract_comments(args.video_id, args.force_refresh)
    else:
        print("\n=== Step 1: Loading cached comments ===")
        comments = extract_comments(args.video_id, False)
    
    if not comments:
        print("Error: No comments available. Exiting pipeline.")
        return False
    
    # Step 2: Analyze comments
    if not args.skip_analysis:
        print("\n=== Step 2: Analyzing comments ===")
        analyzer = CommentAnalyzer()
        analysis = analyzer.analyze_comments(comments, args.force_refresh)
    else:
        print("\n=== Step 2: Loading cached analysis ===")
        analyzer = CommentAnalyzer()
        analysis = analyzer.analyze_comments(None, False)
    
    if not analysis:
        print("Error: No analysis available. Exiting pipeline.")
        return False
    
    # Step 3: Create visualizations
    if not args.skip_visualization:
        print("\n=== Step 3: Creating visualizations ===")
        create_gif = not args.no_gif
        create_static = not args.no_static
        
        visualization_results = create_visualizations(
            analysis, 
            create_gif=create_gif, 
            create_static=create_static
        )
        
        # Print summary of created visualizations
        if create_gif and 'animated_gif' in visualization_results:
            print(f"Created animated GIF: {visualization_results['animated_gif']}")
            
        if create_static and 'static_graphs' in visualization_results:
            print("Created static graphs:")
            for category, path in visualization_results['static_graphs'].items():
                print(f"  - {category}: {path}")
    else:
        print("\n=== Step 3: Skipping visualization generation ===")
    
    print("\nPipeline completed successfully!")
    return True

if __name__ == "__main__":
    args = parse_arguments()
    run_pipeline(args)
