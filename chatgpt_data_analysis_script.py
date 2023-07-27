
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def load_data(file_path):
    with open(file_path) as f:
        data = json.load(f)
    df = pd.DataFrame(data.items(), columns=['suggestion', 'count'])
    return df

def clean_data(df, items_to_remove):
    clean_data = {}
    for index, row in df.iterrows():
        category = row['suggestion']
        suggestions = pd.DataFrame(row['count'].items(), columns=['item', 'count'])
        clean_suggestions = suggestions[suggestions['count'].apply(lambda x: isinstance(x, int))]
        clean_suggestions = clean_suggestions[~clean_suggestions['item'].isin(items_to_remove)]
        clean_data[category] = clean_suggestions
    return clean_data

def calculate_percentage(clean_data):
    for category, suggestions in clean_data.items():
        suggestions['percentage'] = (suggestions['count'] / suggestions['count'].sum()) * 100
    return clean_data

def generate_graphs(clean_data, categories, color_palette):
    for category in categories:
        top_suggestions = clean_data[category].sort_values(by="percentage", ascending=False).head(40)
        plt.figure(figsize=(10, 15))
        sns.barplot(x="percentage", y="item", data=top_suggestions, palette=color_palette, edgecolor=".2")
        plt.title(f"Top 40 {category} Suggestions by Percentage", fontsize=16)
        plt.xlabel("Percentage (%)", fontsize=12)
        plt.ylabel("")
        plt.savefig(f"{category.replace(' ', '_')}_Top_40_Suggestions.png", bbox_inches='tight')
    plt.close('all')

def main():
    # Load data
    df = load_data('combined_Hank_Green.json')
    
    # Define items to remove
    items_to_remove = ['The Fault in Our Stars', 'Crash Course', 'SciShow', 'Sci Show', 'Dear Hank and John', 'Vlogbrothers', 'Hank Green', 'The Fault In Our Stars by John Green']
    
    # Clean data
    clean_data = clean_data(df, items_to_remove)
    
    # Calculate percentage
    clean_data = calculate_percentage(clean_data)
    
    # Define categories and color palette
    categories = ['Video Games', 'TV Shows', 'Movies', 'Books']
    color_palette = sns.color_palette("viridis", 40)
    
    # Generate graphs
    generate_graphs(clean_data, categories, color_palette)

if __name__ == "__main__":
    main()
