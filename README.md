# HankComments

Hank Green had a video, where he asked his viewers to recommend books, movies, TV shows, and video games, that they thought were calming.
I iterated through all the comments, stored them in a txt file, then used GPT 3.5 Turbo to parse the comments into a list of recommendations, grouped by category.
I then used GPT 4 Code Interpreter to analyze the recommendations, and create visualizations for each category.

## Animated Visualization
Here's an animated overview of the top recommendations across all categories:

![Recommendation Animation](hank_green_recommendations.gif)

## Detailed Static Graphs
For a more detailed look at each category, check out the static visualizations below:

<details>
<summary>📚 Books (Click to expand)</summary>
<br>
<img src="https://github.com/pauljones0/HankComments/assets/32859666/dcf9c727-451a-4522-bbb6-cec0c2574d6f" alt="Books Top 40 Suggestions" width="800">
</details>

<details>
<summary>🎬 Movies (Click to expand)</summary>
<br>
<img src="https://github.com/pauljones0/HankComments/assets/32859666/d85ccfb7-53a8-441f-9337-ad069d9ee353" alt="Movies Top 40 Suggestions" width="800">
</details>

<details>
<summary>📺 TV Shows (Click to expand)</summary>
<br>
<img src="https://github.com/pauljones0/HankComments/assets/32859666/0ef5bd79-64f5-4625-8b48-09c5122c9fcb" alt="TV Shows Top 40 Suggestions" width="800">
</details>

<details>
<summary>🎮 Video Games (Click to expand)</summary>
<br>
<img src="https://github.com/pauljones0/HankComments/assets/32859666/d360b3dd-8be0-42cc-9b2a-4d9840f1fad0" alt="Video Games Top 40 Suggestions" width="800">
</details>

## How It Works

1. **Collection**: YouTube comments were collected from Hank Green's video asking for calming media recommendations.
2. **Processing**: Comments were processed using GPT-3.5 Turbo to extract and categorize recommendations.
3. **Analysis**: Data was cleaned and analyzed to identify the most frequently mentioned items in each category.
4. **Visualization**: Visualizations were created to showcase the findings.

## Installation

1. **Clone this repository**:
   ```bash
   git clone https://github.com/yourusername/HankComments.git
   cd HankComments
   ```

2. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file with your API keys** (see `.env.example` for format):
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your API keys.

## Usage

Run the complete pipeline with a single command: